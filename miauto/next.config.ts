import type { NextConfig } from "next";

/**
 * STATIC_EXPORT=1 produces a folder of plain files in `out/`, for Netlify's
 * drag-and-drop deploy, which publishes what you give it and runs no build.
 *
 * That mode has a real cost: a static site has no server, so `app/api/chat`
 * cannot exist and the assistant runs its scripted tier in the browser instead.
 * The enquiry form is unaffected — Netlify Forms is handled by Netlify's own
 * infrastructure, not by a function.
 *
 * The normal build (Git deploy, or `netlify deploy` with the Next.js runtime
 * adapter) keeps the route and can run the grounded assistant.
 */
const STATIC = process.env.STATIC_EXPORT === "1";

const config: NextConfig = {
  reactStrictMode: true,
  ...(STATIC
    ? {
        output: "export" as const,
        // Next's image optimizer is a server feature; without it the files are
        // served exactly as scripts/process-images.py wrote them, which they
        // were already sized and compressed for.
        images: { unoptimized: true },
      }
    : {
        images: { formats: ["image/avif", "image/webp"] as const },
        // redirects() and headers() need a server. In static mode the same two
        // jobs are done by public/_redirects and public/_headers.
        async redirects() {
          return [{ source: "/", destination: "/sk", permanent: false }];
        },
        async headers() {
          return [
            {
              source: "/:path*",
              headers: [
                { key: "X-Content-Type-Options", value: "nosniff" },
                { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
                { key: "X-Frame-Options", value: "SAMEORIGIN" },
              ],
            },
          ];
        },
      }),
};

export default config;
