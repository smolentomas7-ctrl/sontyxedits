import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";
import { LOCALES } from "@/content/i18n";
import { sortedPosts } from "@/content/blog/posts";
import { projects } from "@/content/projects";

/**
 * Marketing routes in both locales. /demo/* is deliberately excluded — the
 * demos are noindex and should not compete with the real pages.
 */
/**
 * Pre-rendered at build time. `force-static` is required by
 * `output: "export"` and is correct for the server build too — this file's
 * contents only change when the route list or post list changes.
 */
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticPaths = ["", "services", "portfolio", "features", "blog", "about", "contact"];
  const casePaths = projects.map((project) => `portfolio/${project.slug}`);
  const postPaths = sortedPosts().map((post) => `blog/${post.slug}`);
  const allPaths = [...staticPaths, ...casePaths, ...postPaths, "legal/privacy"];

  const entries: MetadataRoute.Sitemap = [];

  for (const locale of LOCALES) {
    for (const path of allPaths) {
      const suffix = path ? `/${path}` : "";
      entries.push({
        url: `${siteConfig.url}/${locale}${suffix}`,
        lastModified: new Date(),
        changeFrequency: path.startsWith("blog/") ? "yearly" : "monthly",
        priority:
          path === ""
            ? 1
            : path.startsWith("blog/") || path.startsWith("legal/")
              ? 0.5
              : 0.8,
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
