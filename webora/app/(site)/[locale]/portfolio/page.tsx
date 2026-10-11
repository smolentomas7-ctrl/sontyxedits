import type { Metadata } from "next";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { PortfolioGrid } from "@/components/marketing/PortfolioGrid";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { buildAlternates, ogImages } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.portfolio.metaTitle,
    description: dict.portfolio.metaDescription,
    alternates: buildAlternates("portfolio"),
    openGraph: {
      title: dict.portfolio.metaTitle,
      description: dict.portfolio.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function PortfolioPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  return (
    <>
      <Container>
        <div className="flex flex-col gap-6 py-20 md:py-28">
          <h1 className="t-h1 max-w-[14ch] text-text">{dict.portfolio.heroTitle}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.portfolio.heroSubtitle}</p>
          <p className="t-small max-w-[60ch] rounded-lg border border-border bg-surface px-4 py-3 text-text-muted">
            {dict.portfolio.note}
          </p>
        </div>
      </Container>

      <Section className="border-t border-border pt-14 md:pt-20">
        {/* useSearchParams needs a Suspense boundary during prerender. */}
        <Suspense fallback={<div className="h-10" />}>
          <PortfolioGrid locale={typedLocale} dict={dict} />
        </Suspense>

        <div className="mt-16 flex flex-col gap-3 sm:flex-row">
          <ButtonLink href={`/${typedLocale}/contact`}>{dict.common.getQuote}</ButtonLink>
          <ButtonLink href={`/${typedLocale}/pricing`} variant="secondary">
            {dict.home.pricingLink}
          </ButtonLink>
        </div>
      </Section>
    </>
  );
}
