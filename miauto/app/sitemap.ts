import type { MetadataRoute } from "next";
import { LOCALES, SERVICE_SLUGS } from "@/content/types";
import { ROUTES } from "@/lib/i18n";
import { siteUrl } from "@/config/miauto";

/** All 24 routes: 12 per locale, both locales, each with its hreflang alternates. */
export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    { path: ROUTES.home, priority: 1 },
    { path: ROUTES.services, priority: 0.9 },
    ...SERVICE_SLUGS.map((slug) => ({ path: `${ROUTES.services}/${slug}`, priority: 0.8 })),
    { path: ROUTES.about, priority: 0.6 },
    { path: ROUTES.contact, priority: 0.9 },
    { path: ROUTES.privacy, priority: 0.2 },
  ];

  const now = new Date();

  return LOCALES.flatMap((locale) =>
    routes.map((route) => ({
      url: `${siteUrl}/${locale}${route.path}`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: route.priority,
      alternates: {
        languages: Object.fromEntries([
          ...LOCALES.map((alt) => [alt, `${siteUrl}/${alt}${route.path}`]),
          ["x-default", `${siteUrl}/sk${route.path}`],
        ]),
      },
    })),
  );
}
