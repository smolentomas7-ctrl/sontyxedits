/**
 * Single source of truth for brand and contact data.
 *
 * Nothing in a component hardcodes a contact detail. Values that are not yet
 * known are an empty string, and `has()` is how the UI decides whether to render
 * that piece at all. Nothing on the site ever renders a bracketed placeholder:
 * a block with no data does not exist on the page.
 */

/** A piece of data the client has not supplied yet. */
export const PENDING = "" as const;

/** True when a config value holds real data and may be rendered. */
export function has(value: string | undefined | null): value is string {
  return typeof value === "string" && value.trim() !== "";
}

export type Owner = {
  /** Full name as it should appear in print. */
  readonly name: string;
  /** Role, keyed into content so it can be translated. */
  readonly roleKey: "coOwner" | "owner";
  /** Image slot id in config/images.ts, or "" while no photograph exists. */
  readonly photo: string;
};

export const site = {
  legalName: "M.I.Auto s.r.o.",
  shortName: "M.I.Auto",
  street: "Sládkovičova 2528/108",
  postalCode: "034 01",
  city: "Ružomberok",
  country: "SK",
  region: "Žilinský kraj",
  phone: "+421 918 918 109",
  phoneHref: "tel:+421918918109",
  email: "ivankubis96@centrum.sk",

  /**
   * Company registration data.
   *
   * § 3a of the Slovak Commercial Code requires a company's business name,
   * registered seat, company number (IČO) and its commercial-register entry to
   * appear on its business website. These are therefore NOT optional in the
   * legal sense — they are empty only because nobody has supplied them, each
   * renders only once filled, and the handover report lists them as a launch
   * blocker. They are never guessed.
   */
  ico: PENDING,
  dic: PENDING,
  icDph: PENDING,
  /** e.g. "Obchodný register Okresného súdu Žilina, oddiel: Sro, vložka č. …" */
  zapisVOR: PENDING,

  /**
   * Owners, rendered by components/about/Owners.tsx. The component handles one
   * or two entries without a layout change. While this array is empty the whole
   * section is absent from the page — no outline cards, no initials.
   */
  owners: [
    { name: "Marián Hrnčiar", roleKey: "coOwner", photo: "owner-01" },
    { name: "Ivan Kubis", roleKey: "coOwner", photo: "owner-02" },
  ] as readonly Owner[],

  hours: {
    mon: ["08:00", "16:00"],
    tue: ["08:00", "16:00"],
    wed: ["08:00", "16:00"],
    thu: ["08:00", "16:00"],
    fri: ["08:00", "16:00"],
    sat: null,
    sun: null,
  },

  /**
   * Geocoded from the street address: exact coordinates were never supplied.
   * Replacing this with `?q=<lat>,<lng>&output=embed` pins the map precisely,
   * and filling `geo` below adds coordinates to the structured data.
   */
  mapEmbedUrl:
    "https://www.google.com/maps?q=Sl%C3%A1dkovi%C4%8Dova%202528%2F108%2C%20034%2001%20Ru%C5%BEomberok&output=embed",
  mapDirectionsUrl:
    "https://www.google.com/maps/dir/?api=1&destination=Sl%C3%A1dkovi%C4%8Dova%202528%2F108%2C%20034%2001%20Ru%C5%BEomberok",
  /** Public Google Maps link for schema.org hasMap. */
  mapUrl:
    "https://www.google.com/maps/search/?api=1&query=Sl%C3%A1dkovi%C4%8Dova%202528%2F108%2C%20034%2001%20Ru%C5%BEomberok",
  /** Latitude / longitude. Left empty rather than estimated from the address. */
  geo: { lat: PENDING, lng: PENDING },

  /** Social profiles. Rendered only when a real URL is present. */
  social: { facebook: PENDING, instagram: PENDING },
} as const;

export type Site = typeof site;
export type DayKey = keyof Site["hours"];

export const DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] as const;

/**
 * Production URL. Netlify sets URL/DEPLOY_PRIME_URL on a deploy, but the final
 * domain has to be set explicitly as NEXT_PUBLIC_SITE_URL, because canonicals,
 * hreflang, the sitemap, robots.txt and the OG tags all derive from it and a
 * preview URL in those is worse than useless for search.
 */
export const siteUrl = (
  process.env.NEXT_PUBLIC_SITE_URL ??
  process.env.URL ??
  "http://localhost:3000"
).replace(/\/$/, "");

/** True when siteUrl is still a local or preview address rather than the domain. */
export const siteUrlIsPlaceholder =
  !process.env.NEXT_PUBLIC_SITE_URL || siteUrl.includes("localhost");

export const formattedAddress = `${site.street}, ${site.postalCode} ${site.city}`;
export const mailtoHref = `mailto:${site.email}`;
