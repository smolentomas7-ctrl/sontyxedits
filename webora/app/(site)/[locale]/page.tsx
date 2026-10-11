import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  Smartphone,
  Gauge,
  Search,
  GraduationCap,
  ArrowRight,
  FileText,
  Layout,
  ShoppingCart,
} from "lucide-react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Container } from "@/components/ui/Container";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { DemoShowcase } from "@/components/marketing/DemoShowcase";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { siteConfig } from "@/config/site";
import { buildAlternates, ogImages } from "@/lib/seo";

const TRUST_ICONS = [Smartphone, Gauge, Search, GraduationCap];
const SERVICE_ICONS = [FileText, Layout, ShoppingCart];

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.home.metaTitle,
    description: dict.home.metaDescription,
    alternates: buildAlternates(""),
    openGraph: {
      title: dict.home.metaTitle,
      description: dict.home.metaDescription,
      url: `${siteConfig.url}/${locale}`,
      siteName: siteConfig.name,
      locale: locale === "sk" ? "sk_SK" : "en_GB",
      type: "website",
      images: ogImages(locale),
    },
    twitter: {
      card: "summary_large_image",
      title: dict.home.metaTitle,
      description: dict.home.metaDescription,
    },
  };
}

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  // Organization JSON-LD, built only from config/site.ts. No invented ratings,
  // review counts or awards.
  const organizationLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: siteConfig.name,
    url: `${siteConfig.url}/${typedLocale}`,
    description: dict.meta.siteDescription,
    email: siteConfig.email,
    telephone: siteConfig.phone,
    address: { "@type": "PostalAddress", addressLocality: siteConfig.city },
  };

  const servicesTeaser = dict.services.items.slice(0, 3);

  return (
    <>
      <script
        type="application/ld+json"
        // Static, locally built object — no user input reaches this string.
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationLd) }}
      />

      {/* ---------- a) HERO ---------- */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 -z-10 flex items-start justify-center"
        >
          <div
            className="hero-glow mt-[-12rem] size-[46rem] rounded-full opacity-70 blur-[120px]"
            style={{
              background:
                "radial-gradient(circle, rgba(91,141,255,0.22) 0%, rgba(91,141,255,0.07) 42%, transparent 70%)",
            }}
          />
        </div>

        <Container>
          <div className="flex flex-col items-start gap-7 py-24 md:py-36">
            <Reveal>
              <span className="t-small inline-flex rounded-full border border-border bg-surface px-3 py-1 font-medium uppercase tracking-[0.16em] text-accent">
                {dict.home.heroEyebrow}
              </span>
            </Reveal>

            <Reveal delay={60}>
              <h1 className="t-h1 max-w-[16ch] text-balance text-text">{dict.home.heroTitle}</h1>
            </Reveal>

            <Reveal delay={120}>
              <p className="t-prose text-lg text-text-muted">{dict.home.heroSubtitle}</p>
            </Reveal>

            <Reveal delay={180}>
              <div className="flex flex-col gap-3 sm:flex-row">
                <ButtonLink href={`/${typedLocale}/contact`}>{dict.common.getQuote}</ButtonLink>
                <ButtonLink href={`/${typedLocale}/portfolio`} variant="secondary">
                  {dict.common.seeDemos}
                </ButtonLink>
              </div>
            </Reveal>
          </div>
        </Container>
      </section>

      {/* ---------- b) TRUST STRIP ---------- */}
      <Section className="border-y border-border py-16 md:py-20" ariaLabelledBy="trust-heading">
        <h2 id="trust-heading" className="sr-only">
          {dict.home.trustTitle}
        </h2>
        <ul className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {dict.home.trust.map((item, index) => {
            const Icon = TRUST_ICONS[index] ?? Smartphone;
            return (
              <Reveal as="li" key={item.title} delay={index * 60} className="flex flex-col gap-3">
                <Icon aria-hidden="true" strokeWidth={1.5} className="size-6 text-accent" />
                <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-medium text-text">
                  {item.title}
                </h3>
                <p className="t-small text-text-muted">{item.body}</p>
              </Reveal>
            );
          })}
        </ul>
      </Section>

      {/* ---------- c) LIVE DEMO SHOWCASE ---------- */}
      <Section ariaLabelledBy="demos-heading">
        <SectionHeading
          id="demos-heading"
          eyebrow={dict.home.demosEyebrow}
          title={dict.home.demosTitle}
          subtitle={dict.home.demosSubtitle}
          className="mb-14"
        />
        <DemoShowcase locale={typedLocale} dict={dict} />
      </Section>

      {/* ---------- d) SERVICES SUMMARY ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="services-heading">
        <SectionHeading
          id="services-heading"
          eyebrow={dict.home.servicesEyebrow}
          title={dict.home.servicesTitle}
          subtitle={dict.home.servicesSubtitle}
          className="mb-14"
        />

        <ul className="grid gap-6 md:grid-cols-3">
          {servicesTeaser.map((service, index) => {
            const Icon = SERVICE_ICONS[index] ?? FileText;
            return (
              <Reveal as="li" key={service.slug} delay={index * 60} className="flex">
                <Card className="flex w-full flex-col gap-4 p-7">
                  <Icon aria-hidden="true" strokeWidth={1.5} className="size-6 text-accent" />
                  <h3 className="t-h3 text-text">{service.name}</h3>
                  <p className="flex-1 text-[15px] text-text-muted">{service.what}</p>
                  <p className="t-small text-text-muted">
                    {dict.common.from}{" "}
                    <span className="font-medium text-text">{service.price}</span>
                  </p>
                  <Link
                    href={`/${typedLocale}/services#${service.slug}`}
                    className="inline-flex items-center gap-1.5 text-[14px] font-medium text-accent hover:text-accent-hover"
                  >
                    {dict.common.readMore}
                    <ArrowRight aria-hidden="true" strokeWidth={1.5} className="size-4" />
                  </Link>
                </Card>
              </Reveal>
            );
          })}
        </ul>

        <div className="mt-10">
          <ButtonLink href={`/${typedLocale}/services`} variant="secondary">
            {dict.home.servicesLink}
          </ButtonLink>
        </div>
      </Section>

      {/* ---------- e) PROCESS ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="process-heading">
        <SectionHeading
          id="process-heading"
          eyebrow={dict.home.processEyebrow}
          title={dict.home.processTitle}
          className="mb-14"
        />

        <ol className="grid gap-x-6 gap-y-10 md:grid-cols-4">
          {dict.home.process.map((step, index) => (
            <Reveal as="li" key={step.title} delay={index * 60} className="relative flex gap-4 md:block">
              {/* Vertical connector on mobile, horizontal rule on desktop. */}
              <div aria-hidden="true" className="flex flex-col items-center md:block">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent-soft font-[family-name:var(--font-space-grotesk)] text-sm font-bold text-accent">
                  {index + 1}
                </span>
                {index < dict.home.process.length - 1 ? (
                  <span className="mt-2 w-px flex-1 bg-border md:hidden" />
                ) : null}
              </div>

              <div className="pb-2 md:mt-5">
                <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-medium text-text">
                  {step.title}
                </h3>
                <p className="mt-2 text-[15px] text-text-muted">{step.body}</p>
              </div>
            </Reveal>
          ))}
        </ol>
      </Section>

      {/* ---------- f) PRICING TEASER ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="pricing-heading">
        <SectionHeading
          id="pricing-heading"
          eyebrow={dict.home.pricingEyebrow}
          title={dict.home.pricingTitle}
          subtitle={dict.home.pricingSubtitle}
          className="mb-14"
        />

        <ul className="grid gap-6 md:grid-cols-3">
          {dict.pricing.packages.map((pkg, index) => (
            <Reveal as="li" key={pkg.id} delay={index * 60} className="flex">
              <Card className="flex w-full flex-col gap-3 p-7">
                <h3 className="t-h3 text-text">{pkg.name}</h3>
                <p className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold text-accent">
                  {pkg.price}
                </p>
                <p className="flex-1 text-[15px] text-text-muted">{pkg.summary}</p>
                <p className="t-small text-text-muted">{pkg.delivery}</p>
              </Card>
            </Reveal>
          ))}
        </ul>

        <div className="mt-10">
          <ButtonLink href={`/${typedLocale}/pricing`} variant="secondary">
            {dict.home.pricingLink}
          </ButtonLink>
        </div>
      </Section>

      {/* ---------- g) FINAL CTA BAND ---------- */}
      <Section className="pb-24 pt-0 md:pb-32">
        <Reveal>
          <div className="rounded-3xl border border-accent/20 bg-accent-soft px-7 py-14 text-center md:px-16 md:py-20">
            <h2 className="t-h2 mx-auto max-w-[18ch] text-balance text-text">
              {dict.home.ctaTitle}
            </h2>
            <p className="mx-auto mt-5 max-w-[52ch] text-text-muted">{dict.home.ctaBody}</p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href={`/${typedLocale}/contact`}>{dict.home.ctaButton}</ButtonLink>
              <ButtonLink href={`/${typedLocale}/pricing`} variant="secondary">
                {dict.home.pricingLink}
              </ButtonLink>
            </div>
          </div>
        </Reveal>
      </Section>
    </>
  );
}
