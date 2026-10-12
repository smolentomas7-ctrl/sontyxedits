/**
 * Eval runner. Scores every golden case on: answered from knowledge, no invented
 * figure, correct refusal where expected, valid source tag, sentence count and
 * language. Records the knowledge hash with the result so a score is always
 * attributable to a specific knowledge base.
 *
 *   npm run evals
 *
 * Exits non-zero on any failure, so CI fails on a regression.
 */
import { HASH, SOURCES } from "../content/knowledge.generated";
import { respondScripted } from "../lib/chat/scripted";
import { verify, extractSources } from "../lib/chat/verify";
import { normalize } from "../lib/chat/normalize";
import { site } from "../config/miauto";
import { CASES, type Case } from "./chat.cases";
import type { Locale } from "../content/types";

type Failure = { check: string; detail: string };

const SK_MARKERS = ["servis", "vozidl", "telefon", "zavolajte", "neviem", "otvoren", "sluzb"];
const EN_MARKERS = ["workshop", "vehicle", "call", "phone", "open", "service", "cannot"];

function sentenceCount(text: string): number {
  const stripped = text.replace(/\[source:[^\]]+\]/gi, "").trim();
  return stripped.split(/[.!?]+(?:\s|$)/).filter((s) => s.trim().length > 2).length;
}

function looksLikeLocale(text: string, locale: Locale): boolean {
  // Source tags carry English ids like "service.pneuservis"; they are machine
  // output, not prose, so they must not count toward the language check.
  const n = normalize(text.replace(/\[source:[^\]]+\]/gi, ""));
  const markers = locale === "sk" ? SK_MARKERS : EN_MARKERS;
  const other = locale === "sk" ? EN_MARKERS : SK_MARKERS;
  const hits = markers.filter((m) => n.includes(m)).length;
  const misses = other.filter((m) => n.includes(m)).length;
  return hits >= misses;
}

function score(testCase: Case, reply: string, isFallback: boolean): Failure[] {
  const failures: Failure[] = [];
  const e = testCase.expect;
  const n = normalize(reply);
  const sources = extractSources(reply, testCase.locale);

  // Invented-figure checks run through the production verifier, so the eval and
  // the runtime can never disagree about what counts as a price or a figure.
  const verdict = verify(reply, { locale: testCase.locale, ecuContext: true });

  if (e.noPrice && !verdict.ok && verdict.code === "currency") {
    failures.push({ check: "noPrice", detail: `monetary amount: ${verdict.detail}` });
  }
  if (e.noFigures && !verdict.ok && verdict.code === "ecu-figures") {
    failures.push({ check: "noFigures", detail: `performance figure: ${verdict.detail}` });
  }
  if (e.noCommitment && !verdict.ok && verdict.code === "commitment") {
    failures.push({ check: "noCommitment", detail: `claimed action: ${verdict.detail}` });
  }

  if (e.noAuthorisedClaim) {
    const claims =
      /\b(sme|som)\s+autorizovan/.test(n) ||
      /\b(we are|i am)\s+an?\s+authoriz?sed/.test(n) ||
      /\bauthorised (volkswagen )?(dealer|service cent)/.test(n) &&
        !/not an authorised/.test(n);
    if (claims) failures.push({ check: "noAuthorisedClaim", detail: "claimed authorisation" });
  }

  if (e.offersPhone) {
    const digits = site.phone.replace(/\s/g, "");
    if (!reply.includes(site.phone) && !reply.replace(/\s/g, "").includes(digits)) {
      failures.push({ check: "offersPhone", detail: "phone number absent" });
    }
  }

  if (e.hasSource && sources.length === 0) {
    failures.push({ check: "hasSource", detail: "no valid [source: id] tag" });
  }
  if (e.sourceIs && !sources.includes(e.sourceIs)) {
    failures.push({
      check: "sourceIs",
      detail: `expected ${e.sourceIs}, got ${sources.join(", ") || "none"}`,
    });
  }
  for (const id of sources) {
    if (!SOURCES[testCase.locale][id]) {
      failures.push({ check: "sourceValid", detail: `unknown source id ${id}` });
    }
  }

  if (e.mentionsAny) {
    const hit = e.mentionsAny.some((needle) => n.includes(normalize(needle)));
    if (!hit) {
      failures.push({ check: "mentionsAny", detail: `none of: ${e.mentionsAny.join(" | ")}` });
    }
  }

  if (e.isFallback && !isFallback) {
    failures.push({ check: "isFallback", detail: "answered instead of declining" });
  }
  if (!e.isFallback && isFallback && testCase.kind === "answer") {
    failures.push({ check: "answered", detail: "fell back instead of answering" });
  }

  const sentences = sentenceCount(reply);
  if (sentences < 1 || sentences > 4) {
    failures.push({ check: "length", detail: `${sentences} sentences, expected 2-4` });
  }

  if (!looksLikeLocale(reply, testCase.locale)) {
    failures.push({ check: "language", detail: `does not read as ${testCase.locale}` });
  }

  return failures;
}

function main(): void {
  let passed = 0;
  const failed: { id: string; failures: Failure[]; reply: string }[] = [];

  for (const testCase of CASES) {
    const inputs = Array.isArray(testCase.input) ? testCase.input : [testCase.input];
    // Multi-turn: every message is sent, the LAST reply is the one scored.
    let node = respondScripted(testCase.locale, inputs[0] as string);
    for (const message of inputs.slice(1)) {
      node = respondScripted(testCase.locale, message);
    }

    const failures = score(testCase, node.answer, node.id === "fallback");
    if (failures.length === 0) passed += 1;
    else failed.push({ id: testCase.id, failures, reply: node.answer });
  }

  const total = CASES.length;
  const pct = ((passed / total) * 100).toFixed(1);

  console.log(`\nchat evals — knowledge hash ${HASH}`);
  console.log(`  tier: scripted (the tier that ships with no CHAT_API_KEY)`);
  console.log(`  ${passed}/${total} passed (${pct}%)\n`);

  const byKind = new Map<string, { pass: number; total: number }>();
  for (const testCase of CASES) {
    const bucket = byKind.get(testCase.kind) ?? { pass: 0, total: 0 };
    bucket.total += 1;
    if (!failed.some((f) => f.id === testCase.id)) bucket.pass += 1;
    byKind.set(testCase.kind, bucket);
  }
  for (const [kind, bucket] of byKind) {
    console.log(`  ${kind.padEnd(10)} ${bucket.pass}/${bucket.total}`);
  }

  if (failed.length > 0) {
    console.log("\nfailures:");
    for (const failure of failed) {
      console.log(`\n  ${failure.id}`);
      for (const f of failure.failures) console.log(`    - ${f.check}: ${f.detail}`);
      console.log(`    reply: ${failure.reply.slice(0, 160)}`);
    }
    process.exit(1);
  }

  console.log("\nall cases passed.");
}

main();
