import type { NextConfig } from "next";

/**
 * Set STATIC_EXPORT=1 to produce a fully static `out/` directory for hosts
 * that just serve files (Netlify drag-and-drop, GitHub Pages, any CDN).
 *
 * The default build — no env var — targets Vercel and keeps the Next.js
 * image optimizer and the `/` redirect handled by the server.
 */
const isStaticExport = process.env.STATIC_EXPORT === "1";

const nextConfig: NextConfig = {
  ...(isStaticExport
    ? {
        output: "export" as const,
        // A static host has no Next.js image optimizer, so images must be
        // emitted as-is. They are already resized and recompressed on disk.
        images: { unoptimized: true },
        // Emit /sk/index.html rather than /sk.html so plain file servers
        // resolve directory-style URLs without extra rewrite rules.
        trailingSlash: true,
      }
    : {
        images: {
          remotePatterns: [
            // Stock fallback source. Every slot currently resolves to a local
            // file in public/assets, but config/images.ts may point any slot
            // at Unsplash.
            { protocol: "https", hostname: "images.unsplash.com" },
          ],
        },
        // redirects() requires a server; the static build ships a Netlify
        // _redirects file instead (see public/_redirects).
        async redirects() {
          return [{ source: "/", destination: "/sk", permanent: false }];
        },
      }),
};

export default nextConfig;
