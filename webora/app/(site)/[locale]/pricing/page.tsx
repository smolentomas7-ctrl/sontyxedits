import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Check } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Section, SectionHeading } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { Accordion } from "@/components/ui/Accordion";
import { PriceCalculator } from "@/components/marketing/PriceCalculator";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { buildAlternates, ogImages } from "@/lib/seo";
import { cn } from "@/lib/utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.pricing.metaTitle,
    description: dict.pricing.metaDescription,
    alternates: buildAlternates("pricing"),
    openGraph: {
      title: dict.pricing.metaTitle,
      description: dict.pricing.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function PricingPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  // FAQPage structured data, built from the same copy the page renders.
  const faqLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: dict.pricing.faq.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: { "@type": "Answer", text: item.a },
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqLd) }}
      />

      <Container>
        <div className="flex flex-col gap-6 py-20 md:py-28">
          <h1 className="t-h1 max-w-[12ch] text-text">{dict.pricing.heroTitle}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.pricing.heroSubtitle}</p>
        </div>
      </Container>

      {/* ---------- a) PACKAGES ---------- */}
      <Section className="border-t border-border pt-14 md:pt-20" ariaLabelledBy="packages-heading">
        <h2 id="packages-heading" className="sr-only">
          {dict.pricing.heroTitle}
        </h2>

        <ul className="grid gap-6 lg:grid-cols-3">
          {dict.pricing.packages.map((pkg, index) => {
            const popular = pkg.id === "business";
            return (
              <Reveal as="li" key={pkg.id} delay={index * 60} className="flex">
                <Card
                  interactive={false}
                  className={cn(
                    "relative flex w-full flex-col gap-5 p-7",
                    popular && "border-accent/45",
                  )}
                >
                  {popular ? (
                    <span className="absolute -top-3 left-7 rounded-full bg-accent px-3 py-1 text-[12px] font-medium text-[#06120D]">
                      {dict.pricing.popular}
                    </span>
                  ) : null}

                  <div>
                    <h3 className="t-h3 text-text">{pkg.name}</h3>
                    <p className="mt-2 font-[family-name:var(--font-space-grotesk)] text-3xl font-bold tracking-[-0.03em] text-accent">
                      {pkg.price}
                    </p>
                  </div>

                  <p className="text-[15px] text-text-muted">{pkg.summary}</p>

                  <ul className="flex flex-1 flex-col gap-3">
                    {pkg.features.map((feature) => (
                      <li
                        key={feature}
                        className="flex items-start gap-2.5 text-[15px] text-text-muted"
                      >
                        <Check
                          aria-hidden="true"
                          strokeWidth={1.5}
                          className="mt-0.5 size-4 shrink-0 text-accent"
                        />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <p className="t-small text-text-muted">{pkg.delivery}</p>

                  <ButtonLink
                    href={`/${typedLocale}/contact?package=${pkg.id}`}
                    variant={popular ? "primary" : "secondary"}
                    className="w-full"
                  >
                    {dict.pricing.choosePackage}
                  </ButtonLink>
                </Card>
              </Reveal>
            );
          })}
        </ul>
      </Section>

      {/* ---------- b) CALCULATOR ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="calc-heading">
        <SectionHeading
          id="calc-heading"
          title={dict.pricing.calc.title}
          subtitle={dict.pricing.calc.subtitle}
          className="mb-12"
        />
        <PriceCalculator locale={typedLocale} dict={dict} />
      </Section>

      {/* ---------- c) FAQ ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="faq-heading">
        <SectionHeading id="faq-heading" title={dict.pricing.faqTitle} className="mb-10" />
        <Accordion items={dict.pricing.faq} />
      </Section>

      {/* ---------- d) CTA BAND ---------- */}
      <Section className="pb-24 pt-0 md:pb-32">
        <Reveal>
          <div className="rounded-3xl border border-accent/20 bg-accent-soft px-7 py-14 text-center md:px-16 md:py-20">
            <h2 className="t-h2 mx-auto max-w-[18ch] text-balance text-text">
              {dict.pricing.ctaTitle}
            </h2>
            <p className="mx-auto mt-5 max-w-[52ch] text-text-muted">{dict.pricing.ctaBody}</p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href={`/${typedLocale}/contact`}>{dict.pricing.ctaButton}</ButtonLink>
              <ButtonLink href={`/${typedLocale}/services`} variant="secondary">
                {dict.home.servicesLink}
              </ButtonLink>
            </div>
          </div>
        </Reveal>
      </Section>
    </>
  );
}
