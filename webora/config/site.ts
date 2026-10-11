/**
 * Single source of truth for brand and contact data.
 *
 * The bracketed values below are PLACEHOLDERS. They render literally on the
 * page so they are impossible to miss before launch. Replace every one of them
 * with real data, then search the repo for "[" to confirm none are left.
 *
 * No component may hardcode contact details — read them from here.
 */

export const siteConfig = {
  name: "Webora",
  tagline: {
    sk: "Webové stránky pre malé firmy",
    en: "Websites for small businesses",
  },

  /** Public-facing contact details. */
  email: "[EMAIL]",
  phone: "[TELEFÓN]",
  city: "[MESTO]",
  companyId: "[IČO]",

  /** Founder name, shown on the About page. */
  founder: "[MENO]",

  /** Typical first-response time, shown on the contact page. */
  responseTime: {
    sk: "Odpovedáme do 24 hodín počas pracovných dní.",
    en: "We reply within 24 hours on business days.",
  },

  social: {
    instagram: "[URL]",
    facebook: "[URL]",
    linkedin: "[URL]",
  },

  /**
   * Canonical origin, used for metadata, sitemap and JSON-LD.
   * Change this to the real domain before launch.
   */
  url: "https://webora.sk",
} as const;

export type SiteConfig = typeof siteConfig;

/** True for values that are still unfilled placeholders. */
export function isPlaceholder(value: string): boolean {
  return value.startsWith("[") && value.endsWith("]");
}
