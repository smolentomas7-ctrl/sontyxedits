import { getContent } from "@/content";
import { SERVICE_SLUGS, type Locale } from "@/content/types";
import { formattedAddress, site } from "@/config/miauto";
import { normalize, tokens } from "./normalize";
import type { Node } from "./types";

/**
 * TIER 1 — scripted.
 *
 * Built first, and the fallback for every failure mode above it. The copy here
 * is pulled from the same content files the pages render, so the assistant and
 * the site can never disagree about a fact.
 *
 * Below the score threshold it does NOT answer: it names what it can help with
 * and gives the phone number. Guessing at a question it did not understand is
 * how a scripted bot starts inventing.
 */

const SERVICE_KEYWORDS: Record<(typeof SERVICE_SLUGS)[number], readonly string[]> = {
  "diagnostika-vozidiel": [
    "diagnostika", "diagnostiku", "diagnostiky", "kontrolka", "kontrolku", "kontrolky",
    "chybovy", "chybove", "kod", "kody", "obd", "porucha", "poruchu", "svieti",
    "diagnostics", "warning", "lights", "light", "fault", "faults", "code", "codes",
    "scan", "scanner", "nastartovat", "startuje",
  ],
  "cipovanie-ecu": [
    "cipovanie", "cipovat", "cip", "ecu", "chiptuning", "tuning", "softver", "softveru",
    "riadiacej", "jednotky", "remap", "chip", "chipovanie", "software", "upravu", "uprava",
  ],
  "geometria-kolies": [
    "geometria", "geometriu", "geometrie", "zbiehavost", "nastavenie", "kolies",
    "taha", "tahá", "volant", "alignment", "aligned", "wheels", "wheel", "tracking",
    "camber", "toe", "zbiehavosti", "nastavit",
  ],
  pneuservis: [
    "pneuservis", "pneumatiky", "pneumatik", "gumy", "prezutie", "prezuvanie",
    "vyvazenie", "vyvazovanie", "disky", "disk", "defekt", "prezujete", "prezut",
    "zimne", "letne", "tyre", "tyres", "tire", "tires", "puncture", "balancing",
  ],
  "elektroinstalacia-vw": [
    "elektro", "elektrika", "elektroinstalacia", "elektronika", "kabelaz", "vodic",
    "zasuvka", "konektor", "vw", "volkswagen", "koncern", "skoda", "audi", "seat",
    "electrics", "electrical", "wiring", "battery", "vybija", "bateria", "baterie",
    "svetla", "okna", "zamykanie",
  ],
  "vymena-rozvodov": [
    "rozvody", "rozvod", "rozvodov", "rozvodi", "rozvodu", "remen", "retaz", "timing",
    "belt", "belts", "chain", "tdi", "2 0 tdi", "3 0 tdi", "vacky", "menite", "vymena",
  ],
  "servis-klimatizacie": [
    "klimatizacia", "klimatizaciu", "klimatizacie", "klima", "chladivo", "nechladi",
    "aircondition", "air conditioning", "conditioning", "refrigerant", "r134a", "r1234yf",
    "nechladi", "chladi", "cooling", "aircon",
  ],
};

const REFUSAL_KEYWORDS = {
  price: [
    "cena", "cenu", "ceny", "cennik", "stoji", "stoja", "kolko", "koli", "euro", "eur",
    "price", "cost", "costs", "how much", "quote", "expensive", "lacne", "zlava",
  ],
  duration: [
    "dlho", "trva", "trvat", "cas", "casu", "termin", "kedy to bude", "rychlo",
    "how long", "duration", "take", "wait", "waiting",
  ],
  guarantee: [
    "zaruka", "zaruku", "garancia", "garanciu", "rucite", "guarantee", "warranty", "warranties",
  ],
  power: [
    "kon", "koni", "konskych", "vykon", "vykonu", "kw", "nm", "krutiaci", "moment",
    "horsepower", "hp", "power", "torque", "bhp", "spotreba", "consumption",
  ],
} as const;

