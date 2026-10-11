/**
 * Price calculator logic.
 *
 * Everything the calculator charges for lives in RATES below. To change what
 * the site quotes, edit that one constant — no other file needs touching.
 *
 * All figures are EUR, excluding VAT, and are deliberately returned as a
 * range rather than a single number: the low end assumes a straightforward
 * build with materials supplied, the high end assumes more rounds of revision
 * and more work on content.
 */

export type SiteType = "landing" | "business" | "eshop";

export type AddonId =
  | "blog"
  | "booking"
  | "ecommerce"
  | "copywriting"
  | "logo"
  | "photography"
  | "care";

export type CalculatorInput = {
  siteType: SiteType;
  /** Total pages, including the home page. Clamped to 1–20. */
  pages: number;
  /** Number of languages the site ships in. Clamped to 1–3. */
  languages: number;
  addons: AddonId[];
};

/* ============================================================
   RATE TABLE — the single place prices are defined
   ============================================================ */

export const RATES = {
  /** Starting price for each type of site, covering the pages in `includedPages`. */
  base: {
    landing: 490,
    business: 990,
    eshop: 2400,
  } as Record<SiteType, number>,

  /** How many pages the base price already covers. */
  includedPages: {
    landing: 1,
    business: 5,
    eshop: 6,
  } as Record<SiteType, number>,

  /** Charged per page beyond `includedPages`. */
  perExtraPage: {
    landing: 120,
    business: 140,
    eshop: 160,
  } as Record<SiteType, number>,

  /**
   * Each language beyond the first adds a share of the subtotal, covering
   * translation handling, a second content set and extra testing.
   */
  perExtraLanguageShare: 0.3,

  /** Flat price per add-on. `care` is monthly and excluded from the one-off total. */
  addons: {
    blog: 240,
    booking: 420,
    ecommerce: 1200,
    copywriting: 320,
    logo: 280,
    photography: 350,
    care: 39,
  } as Record<AddonId, number>,

  /** Add-ons billed monthly rather than once. */
  monthlyAddons: ["care"] as AddonId[],

  /** The quoted range runs from total × low to total × high. */
  rangeLow: 1,
  rangeHigh: 1.35,

  /** Final figures are rounded to this nearest multiple, for readability. */
  roundTo: 10,
} as const;

export const ADDON_IDS: AddonId[] = [
  "blog",
  "booking",
  "ecommerce",
  "copywriting",
  "logo",
  "photography",
  "care",
];

export const MIN_PAGES = 1;
export const MAX_PAGES = 20;
export const MIN_LANGUAGES = 1;
export const MAX_LANGUAGES = 3;

export type BreakdownLine = {
  /** Stable identifier; the UI maps this to a translated label. */
  id: string;
  /** Extra detail, e.g. how many pages are being charged for. */
  detail?: { count: number };
  amount: number;
  /** True when this line is a recurring monthly cost. */
  monthly?: boolean;
};

export type PriceResult = {
  low: number;
  high: number;
  /** Recurring monthly cost, 0 when no monthly add-on is selected. */
  monthly: number;
  lines: BreakdownLine[];
};

function clamp(value: number, min: number, max: number): number {
  if (Number.isNaN(value)) return min;
  return Math.min(max, Math.max(min, Math.round(value)));
}

function roundTo(value: number, step: number): number {
  return Math.round(value / step) * step;
}

/**
 * Pure function: same input always yields the same result, no side effects,
 * no reads from anything outside RATES. Safe to call on every keystroke.
 */
export function calculatePrice(input: CalculatorInput): PriceResult {
  const siteType: SiteType = input.siteType;
  const pages = clamp(input.pages, MIN_PAGES, MAX_PAGES);
  const languages = clamp(input.languages, MIN_LANGUAGES, MAX_LANGUAGES);

  // De-duplicate and drop anything that is not a known add-on id.
  const addons = Array.from(new Set(input.addons)).filter((a): a is AddonId =>
    ADDON_IDS.includes(a),
  );

  const lines: BreakdownLine[] = [];

  // 1. Base price for the chosen type of site.
  const base = RATES.base[siteType];
  lines.push({ id: "base", amount: base });

  // 2. Pages beyond what the base covers.
  const included = RATES.includedPages[siteType];
  const extraPages = Math.max(0, pages - included);
  const extraPagesCost = extraPages * RATES.perExtraPage[siteType];
  if (extraPages > 0) {
    lines.push({ id: "extraPages", detail: { count: extraPages }, amount: extraPagesCost });
  }

  // 3. One-off add-ons.
  let addonsCost = 0;
  let monthly = 0;
  for (const addon of addons) {
    const price = RATES.addons[addon];
    if ((RATES.monthlyAddons as readonly AddonId[]).includes(addon)) {
      monthly += price;
      lines.push({ id: addon, amount: price, monthly: true });
    } else {
      addonsCost += price;
      lines.push({ id: addon, amount: price });
    }
  }

  // 4. Extra languages, charged as a share of everything one-off above.
  const oneOffSubtotal = base + extraPagesCost + addonsCost;
  const extraLanguages = Math.max(0, languages - 1);
  const languagesCost = roundTo(
    oneOffSubtotal * RATES.perExtraLanguageShare * extraLanguages,
    RATES.roundTo,
  );
  if (extraLanguages > 0) {
    lines.push({
      id: "extraLanguages",
      detail: { count: extraLanguages },
      amount: languagesCost,
    });
  }

  const total = oneOffSubtotal + languagesCost;

  return {
    low: roundTo(total * RATES.rangeLow, RATES.roundTo),
    high: roundTo(total * RATES.rangeHigh, RATES.roundTo),
    monthly,
    lines,
  };
}

/**
 * Renders the configuration as plain text, used to pre-fill the contact form
 * when someone sends their estimate as an inquiry.
 */
export function describeConfiguration(
  input: CalculatorInput,
  result: PriceResult,
  labels: {
    siteType: string;
    siteTypeName: string;
    pages: string;
    languages: string;
    addons: string;
    estimate: string;
    addonLabels: Record<string, string>;
    none: string;
  },
): string {
  const addonText =
    input.addons.length > 0
      ? input.addons.map((a) => labels.addonLabels[a] ?? a).join(", ")
      : labels.none;

  return [
    `${labels.siteType}: ${labels.siteTypeName}`,
    `${labels.pages}: ${input.pages}`,
    `${labels.languages}: ${input.languages}`,
    `${labels.addons}: ${addonText}`,
    `${labels.estimate}: ${result.low} – ${result.high} €${
      result.monthly > 0 ? ` + ${result.monthly} €/mes.` : ""
    }`,
  ].join("\n");
}
