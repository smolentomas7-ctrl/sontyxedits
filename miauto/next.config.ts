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

/**
 * Content Security Policy.
 *
 * `script-src` has to allow inline scripts: the App Router emits an inline
 * bootstrap on every page, and the alternative — a per-request nonce from
 * middleware — would make all 24 pages dynamic to protect a site that has no
 * user input rendered back into HTML. What this policy does buy is that no
 * script, style, frame or connection to a host not listed here can load at all,
 * which is the injection route that actually matters here.
 *
 * `https://www.google.com` appears twice on purpose: the contact page embeds the
 * map in an iframe (`frame-src`) and probes the same host before mounting it
 * (`connect-src`). Nothing else leaves the origin.
 */
const CSP = [
  "default-src 'self'",
  "base-uri 'self'",
  "object-src 'none'",
  "frame-ancestors 'self'",
  "form-action 'self'",
  "img-src 'self' data: blob:",
  "style-src 'self' 'unsafe-inline'",
  "font-src 'self' data:",
  // next dev needs eval; the production build does not.
  `script-src 'self' 'unsafe-inline'${process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : ""}`,
  "connect-src 'self' https://www.google.com",
  "frame-src https://www.google.com",
  "upgrade-insecure-requests",
].join("; ");

/** Switches off browser features this site never uses. */
const PERMISSIONS =
  "geolocation=(), camera=(), microphone=(), payment=(), usb=(), magnetometer=(), accelerometer=(), gyroscope=(), midi=(), browsing-topics=()";

const config: NextConfig = {
  reactStrictMode: true,
  // Apache serves a directory's index.html natively; it does not serve sk.html
  // at /sk. See TRAILING_SLASH in config/miauto.ts.
  trailingSlash: process.env.NEXT_PUBLIC_TRAILING_SLASH === "1",
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
        // Permanent, and kept in step with public/_redirects: the Slovak page
        // is the home page for good, so the bare domain should hand its signals
        // to /sk rather than stay indexed as an empty redirect of its own.
        async redirects() {
          return [{ source: "/", destination: "/sk", permanent: true }];
        },
        async headers() {
          return [
            {
              source: "/:path*",
              headers: [
                { key: "X-Content-Type-Options", value: "nosniff" },
                { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
                { key: "X-Frame-Options", value: "SAMEORIGIN" },
                { key: "Permissions-Policy", value: PERMISSIONS },
                { key: "Content-Security-Policy", value: CSP },
              ],
            },
          ];
        },
      }),
};

export default config;
