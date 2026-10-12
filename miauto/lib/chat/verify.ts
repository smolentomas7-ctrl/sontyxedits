import { SOURCES } from "@/content/knowledge.generated";
import type { Locale } from "@/content/types";

/**
 * Output verification, run before any reply reaches the visitor.
 *
 * A grounded model is still a model. These four checks exist because the
 * knowledge contains no prices, no performance figures and no ability to act,
 * so anything matching them is by definition invented.
 */

export type VerdictCode = "currency" | "ecu-figures" | "commitment";

export type Verdict =
  | { readonly ok: true; readonly text: string }
  | { readonly ok: false; readonly code: VerdictCode; readonly detail: string };

/**
 * Anything that reads as a monetary amount. The knowledge contains no prices at
 * all, so any match is invented.
 *
 * Note the symbol alternatives carry no trailing \b: a word boundary after "€"
 * requires a word character immediately after it, so /€\b/ never matches the
 * ordinary "450 € vrátane" and the whole check would quietly pass everything.
 */
const CURRENCY = [
  // amount then symbol: "450 €", "450€", "1 200 $"
  /(?:^|[\s(])\d[\d\s.,]*\s*(?:€|\$|£)/,
  // amount then currency word: "450 eur", "99 Kč", "20 dollars"
  /(?:^|[\s(])\d[\d\s.,]*\s*(?:eur|euro|eurov|usd|czk|kc|kč|dolár|dollar|pound)/i,
  // symbol then amount: "€450", "$99"
  /(?:€|\$|£)\s*\d/,
  // "okolo tisíc eur", "about a thousand euros"
  /\b(?:tis[íi]c|thousand|stovák|hundred)\s+(?:€|eur|dollar)/i,
];

/** Power, torque or consumption figures, only policed on ECU answers. */
const ECU_FIGURES = [
  /\b\d[\d.,]*\s*(?:kw|hp|bhp|ps|k[ií]?[nň]?|kon[ií]|konsk[yý]ch|nm)\b/i,
  /\b\d[\d.,]*\s*%/,
  /\b\d[\d.,]*\s*l\s*\/\s*100\s*km\b/i,
];

/** Claims of a completed action. The assistant has no tools, so all are invalid. */
const COMMITMENT = [
  /\b(objednal|objednala|objednali|objednan[éеe]|objedn[áa]vam|rezervoval|rezervovala|rezervovan[éе]|rezervujem|odoslal|odoslala|odoslan[éе]|posielam|preposlal|potvrdil|potvrdila|potvrden[éе]|zapísal|zapisujem|zaregistroval)\b/i,
  /\b(i have (?:booked|reserved|sent|forwarded|scheduled|registered|arranged)|i(?:'ve| have) (?:passed|put) (?:this|it) (?:on|through)|has been (?:booked|reserved|sent|forwarded|scheduled)|your (?:booking|appointment) (?:is|has been) (?:confirmed|made))\b/i,
];

function matches(patterns: readonly RegExp[], text: string): string | null {
  for (const pattern of patterns) {
    const found = pattern.exec(text);
    if (found) return found[0].trim();
  }
  return null;
}

export function verify(
  text: string,
  options: { readonly locale: Locale; readonly ecuContext: boolean },
): Verdict {
  const currency = matches(CURRENCY, text);
  if (currency) return { ok: false, code: "currency", detail: currency };

  if (options.ecuContext) {
    const figure = matches(ECU_FIGURES, text);
    if (figure) return { ok: false, code: "ecu-figures", detail: figure };
  }

  const commitment = matches(COMMITMENT, text);
  if (commitment) return { ok: false, code: "commitment", detail: commitment };

  return { ok: true, text: stripUnknownSources(text, options.locale) };
}

/**
 * A [source: id] tag that names a section which does not exist would render as a
 * dead chip, so it is stripped rather than shown.
 */
export function stripUnknownSources(text: string, locale: Locale): string {
  const known = SOURCES[locale];
  return text.replace(/\s*\[source:\s*([^\]]+)\]/gi, (match, id: string) => {
    return known[id.trim()] ? match : "";
  });
}

export function extractSources(text: string, locale: Locale): string[] {
  const known = SOURCES[locale];
  const ids: string[] = [];
  for (const match of text.matchAll(/\[source:\s*([^\]]+)\]/gi)) {
    const id = (match[1] ?? "").trim();
    if (known[id] && !ids.includes(id)) ids.push(id);
  }
  return ids;
}

/** The instruction appended on the single retry after a verifier block. */
export function retryInstruction(code: VerdictCode, locale: Locale): string {
  const sk = locale === "sk";
  switch (code) {
    case "currency":
      return sk
        ? "Tvoja predchádzajúca odpoveď obsahovala sumu. Žiadne ceny neexistujú. Odpovedz znova bez akejkoľvek sumy a odkáž na telefón."
        : "Your previous reply contained a monetary amount. No prices exist. Answer again with no amount of any kind and point at the phone number.";
    case "ecu-figures":
      return sk
        ? "Tvoja predchádzajúca odpoveď obsahovala číselný údaj o výkone, momente alebo spotrebe. Také údaje neexistujú. Odpovedz znova bez čísel."
        : "Your previous reply contained a power, torque or consumption figure. No such figures exist. Answer again with no figures.";
    case "commitment":
      return sk
        ? "Tvoja predchádzajúca odpoveď tvrdila, že si niečo vybavil. Nemáš žiadne nástroje a nič vybaviť nevieš. Odpovedz znova a povedz, ako to zákazník vybaví sám."
        : "Your previous reply claimed you had completed an action. You have no tools and can complete nothing. Answer again, saying how the visitor does it themselves.";
  }
}
