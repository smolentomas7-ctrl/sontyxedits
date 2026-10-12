import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  // No `output: "export"`. The chat route is a server route handler; a static
  // export would silently drop it and the assistant would 404 in production.
  images: {
    formats: ["image/avif", "image/webp"],
  },
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
};

export default config;
