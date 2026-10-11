import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";
import { LOCALES } from "@/content/i18n";
import { sortedPosts } from "@/content/blog/posts";

/**
 * Marketing routes in both locales. /demo/* is deliberately excluded — the
 * demos are noindex and should not compete with the real pages.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const staticPaths = ["", "services", "portfolio", "pricing", "blog", "about", "contact"];
  const postPaths = sortedPosts().map((post) => `blog/${post.slug}`);
  const allPaths = [...staticPaths, ...postPaths];

  const entries: MetadataRoute.Sitemap = [];

  for (const locale of LOCALES) {
    for (const path of allPaths) {
      const suffix = path ? `/${path}` : "";
      entries.push({
        url: `${siteConfig.url}/${locale}${suffix}`,
        lastModified: new Date(),
        changeFrequency: path.startsWith("blog/") ? "yearly" : "monthly",
        priority: path === "" ? 1 : path.startsWith("blog/") ? 0.5 : 0.8,
        alternates: {
          languages: Object.fromEntries(
            LOCALES.map((l) => [l, `${siteConfig.url}/${l}${suffix}`]),
          ),
        },
      });
    }
  }

  return entries;
}
