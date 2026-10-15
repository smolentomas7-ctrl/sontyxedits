import type { MetadataRoute } from "next";
import { LOCALES, SERVICE_SLUGS } from "@/content/types";
import { ROUTES } from "@/lib/i18n";
import { siteUrl, siteUrlIsPlaceholder } from "@/config/miauto";

/** Both builds emit this as a file; nothing about it varies per request. */
export const dynamic = "force-static";

/**
 * The 24 indexable pages: 12 routes in each of the two locales.
 *
 * What is deliberately NOT here:
 *
 *   lastmod — it would have to be invented. Every page is generated from the
 *     same two content files, so a build timestamp would claim all 24 pages
 *     changed whenever any word anywhere did, and a file date would claim the
 *     same. Google treats an unreliable lastmod as a reason to ignore the field
 *     on a whole site, so a page with no date is better off than a page with a
 *     date that is not true. It belongs here only once something records when a
 *     given page's content actually changed.
 *
 *   changefreq and priority — Google ignores both, and priority in particular
 *     would only be this file guessing at its own importance.
 *
 *   `/` — it is a 301 to /sk, and a sitemap lists destinations, not redirects.
 *     /sk is the Slovak home page and is what its canonical names.
 *
 * The hreflang alternates stay: unlike the fields above they are facts, and in
 * a sitemap they are the second place Google accepts a language cluster from.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  // Every entry in a sitemap is an absolute URL, so a build pointed at
  // localhost has nothing truthful to put in one.
  if (siteUrlIsPlaceholder) return [];

  const routes = [
    ROUTES.home,
    ROUTES.services,
    ...SERVICE_SLUGS.map((slug) => `${ROUTES.services}/${slug}`),
    ROUTES.about,
    ROUTES.contact,
    ROUTES.privacy,
  ];

  return LOCALES.flatMap((locale) =>
    routes.map((route) => ({
      url: `${siteUrl}/${locale}${route}`,
      alternates: {
        languages: Object.fromEntries([
          ...LOCALES.map((alt) => [alt, `${siteUrl}/${alt}${route}`]),
          ["x-default", `${siteUrl}/sk${route}`],
        ]),
      },
    })),
  );
}
