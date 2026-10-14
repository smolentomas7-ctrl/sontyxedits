import { DEFAULT_LOCALE, LOCALES, type Locale } from "@/content/types";
import { siteUrl, siteUrlIsPlaceholder } from "@/config/miauto";

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
 * hreflang alternates for a route, plus x-default pointing at the Slovak version.
 * `route` is the path WITHOUT the locale prefix, e.g. "/sluzby/pneuservis".
 *
 * Until the real domain is set as NEXT_PUBLIC_SITE_URL these come back empty, on
 * purpose. A canonical is an absolute URL or nothing, and a build that has not
 * been told its address would otherwise publish `http://localhost:3000/...` as
 * the one true URL of every page — which tells a crawler that the page it is
 * reading lives somewhere it cannot reach. No canonical at all is correct
 * instead: the crawler keeps the URL it fetched. Set the variable and every
 * canonical, hreflang and x-default appears.
 */
export function alternates(route: string) {
  if (siteUrlIsPlaceholder) return {};
  const languages: Record<string, string> = {};
  for (const locale of LOCALES) {
    languages[locale] = `${siteUrl}/${locale}${route}`;
  }
  languages["x-default"] = `${siteUrl}/${DEFAULT_LOCALE}${route}`;
  return {
    canonical: `${siteUrl}/${DEFAULT_LOCALE}${route}`,
    languages,
  };
}

/** Canonical for a specific locale, used per-page so each locale is self-canonical. */
export function canonicalFor(locale: Locale, route: string) {
  if (siteUrlIsPlaceholder) return {};
  const alt = alternates(route);
  return { ...alt, canonical: `${siteUrl}/${locale}${route}` };
}
