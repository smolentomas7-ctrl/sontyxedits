import { siteConfig } from "@/config/site";
import { LOCALES } from "@/content/i18n";

/**
 * Builds the canonical + hreflang alternates block for a page.
 *
 * `path` is the route below the locale segment, with no leading slash —
 * "" for the home page, "portfolio" for /sk/portfolio, "blog/some-slug" and
 * so on. The slugs are identical across locales by design, so one path
 * produces every alternate.
 */
export function buildAlternates(path: string) {
  const suffix = path ? `/${path}` : "";

  const languages: Record<string, string> = {};
  for (const locale of LOCALES) {
    languages[locale] = `${siteConfig.url}/${locale}${suffix}`;
  }
  languages["x-default"] = `${siteConfig.url}/sk${suffix}`;

  return { languages };
}

/** Canonical URL for one locale and path. */
export function canonicalUrl(locale: string, path: string): string {
  return `${siteConfig.url}/${locale}${path ? `/${path}` : ""}`;
}

/**
 * Open Graph image for a locale, served by app/(site)/[locale]/og/route.tsx.
 *
 * Page-level `openGraph` in generateMetadata replaces the layout's rather than
 * merging with it, so every page that sets openGraph must spread this in or it
 * will ship without an image.
 */
export function ogImages(locale: string) {
  return [{ url: `${siteConfig.url}/${locale}/og`, width: 1200, height: 630 }];
}
