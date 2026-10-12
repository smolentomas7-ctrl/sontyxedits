import type { MetadataRoute } from "next";
import { siteUrl } from "@/config/miauto";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      // Netlify's form-registration page, which is not content.
      disallow: ["/__forms.html"],
    },
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
