import type { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";

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
