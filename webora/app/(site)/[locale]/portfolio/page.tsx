import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Info } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { WorkShowcase } from "@/components/marketing/WorkShowcase";
import { mailtoHref } from "@/config/site";
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
          <p className="t-small flex max-w-[62ch] gap-2.5 rounded-xl border border-border bg-surface px-4 py-3 text-text-muted">
            <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
            {dict.portfolio.note}
          </p>
        </div>
      </Container>

      <Section className="border-t border-border pt-14 md:pt-20">
        <WorkShowcase locale={typedLocale} dict={dict} />

        <div className="mt-16 flex flex-col gap-3 sm:flex-row">
          <ButtonLink href={mailtoHref(dict.contact.mailSubject)} external size="lg">
            {dict.contact.emailCta}
          </ButtonLink>
          <ButtonLink href={`/${typedLocale}/features`} variant="secondary" size="lg">
            {dict.home.ctaSecondary}
          </ButtonLink>
        </div>
      </Section>
    </>
  );
}