export function buildNodes(locale: Locale): Node[] {
  const t = getContent(locale);
  const sk = locale === "sk";
  const castrol = t.castrol;
  const callLine = sk
    ? `Zavolajte na ${site.phone}.`
    : `Call ${site.phone}.`;

  const nodes: Node[] = [];

  // One node per service, reusing the page's own card description and lead.
  for (const slug of SERVICE_SLUGS) {
    const service = t.services[slug];
    nodes.push({
      id: `service.${slug}`,
      keywords: SERVICE_KEYWORDS[slug],
      answer: `${service.overview} ${
        sk ? "Podrobnosti sú na stránke služby." : "There is more on the service page."
      } ${callLine} [source: service.${slug}]`,
      chips: sk
        ? ["Kde vás nájdem?", "Aké máte otváracie hodiny?"]
        : ["Where are you?", "What are your opening hours?"],
      cta: "phone",
    });
  }

  nodes.push(
    {
      id: "contact.hours",
      keywords: [
        "hodiny", "otvaracie", "otvorene", "otvoreno", "zatvorene", "vikend",
        "prestavka", "prestavku", "obed", "obedna", "obednajsia", "pauza", "break", "lunch",
        "sobota", "sobotu", "nedela", "nedelu",
        "hours", "open", "opening", "closed", "weekend", "saturday", "sunday",
      ],
      answer: sk
        ? `Otvorené máme v pracovné dni od ${site.hours.mon[0]} do ${site.hours.mon[1]}, s obedňajšou prestávkou od ${site.lunchBreak[0]} do ${site.lunchBreak[1]}. V sobotu a v nedeľu je zatvorené. [source: contact]`
        : `We are open on weekdays from ${site.hours.mon[0]} to ${site.hours.mon[1]}, with a lunch break from ${site.lunchBreak[0]} to ${site.lunchBreak[1]}. Closed on Saturday and Sunday. [source: contact]`,
      chips: sk ? ["Kde vás nájdem?", "Ako si dohodnem termín?"] : ["Where are you?", "How do I arrange a visit?"],
      cta: "phone",
    },
    {
      id: "contact.address",
      keywords: [
        "kde", "adresa", "adresu", "najdem", "najst", "navigacia", "mapa", "sidlo",
        "ruzomberok", "ruzomberku", "sladkovicova",
        "where", "address", "find", "located", "location", "map", "directions",
      ],
      answer: sk
        ? `Nájdete nás na adrese ${formattedAddress}. Na stránke Kontakt je mapa aj odkaz na navigáciu. [source: contact]`
        : `We are at ${formattedAddress}. The contact page has a map and a directions link. [source: contact]`,
      chips: sk ? ["Aké máte otváracie hodiny?", "Aké služby ponúkate?"] : ["What are your opening hours?", "What services do you offer?"],
      cta: "phone",
    },
    {
      id: "contact.visit",
      keywords: [
        "objednat", "objednajte", "objednanie", "dohodnut", "dohodnem", "navsteva",
        "prist", "rezervacia", "rezervovat", "termin",
        "book", "booked", "booking", "arrange", "appointment", "visit", "reserve",
      ],
      answer: sk
        ? `Termín si dohodnete telefonicky na ${site.phone}. Mimo otváracích hodín použite formulár na stránke Kontakt. Sám termín rezervovať neviem. [source: contact]`
        : `Arrange a visit by calling ${site.phone}. Outside opening hours, use the form on the contact page. I cannot book anything myself. [source: contact]`,
      chips: sk ? ["Čo si mám pripraviť?", "Aké máte otváracie hodiny?"] : ["What should I have ready?", "What are your opening hours?"],
      cta: "form",
    },
    {
      id: "castrol",
      keywords: [
        "olej", "oleja", "oleje", "olejov", "motorovy", "motoroveho", "vymena oleja",
        "castrol", "mazivo", "maziva", "specifikacia", "specifikacie", "viskozita",
        "oil", "oils", "engine oil", "oil change", "lubricant", "viscosity", "spec",
      ],
      // `t` is already the visitor's locale, so one line serves both.
      answer: `${castrol.body} [source: castrol]`,
      chips: sk
        ? ["Ako si dohodnem termín?", "Aké služby ponúkate?"]
        : ["How do I arrange a visit?", "What services do you offer?"],
      cta: "phone",
    },
    {
      id: "faq.priprava",
      keywords: [
        "pripravit", "priprava", "volam", "volat", "co potrebujem", "udaje", "informacie",
        "ready", "prepare", "before calling", "what do i need", "information",
      ],
      answer: sk
        ? `${t.faq.find((f) => f.id === "priprava")?.a ?? ""} [source: faq.priprava]`
        : `${t.faq.find((f) => f.id === "priprava")?.a ?? ""} [source: faq.priprava]`,
      chips: sk ? ["Ako si dohodnem termín?", "Kde vás nájdem?"] : ["How do I arrange a visit?", "Where are you?"],
      cta: "phone",
    },
    {
      id: "faq.vw",
      priority: true,
      keywords: [
        "autorizovany", "autorizovanom", "autorizovany servis", "znacka", "znacky",
        "authorised", "authorized", "authorised service", "official", "dealer", "main dealer",
      ],
      answer: sk
        ? `${t.faq.find((f) => f.id === "vw")?.a ?? ""} [source: service.elektroinstalacia-vw]`
        : `${t.faq.find((f) => f.id === "vw")?.a ?? ""} [source: service.elektroinstalacia-vw]`,
      chips: sk ? ["Robíte čipovanie ECU?", "Aké služby ponúkate?"] : ["Do you do ECU work?", "What services do you offer?"],
      cta: "phone",
    },
    {
      id: "faq.sluzby",
      keywords: [
        "sluzby", "sluzieb", "ponukate", "robite", "co robite", "zoznam",
        "services", "offer", "what do you do", "list",
      ],
      answer: sk
        ? `${t.faq.find((f) => f.id === "sluzby")?.a ?? ""} [source: faq.sluzby]`
        : `${t.faq.find((f) => f.id === "sluzby")?.a ?? ""} [source: faq.sluzby]`,
      chips: sk ? ["Robíte geometriu?", "Kde vás nájdem?"] : ["Do you do wheel alignment?", "Where are you?"],
      cta: "services",
    },

    // ---- refusals -------------------------------------------------------
    {
      id: "refusal.price",
      priority: true,
      keywords: REFUSAL_KEYWORDS.price,
      answer: sk
        ? `Ceny neuvádzam — na stránke žiadne nie sú a vymýšľať si ich nebudem. Cenu za konkrétnu prácu na konkrétnom vozidle vám povedia na ${site.phone}. [source: contact]`
        : `I do not give prices — there are none on this site and I will not invent one. For a price on specific work on a specific vehicle, call ${site.phone}. [source: contact]`,
      chips: sk ? ["Aké služby ponúkate?", "Aké máte otváracie hodiny?"] : ["What services do you offer?", "What are your opening hours?"],
      cta: "phone",
    },
    {
      id: "refusal.duration",
      priority: true,
      keywords: REFUSAL_KEYWORDS.duration,
      answer: sk
        ? `Ako dlho oprava potrvá, neviem povedať — závisí to od vozidla a od toho, čo sa nájde. Povedia vám to na ${site.phone}. [source: contact]`
        : `I cannot say how long a repair will take — it depends on the vehicle and on what is found. ${site.phone} can tell you. [source: contact]`,
      chips: sk ? ["Ako si dohodnem termín?", "Aké služby ponúkate?"] : ["How do I arrange a visit?", "What services do you offer?"],
      cta: "phone",
    },
    {
      id: "refusal.guarantee",
      priority: true,
      keywords: REFUSAL_KEYWORDS.guarantee,
      answer: sk
        ? `O zárukách nemám žiadne informácie, takže k nim nič netvrdím. Opýtajte sa priamo na ${site.phone}. [source: contact]`
        : `I have no information about guarantees, so I will not claim anything about them. Ask directly on ${site.phone}. [source: contact]`,
      chips: sk ? ["Aké služby ponúkate?", "Kde vás nájdem?"] : ["What services do you offer?", "Where are you?"],
      cta: "phone",
    },
    {
      id: "refusal.power",
      priority: true,
      keywords: REFUSAL_KEYWORDS.power,
      answer: sk
        ? `Čísla o výkone, krútiacom momente ani spotrebe neuvádzam — žiadne tu nie sú. Čo je pri vašom motore možné, preberiete na ${site.phone}. [source: service.cipovanie-ecu]`
        : `I do not give figures for power, torque or fuel consumption — there are none here. What is possible on your engine is a conversation for ${site.phone}. [source: service.cipovanie-ecu]`,
      chips: sk ? ["Robíte čipovanie ECU?", "Aké služby ponúkate?"] : ["Do you do ECU work?", "What services do you offer?"],
      cta: "phone",
    },
  );

  return nodes;
}

