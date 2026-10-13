import type { MetadataRoute } from "next";
import { site } from "@/config/miauto";

export const dynamic = "force-static";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: `${site.legalName} — ${site.city}`,
    short_name: site.shortName,
    description: "Autoservis v Ružomberku. Diagnostika, elektronika, rozvody.",
    start_url: "/sk",
    display: "standalone",
    background_color: "#0B0D0E",
    theme_color: "#0B0D0E",
    lang: "sk",
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
    ],
  };
}
