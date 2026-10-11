import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

/**
 * Pre-rendered at build time. `force-static` is required by
 * `output: "export"` and is correct for the server build too — this file's
 * contents only change when the route list or post list changes.
 */
export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      // The demo sites are illustrative only and must not be indexed.
      disallow: ["/demo/"],
    },
    sitemap: `${siteConfig.url}/sitemap.xml`,
  };
}
