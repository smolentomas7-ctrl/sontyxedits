import { DEFAULT_LOCALE, LOCALES, type Locale } from "@/content/types";
import { TRAILING_SLASH, site, siteUrl, siteUrlIsPlaceholder } from "@/config/miauto";

export { DEFAULT_LOCALE, LOCALES };
export type { Locale };

/** Slugs are identical in both locales, so a path maps across by swapping the prefix. */
export const ROUTES = {
  home: "",
  services: "/sluzby",
  about: "/o-nas",
  contact: "/kontakt",
  privacy: "/ochrana-osobnych-udajov",
} as const;

export function path(locale: Locale, route: string = ""): string {
  const clean = route === "/" ? "" : route;
  return `/${locale}${clean}`;
}

export function servicePath(locale: Locale, slug: string): string {
  return `/${locale}${ROUTES.services}/${slug}`;
}

/**
 * Swap the locale on an arbitrary pathname, keeping the rest of the path.
 * "/en/sluzby/pneuservis" -> "/sk/sluzby/pneuservis"
 */
export function swapLocale(pathname: string, to: Locale): string {
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return `/${to}`;
  const [first, ...rest] = segments;
  if ((LOCALES as readonly string[]).includes(first ?? "")) {
    return `/${[to, ...rest].join("/")}`;
  }
  return `/${[to, ...segments].join("/")}`;
}

export function otherLocale(locale: Locale): Locale {
  return locale === "sk" ? "en" : "sk";
}

/**
 * The absolute, canonical URL of a page — the single source every canonical,
 * hreflang entry, og:url and sitemap line is built from.
 *
 * `route` is the path without the locale prefix, e.g. "/sluzby/pneuservis".
 */
export function pageUrl(locale: Locale, route: string): string {
  const path = `/${locale}${route}`;
  return `${siteUrl}${TRAILING_SLASH ? `${path}/` : path}`;
}

/**
 * hreflang alternates for a route, plus x-default pointing at the Slovak version.
 * `route` is the path WITHOUT the locale prefix, e.g. "/sluzby/pneuservis".
 *
 * Every canonical here is self-referencing: the Slovak page points at itself,
 * the English page at itself, and each lists the other as its hreflang
 * alternate. That is what makes the pair a language cluster rather than two
 * pages competing for the same query, and it is why neither of them canonicals
 * to the bare domain — `/` is a redirect to `/sk/`, and a canonical that points
 * at a redirect is a signal a crawler has to resolve against itself.
 *
 * They come back empty only when the build is pointed at localhost, where a
 * canonical would name an address no crawler can reach.
 */
export function alternates(route: string) {
  if (siteUrlIsPlaceholder) return {};
  const languages: Record<string, string> = {};
  for (const locale of LOCALES) {
    languages[locale] = pageUrl(locale, route);
  }
  languages["x-default"] = pageUrl(DEFAULT_LOCALE, route);
  return {
    canonical: pageUrl(DEFAULT_LOCALE, route),
    languages,
  };
}

/** Canonical for a specific locale, used per-page so each locale is self-canonical. */
export function canonicalFor(locale: Locale, route: string) {
  if (siteUrlIsPlaceholder) return {};
  const alt = alternates(route);
  return { ...alt, canonical: pageUrl(locale, route) };
}

/** Open Graph locale codes; `og:locale` wants a territory, not a bare language. */
const OG_LOCALE: Record<Locale, string> = { sk: "sk_SK", en: "en_GB" };

/**
 * The SEO half of a page's metadata: canonical, hreflang, Open Graph.
 *
 * It exists so the three cannot drift apart. Open Graph carries its own URL and
 * its own title, and a page that sets one of them by hand eventually sets it to
 * something the canonical disagrees with; here `og:url` IS the canonical, by
 * construction, and the title is written once.
 */
export function pageSeo(
  locale: Locale,
  route: string,
  meta: { readonly title: string; readonly description: string },
  type: "website" | "article" = "website",
) {
  const canonical = siteUrlIsPlaceholder ? undefined : pageUrl(locale, route);
  return {
    title: meta.title,
    description: meta.description,
    alternates: canonicalFor(locale, route),
    openGraph: {
      title: meta.title,
      description: meta.description,
      siteName: site.legalName,
      locale: OG_LOCALE[locale],
      type,
      ...(canonical ? { url: canonical } : {}),
    },
  };
}