/**
 * Below this, the assistant says it did not understand rather than guessing.
 * One confident keyword is enough to route; zero is not, which is what keeps
 * "what is the capital of France" on the fallback.
 */
const SCORE_THRESHOLD = 1;

export function fallbackAnswer(locale: Locale): Node {
  const sk = locale === "sk";
  return {
    id: "fallback",
    answer: sk
      ? `Tomu nerozumiem. Viem poradiť so službami, s otváracími hodinami a s tým, kde nás nájdete. Čokoľvek iné vám povedia na ${site.phone}.`
      : `I did not follow that. I can help with the services, the opening hours and where to find the workshop. For anything else, call ${site.phone}.`,
    chips: sk
      ? ["Aké služby ponúkate?", "Aké máte otváracie hodiny?"]
      : ["What services do you offer?", "What are your opening hours?"],
    cta: "phone",
  };
}

/**
 * Keyword scoring. Multi-word keywords count double, because "how long" hitting
 * as a phrase is a much stronger signal than "how" and "long" separately.
 */
export function scoreNode(node: Node, input: string): number {
  if (!node.keywords) return 0;
  const haystack = normalize(input);
  const words = new Set(tokens(input));
  let score = 0;
  for (const keyword of node.keywords) {
    if (keyword.includes(" ")) {
      if (haystack.includes(keyword)) score += 2;
    } else if (words.has(keyword)) {
      score += 1;
    }
  }
  return score;
}

export function respondScripted(locale: Locale, message: string): Node {
  const nodes = buildNodes(locale);

  let best: Node | null = null;
  let bestScore = 0;
  let bestPriority = false;

  for (const node of nodes) {
    const score = scoreNode(node, message);
    if (score === 0) continue;
    const priority = node.priority === true;

    // A priority node wins an equal score, so "how much does a timing belt
    // cost" refuses the price rather than describing timing belts.
    const wins =
      score > bestScore || (score === bestScore && priority && !bestPriority);
    if (wins) {
      best = node;
      bestScore = score;
      bestPriority = priority;
    }
  }

  if (!best || bestScore < SCORE_THRESHOLD) return fallbackAnswer(locale);
  return best;
}

/** The scripted answer closest to an intent, used when the verifier blocks twice. */
export function scriptedForIntent(locale: Locale, intent: string): Node {
  const nodes = buildNodes(locale);
  return nodes.find((node) => node.id === intent) ?? fallbackAnswer(locale);
}
