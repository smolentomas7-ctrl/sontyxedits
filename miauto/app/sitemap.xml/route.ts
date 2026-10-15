import { LOCALES, SERVICE_SLUGS } from "@/content/types";
import { ROUTES } from "@/lib/i18n";
import { siteUrl, siteUrlIsPlaceholder } from "@/config/miauto";

/**
 * /sitemap.xml, written out by hand rather than through Next's `sitemap.ts`
 * convention.
 *
 * The convention produces correct XML but gives no say over how it is
 * serialised — no indentation, and a second namespace declared on the root the
 * moment any alternate is attached. For a file whose whole job is to be read,
 * by a crawler and occasionally by a person checking it in a browser, the exact
 * bytes are worth owning. There are 24 of them and the shape is three elements
 * deep; this is less machinery than it looks.
 *
 * Deliberately absent, and why:
 *
 *   lastmod — it would have to be invented. All 24 pages are generated from the
 *     same two content files, so neither a build timestamp nor a file date says
 *     anything true about an individual page. Google treats an unreliable
 *     lastmod as a reason to ignore the field across a whole site, so no date
 *     beats a wrong one. It belongs here once something records when a given
 *     page actually changed.
 *
 *   changefreq and priority — Google ignores both, and priority would only be
 *     this file guessing at its own importance.
 *
 *   hreflang alternates — the same claim is already in the <head> of all 24
 *     pages as <link rel="alternate">. Google wants it declared once; a second
 *     copy is not a stronger signal.
 *
 *   `/` — a 301 to /sk. A sitemap lists destinations, not redirects.
 *
 * `force-static` is what lets this exist in the static export: it is rendered
 * to a file at build time, so no server is involved on either deploy path.
 */
export const dynamic = "force-static";

/** XML text escaping. No slug needs it today; one containing `&` would. */
function xml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/** The 12 indexable routes, in the order a visitor meets them. */
const ROUTE_PATHS = [
  ROUTES.home,
  ROUTES.services,
  ...SERVICE_SLUGS.map((slug) => `${ROUTES.services}/${slug}`),
  ROUTES.about,
  ROUTES.contact,
  ROUTES.privacy,
];

export function GET(): Response {
  // Every entry is an absolute URL, so a build pointed at localhost has nothing
  // truthful to put in one.
  const urls = siteUrlIsPlaceholder
    ? []
    : LOCALES.flatMap((locale) => ROUTE_PATHS.map((route) => `${siteUrl}/${locale}${route}`));

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...urls.map((url) => `  <url>\n    <loc>${xml(url)}</loc>\n  </url>`),
    "</urlset>",
    "",
  ].join("\n");

  return new Response(body, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=0, must-revalidate",
    },
  });
}
