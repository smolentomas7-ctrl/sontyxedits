/**
 * Single source of truth for brand and contact data.
 *
 * There are exactly two ways to reach Webora: e-mail and WhatsApp. The site
 * has no contact form, so these values are the only route a visitor has —
 * no component may hardcode them, and nothing else may be presented as a
 * contact channel.
 *
 * Bracketed values are PLACEHOLDERS. They render literally so they are
 * impossible to miss before launch.
 */

/** Digits only, international format — what wa.me expects in its path. */
const WHATSAPP_E164 = "421918757493";

export const siteConfig = {
  name: "Webora",
  tagline: {
    sk: "Webové stránky pre malé firmy",
    en: "Websites for small businesses",
  },

  /** Secondary contact. */
  email: "weboraeurope@gmail.com",

  /** Primary contact — the hero and every CTA band lead with it. */
  whatsapp: {
    /** Human-readable, with spaces. */
    display: "+421 918 757 493",
    /** wa.me takes no "+" and no spaces, or the link resolves to nothing. */
    href: `https://wa.me/${WHATSAPP_E164}`,
  },

  /** Shown in the footer's legal line. */
  companyId: "[IČO]",

  /** Typical first-response time. */
  responseTime: {
    sk: "Odpovedám do 24 hodín počas pracovných dní.",
    en: "I reply within 24 hours on business days.",
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

/** `mailto:` with a subject, so the draft arrives already labelled. */
export function mailtoHref(subject?: string): string {
  const to = `mailto:${siteConfig.email}`;
  return subject ? `${to}?subject=${encodeURIComponent(subject)}` : to;
}
