import type { MetadataRoute } from "next";
import { siteUrl, siteUrlIsPlaceholder } from "@/config/miauto";
import { FORM_ENDPOINT } from "@/lib/forms";

/** Both builds emit this as a file; nothing about it varies per request. */
export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      // Netlify's form-registration page, which is not content. It only exists
      // in a build that posts to it; a build for another host has no such file
      // and no reason to name one.
      ...(FORM_ENDPOINT === "/__forms.html" ? { disallow: ["/__forms.html"] } : {}),
    },
    // Both of these are absolute by definition, so neither is emitted until the
    // real domain is known — pointing a crawler at localhost is worse than
    // saying nothing, and it will find /sitemap.xml at the usual place anyway.
    ...(siteUrlIsPlaceholder
      ? {}
      : { sitemap: `${siteUrl}/sitemap.xml`, host: siteUrl }),
  };
}
