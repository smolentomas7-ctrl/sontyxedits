import type { Metadata } from "next";
import "@/app/globals.css";

/**
 * Root layout for every demo site. Each demo sets its own fonts and palette
 * inside its own subtree, so this shell stays deliberately bare.
 *
 * All demo routes are noindex — they are illustrative mini-sites for
 * fictional businesses and must never compete with the real pages.
 */
export const metadata: Metadata = {
  robots: { index: false, follow: false, nocache: true },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon.png", type: "image/png", sizes: "512x512" },
    ],
    apple: "/apple-icon.png",
  },
};

export default function DemoRootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="sk">
      <body>{children}</body>
    </html>
  );
}
