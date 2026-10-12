import type { Metadata, Viewport } from "next";
import { Archivo, Inter } from "next/font/google";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { getContent, isLocale, LOCALES } from "@/content";
import { siteUrl } from "@/config/miauto";
import { autoRepairJsonLd } from "@/lib/jsonld";
import { Nav } from "@/components/layout/Nav";
import { Footer } from "@/components/layout/Footer";
import { MobileCallBar } from "@/components/layout/MobileCallBar";
import { ChatLauncher } from "@/components/chat/ChatLauncher";
import "../globals.css";

/**
 * Self-hosted through next/font: the files are downloaded at build time and
 * served from this origin, so the browser never makes a runtime request to a
 * third-party font CDN. Only the weights actually used are requested.
 */
const archivo = Archivo({
  subsets: ["latin", "latin-ext"],
  weight: ["600", "700"],
  variable: "--font-archivo",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "M.I.Auto s.r.o.",
  description: "Autoservis v Ružomberku.",
};

export const viewport: Viewport = {
  themeColor: "#0B0D0E",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

/**
 * This is the root layout, and it lives inside [locale] on purpose.
 *
 * A layout above the dynamic segment cannot see which locale is rendering, so
 * <html lang> would have to be hardcoded or left empty. A lang attribute on an
 * inner <div> is not what a screen reader reads for the document language, so
 * the <html> element itself has to carry it.
 */
export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const t = getContent(locale);

  return (
    <html
      lang={t.htmlLang}
      className={`${archivo.variable} ${inter.variable}`}
      suppressHydrationWarning
    >
      <body>
        <script
          type="application/ld+json"
          // Built only from config/miauto.ts: no ratings, no reviews, no price range.
          dangerouslySetInnerHTML={{ __html: JSON.stringify(autoRepairJsonLd(locale)) }}
        />

        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-[var(--radius-control)] focus:bg-[var(--accent)] focus:px-5 focus:py-3 focus:font-semibold focus:text-[color:var(--accent-ink)]"
        >
          {t.common.skipToContent}
        </a>

        <Nav locale={locale} t={t} />
        <main id="main">{children}</main>
        <Footer locale={locale} t={t} />

        {/* Below 768px the call bar occupies the bottom edge; the chat launcher
            is offset above it, so neither can cover the other. */}
        <MobileCallBar t={t} />
        <ChatLauncher locale={locale} t={t} />
        <div className="h-[76px] md:hidden" aria-hidden="true" />
      </body>
    </html>
  );
}
