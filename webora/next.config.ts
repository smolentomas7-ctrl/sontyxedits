import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      // Stock fallback source. Every slot currently resolves to a local file in
      // public/assets, but config/images.ts may point any slot at Unsplash.
      { protocol: "https", hostname: "images.unsplash.com" },
    ],
  },
  async redirects() {
    return [{ source: "/", destination: "/sk", permanent: false }];
  },
};

export default nextConfig;
