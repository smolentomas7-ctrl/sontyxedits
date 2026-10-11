import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { Space_Grotesk, Inter } from "next/font/google";
import "@/app/globals.css";
import { Header } from "@/components/marketing/Header";
import { Footer } from "@/components/marketing/Footer";
import { ChatWidget } from "@/components/marketing/ChatWidget";
import { getDictionary, isLocale, LOCALES, type Locale } from "@/content/i18n";
import { siteConfig } from "@/config/site";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin", "latin-ext"],
  weight: ["500", "700"],
  variable: "--font-space-grotesk",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    metadataBase: new URL(siteConfig.url),
    title: { default: dict.meta.siteTitle, template: `%s — ${siteConfig.name}` },
    description: dict.meta.siteDescription,
    icons: {
      icon: [
        { url: "/favicon.ico", sizes: "any" },
        { url: "/icon.png", type: "image/png", sizes: "512x512" },
      ],
      apple: "/apple-icon.png",
    },
    openGraph: {
      images: [{ url: `${siteConfig.url}/${locale}/og`, width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      images: [`${siteConfig.url}/${locale}/og`],
    },
  };
}

export default async function SiteLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();

  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  return (
    <html lang={typedLocale} className={`${spaceGrotesk.variable} ${inter.variable}`}>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[200] focus:rounded-lg focus:bg-accent focus:px-4 focus:py-2 focus:text-[#06120D]"
        >
          {dict.nav.skipToContent}
        </a>
        <Header locale={typedLocale} dict={dict} />
        <main id="main" className="pt-16 md:pt-20">
          {children}
        </main>
        <Footer locale={typedLocale} dict={dict} />
        <ChatWidget locale={typedLocale} dict={dict} />
      </body>
    </html>
  );
}
