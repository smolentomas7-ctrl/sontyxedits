/**
 * Single source of truth for brand and contact data.
 *
 * No component hardcodes a contact detail. Values wrapped in square brackets are
 * deliberate placeholders: they RENDER VISIBLY, brackets included, so they cannot
 * ship unnoticed. `isPlaceholder()` is how the UI decides to hide a link rather
 * than point at the literal text.
 */
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
  email: "[EMAIL]",
  ico: "[IČO]",
  ownerName: "Ivan Kubis",
  hours: {
    mon: ["08:00", "16:00"],
    tue: ["08:00", "16:00"],
    wed: ["08:00", "16:00"],
    thu: ["08:00", "16:00"],
    fri: ["08:00", "16:00"],
    sat: null,
    sun: null,
  },
  // Geocoded from the street address: exact coordinates were never supplied.
  // Replacing this one value with a `?q=<lat>,<lng>` URL pins the map precisely.
  mapEmbedUrl:
    "https://www.google.com/maps?q=Sl%C3%A1dkovi%C4%8Dova%202528%2F108%2C%20034%2001%20Ru%C5%BEomberok&output=embed",
  mapDirectionsUrl:
    "https://www.google.com/maps/dir/?api=1&destination=Sl%C3%A1dkovi%C4%8Dova%202528%2F108%2C%20034%2001%20Ru%C5%BEomberok",
  social: { facebook: "[FACEBOOK_URL]", instagram: "[INSTAGRAM_URL]" },
} as const;

export type Site = typeof site;
export type DayKey = keyof Site["hours"];

export const DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] as const;

/** A value still awaiting real content, e.g. "[EMAIL]". */
export function isPlaceholder(value: string): boolean {
  return /^\[.*\]$/.test(value.trim());
}

/** Production URL. Netlify sets URL/DEPLOY_PRIME_URL; everything else falls back. */
export const siteUrl = (
  process.env.NEXT_PUBLIC_SITE_URL ??
  process.env.URL ??
  "http://localhost:3000"
).replace(/\/$/, "");

export const formattedAddress = `${site.street}, ${site.postalCode} ${site.city}`;
