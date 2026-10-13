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
  const [breakStart, breakEnd] = site.lunchBreak;
  return locale === "sk"
    ? `Otváracie hodiny: pondelok až piatok ${first?.[0]}–${first?.[1]}, ` +
      `s obedňajšou prestávkou ${breakStart}–${breakEnd}. ` +
      `V sobotu a v nedeľu je zatvorené.`
    : `Opening hours: Monday to Friday ${first?.[0]}–${first?.[1]}, ` +
      `with a lunch break from ${breakStart} to ${breakEnd}. ` +
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
      `${t.about.ownersHeading}: ${site.owners
        .map((owner) => `${owner.name} (${t.about.ownerRoles[owner.roleKey]})`)
        .join(", ")}.`,
      "",
      `${t.about.experience.heading}: ${t.about.experience.body}`,
      ...t.about.experience.points.map((point) => `- ${point.title}: ${point.body}`),
      "",
      // The years are the owners' own experience, not the company's age, and the
      // assistant is told the difference explicitly so it cannot blur the two.
      locale === "sk"
        ? "Uvedené roky sú skúsenosti majiteľov, nie dĺžka pôsobenia firmy. O histórii servisu, veľkosti tímu ani o vybavení dielne nie sú na stránke žiadne údaje."
        : "The years above are the owners' own experience, not how long the company has existed. The site carries no information about the workshop's history, team size or equipment.",
    ].join("\n"),
  });

  // castrol -> /{locale}
  sections.push({
    id: "castrol",
    title: t.castrol.heading,
    source: `/${locale}`,
    body: [
      t.castrol.body,
      ...t.castrol.points.map((point) => `- ${point}`),
      locale === "sk"
        ? "Značky olejov, ich konkrétne špecifikácie, ceny ani intervaly výmeny na stránke uvedené nie sú — tie sa preberajú pre konkrétne vozidlo telefonicky."
        : "No oil grades, specifications, prices or change intervals are published on the site — those are discussed by phone for the specific vehicle.",
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
      `E-mail: ${site.email}.`,
      hoursLine(locale),
      locale === "sk"
        ? "Termín si zákazník dohodne telefonicky alebo cez formulár na stránke Kontakt."
        : "Visits are arranged by phone or through the form on the contact page.",
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
