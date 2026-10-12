/**
 * Generates content/knowledge.generated.ts from content/, so the chat assistant's
 * knowledge can never drift from what the pages actually say.
 *
 * Runs in `prebuild`. The output is committed and diffable: a change to the
 * assistant's knowledge shows up in review as a change to a checked-in file.
 *
 * Build fails if the knowledge comes out empty, or shrinks by more than 50%
 * against the committed version. A silently empty <knowledge> block turns a
 * grounded assistant into a confident improviser, which is the single worst
 * failure this system can have.
 */
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { sk } from "../content/sk";
import { en } from "../content/en";
import { SERVICE_SLUGS, type Locale, type LocaleContent } from "../content/types";
import { DAY_ORDER, formattedAddress, site } from "../config/miauto";

type Section = { id: string; title: string; source: string; body: string };

const OUT = join(process.cwd(), "content", "knowledge.generated.ts");
const SHRINK_LIMIT = 0.5;

function hoursLine(locale: Locale): string {
  const open = DAY_ORDER.filter((day) => site.hours[day]);
  const first = site.hours[open[0] ?? "mon"];
  return locale === "sk"
    ? `Otváracie hodiny: pondelok až piatok ${first?.[0]}–${first?.[1]}. ` +
      `V sobotu a v nedeľu je zatvorené.`
    : `Opening hours: Monday to Friday ${first?.[0]}–${first?.[1]}. ` +
      `Closed on Saturday and Sunday.`;
}

function collect(locale: Locale, t: LocaleContent): Section[] {
  const sections: Section[] = [];

  // about -> /{locale}/o-nas
  sections.push({
    id: "about",
    title: t.about.h1,
    source: `/${locale}/o-nas`,
    body: [
      t.about.lead,
      ...t.about.quietBody,
      `${t.about.ownerHeading}: ${site.ownerName} (${t.about.ownerRole}).`,
      locale === "sk"
        ? "Text o servise a o majiteľovi zatiaľ klient nedodal, takže o histórii, počte rokov ani o tíme nie sú žiadne údaje."
        : "The client has not yet supplied the copy about the workshop or its owner, so there is no information about history, years in business or team size.",
    ].join("\n"),
  });

  // service.<slug> -> /{locale}/sluzby/<slug>
  for (const slug of SERVICE_SLUGS) {
    const service = t.services[slug];
    sections.push({
      id: `service.${slug}`,
      title: service.name,
      source: `/${locale}/sluzby/${slug}`,
      body: [
        service.lead,
        "",
        locale === "sk" ? "Kedy to riešiť:" : "When to deal with it:",
        ...service.when.map((item) => `- ${item}`),
        "",
        locale === "sk" ? "Čo robíme:" : "What we do:",
        ...service.what.map((item) => `- ${item}`),
        service.note ? `\n${service.note}` : "",
        "",
        locale === "sk" ? "Nepotvrdený rozsah:" : "Unconfirmed scope:",
        ...service.toConfirm.map((item) => `- ${item}`),
      ]
        .filter((line) => line !== undefined)
        .join("\n"),
    });
  }

  // faq.<slug> -> /{locale}/sluzby#faq
  for (const item of t.faq) {
    sections.push({
      id: `faq.${item.id}`,
      title: item.q,
      source: `/${locale}/sluzby#faq`,
      body: item.a,
    });
  }

  // contact -> /{locale}/kontakt
  sections.push({
    id: "contact",
    title: t.contact.h1,
    source: `/${locale}/kontakt`,
    body: [
      `${site.legalName}, ${formattedAddress}, ${locale === "sk" ? "Slovensko" : "Slovakia"}.`,
      `${locale === "sk" ? "Telefón" : "Phone"}: ${site.phone}.`,
      hoursLine(locale),
      locale === "sk"
        ? "E-mailová adresa zatiaľ nie je známa. Termín si zákazník dohodne telefonicky alebo cez formulár na stránke Kontakt."
        : "No email address is known yet. Visits are arranged by phone or through the form on the contact page.",
      locale === "sk"
        ? "Na stránke nie sú žiadne ceny, cenníky, trvania opráv ani záruky."
        : "There are no prices, price lists, repair durations or guarantees anywhere on this site.",
    ].join("\n"),
  });

  return sections;
}

function serialize(sections: Section[]): string {
  return sections
    .map((section) => `[${section.id}] ${section.title}\nsource: ${section.source}\n${section.body}`)
    .join("\n\n---\n\n");
}

function previousSize(): number {
  if (!existsSync(OUT)) return 0;
  const previous = readFileSync(OUT, "utf8");
  const match = previous.match(/TOTAL_CHARS = (\d+)/);
  return match?.[1] ? Number(match[1]) : 0;
}

function main(): void {
  const byLocale: Record<Locale, Section[]> = { sk: collect("sk", sk), en: collect("en", en) };
  const knowledge: Record<string, string> = {};
  const sources: Record<string, Record<string, string>> = {};
  let totalChars = 0;

  for (const [locale, sections] of Object.entries(byLocale)) {
    const text = serialize(sections);
    knowledge[locale] = text;
    totalChars += text.length;
    sources[locale] = Object.fromEntries(sections.map((s) => [s.id, s.source]));

    if (text.trim().length === 0) {
      console.error(`FAIL: knowledge for "${locale}" is empty.`);
      process.exit(1);
    }
  }

  const before = previousSize();
  if (before > 0 && totalChars < before * SHRINK_LIMIT) {
    console.error(
      `FAIL: knowledge shrank from ${before} to ${totalChars} characters ` +
        `(more than ${(1 - SHRINK_LIMIT) * 100}%). Refusing to ship a gutted knowledge base.`,
    );
    process.exit(1);
  }

  const hash = createHash("sha256")
    .update(Object.values(knowledge).join("\u0000"))
    .digest("hex")
    .slice(0, 16);

  const file = `// GENERATED by scripts/build-knowledge.ts — do not edit by hand.
// Regenerate with \`npm run knowledge\`; it also runs automatically in prebuild.
import type { Locale } from "./types";

export const HASH = ${JSON.stringify(hash)};
export const TOTAL_CHARS = ${totalChars};

export const KNOWLEDGE: Record<Locale, string> = ${JSON.stringify(knowledge, null, 2)};

/** Section id -> the page path that section was collected from. */
export const SOURCES: Record<Locale, Record<string, string>> = ${JSON.stringify(sources, null, 2)};
`;

  writeFileSync(OUT, file, "utf8");

  const words = Math.round(totalChars / 4.2);
  console.log(
    `knowledge: ${Object.keys(byLocale).length} locales, ` +
      `${byLocale.sk.length} sections each, ${totalChars} chars (~${words} tokens), hash ${hash}`,
  );
}

main();
