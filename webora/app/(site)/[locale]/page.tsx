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
  Check,
} from "lucide-react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Container } from "@/components/ui/Container";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { Accordion } from "@/components/ui/Accordion";
import { WorkShowcase } from "@/components/marketing/WorkShowcase";
import { Testimonials } from "@/components/marketing/Testimonials";
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

  // Organization data, built only from config/site.ts. No invented ratings,
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

  const faqLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: dict.faq.items.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: { "@type": "Answer", text: item.a },
    })),
  };

  const servicesTeaser = dict.services.items.slice(0, 3);

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqLd) }}
      />

      {/* ---------- 1. HERO ---------- */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 -z-10 flex items-start justify-center"
        >
          <div
            className="hero-glow mt-[-14rem] size-[48rem] rounded-full opacity-80 blur-[130px]"
            style={{
              background:
                "radial-gradient(circle, rgba(91,141,255,0.24) 0%, rgba(91,141,255,0.07) 42%, transparent 70%)",
            }}
          />
        </div>

        <Container>
          <div className="flex flex-col items-start gap-7 py-24 md:py-36">
            <Reveal>
              <span className="t-small inline-flex rounded-full border border-border bg-surface/70 px-3.5 py-1.5 font-medium uppercase tracking-[0.16em] text-accent backdrop-blur-sm">
                {dict.home.heroEyebrow}
              </span>
            </Reveal>

            <Reveal delay={70}>
              <h1 className="t-h1 max-w-[17ch] text-balance text-text">
                {dict.home.heroTitle}{" "}
                <span className="text-accent">{dict.home.heroTitleAccent}</span>
              </h1>
            </Reveal>

            <Reveal delay={140}>
              <p className="t-prose text-lg text-text-muted">{dict.home.heroSubtitle}</p>
            </Reveal>

            <Reveal delay={210}>
              <div className="flex flex-col gap-3 sm:flex-row">
                <ButtonLink href={`/${typedLocale}/contact`} size="lg">
                  {dict.home.heroPrimary}
                </ButtonLink>
                <ButtonLink href={`/${typedLocale}/portfolio`} variant="secondary" size="lg">
                  {dict.home.heroSecondary}
                </ButtonLink>
              </div>
            </Reveal>

            <Reveal delay={280}>
              <dl className="mt-6 flex flex-wrap gap-x-12 gap-y-6">
                {dict.home.heroStats.map((stat) => (
                  <div key={stat.label}>
                    <dt className="sr-only">{stat.label}</dt>
                    <dd>
                      <span className="block font-[family-name:var(--font-space-grotesk)] text-3xl font-bold tracking-[-0.03em] text-text">
                        {stat.value}
                      </span>
                      <span className="t-small mt-1 block max-w-[20ch] text-text-muted">
                        {stat.label}
                      </span>
                    </dd>
                  </div>
                ))}
              </dl>
            </Reveal>
          </div>
        </Container>
      </section>

      {/* ---------- 2. TRUST STRIP ---------- */}
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

      {/* ---------- 3. PORTFOLIO — three examples ---------- */}
      <Section ariaLabelledBy="work-heading">
        <SectionHeading
          id="work-heading"
          eyebrow={dict.home.workEyebrow}
          title={dict.home.workTitle}
          subtitle={dict.home.workSubtitle}
          className="mb-14"
        />
        <WorkShowcase locale={typedLocale} dict={dict} />
        <div className="mt-10">
          <ButtonLink href={`/${typedLocale}/portfolio`} variant="secondary">
            {dict.common.seeWork}
          </ButtonLink>
        </div>
      </Section>

      {/* ---------- 4. SERVICES ---------- */}
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
                  <Link
                    href={`/${typedLocale}/services#${service.slug}`}
                    className="group/l inline-flex items-center gap-1.5 text-[14px] font-medium text-accent hover:text-accent-hover"
                  >
                    {dict.common.readMore}
                    <ArrowRight
                      aria-hidden="true"
                      strokeWidth={1.5}
                      className="size-4 transition-transform duration-200 group-hover/l:translate-x-0.5 motion-reduce:transition-none"
                    />
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

      {/* ---------- 5. CAPABILITIES teaser ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="features-heading">
        <SectionHeading
          id="features-heading"
          eyebrow={dict.features.eyebrow}
          title={dict.features.title}
          subtitle={dict.features.subtitle}
          className="mb-12"
        />
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {dict.features.groups.map((group, index) => (
            <Reveal as="li" key={group.id} delay={index * 40}>
              <Link
                href={`/${typedLocale}/features#${group.id}`}
                className="flex h-full items-start gap-3 rounded-xl border border-border bg-surface px-5 py-4 transition-colors duration-200 hover:border-accent/35 hover:bg-surface-hover"
              >
                <Check
                  aria-hidden="true"
                  strokeWidth={1.5}
                  className="mt-0.5 size-4 shrink-0 text-accent"
                />
                <span>
                  <span className="block text-[15px] font-medium text-text">{group.title}</span>
                  <span className="t-small mt-0.5 block text-text-muted">{group.summary}</span>
                </span>
              </Link>
            </Reveal>
          ))}
        </ul>
        <div className="mt-10">
          <ButtonLink href={`/${typedLocale}/features`} variant="secondary">
            {dict.home.ctaSecondary}
          </ButtonLink>
        </div>
      </Section>

      {/* ---------- 6. PROCESS ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="process-heading">
        <SectionHeading
          id="process-heading"
          eyebrow={dict.home.processEyebrow}
          title={dict.home.processTitle}
          subtitle={dict.home.processSubtitle}
          className="mb-14"
        />

        <ol className="grid gap-x-6 gap-y-10 md:grid-cols-5">
          {dict.home.process.map((step, index) => (
            <Reveal
              as="li"
              key={step.title}
              delay={index * 60}
              className="relative flex gap-4 md:block"
            >
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

      {/* ---------- 7. TESTIMONIALS (demonstration content) ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="testimonials-heading">
        <SectionHeading
          id="testimonials-heading"
          eyebrow={dict.testimonials.eyebrow}
          title={dict.testimonials.title}
          subtitle={dict.testimonials.subtitle}
          className="mb-10"
        />
        <Testimonials dict={dict} />
      </Section>

      {/* ---------- 8. INDIVIDUAL PRICING ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="pricing-heading">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
          <Reveal>
            <span className="t-small font-medium uppercase tracking-[0.18em] text-accent">
              {dict.pricing.eyebrow}
            </span>
            <h2 id="pricing-heading" className="t-h2 mt-4 max-w-[18ch] text-text">
              {dict.pricing.title}
            </h2>
            <div className="mt-6 flex flex-col gap-4">
              {dict.pricing.body.map((paragraph) => (
                <p key={paragraph.slice(0, 28)} className="t-prose text-text-muted">
                  {paragraph}
                </p>
              ))}
            </div>
            <p className="mt-6 rounded-xl border border-border bg-surface px-5 py-4 text-[14px] leading-relaxed text-text-muted">
              {dict.pricing.note}
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <ButtonLink href={`/${typedLocale}/contact`} size="lg">
                {dict.pricing.ctaPrimary}
              </ButtonLink>
            </div>
          </Reveal>

          <Reveal delay={80}>
            <h3 className="t-small mb-5 font-medium uppercase tracking-[0.12em] text-text">
              {dict.pricing.factorsTitle}
            </h3>
            <ul className="grid gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-2">
              {dict.pricing.factors.map((factor) => (
                <li key={factor.title} className="bg-surface p-6">
                  <h4 className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-medium text-text">
                    {factor.title}
                  </h4>
                  <p className="t-small mt-2 text-text-muted">{factor.body}</p>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </Section>

      {/* ---------- 9. FAQ ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="faq-heading">
        <SectionHeading
          id="faq-heading"
          eyebrow={dict.faq.eyebrow}
          title={dict.faq.title}
          subtitle={dict.faq.subtitle}
          className="mb-10"
        />
        <Accordion items={dict.faq.items} />
      </Section>

      {/* ---------- 10. FINAL CTA ---------- */}
      <Section className="pb-24 pt-0 md:pb-32">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-accent/20 bg-accent-soft px-7 py-14 text-center md:px-16 md:py-20">
            <h2 className="t-h2 mx-auto max-w-[18ch] text-balance text-text">
              {dict.home.ctaTitle}
            </h2>
            <p className="mx-auto mt-5 max-w-[52ch] text-text-muted">{dict.home.ctaBody}</p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href={`/${typedLocale}/contact`} size="lg">
                {dict.home.ctaButton}
              </ButtonLink>
              <ButtonLink href={`/${typedLocale}/features`} variant="secondary" size="lg">
                {dict.home.ctaSecondary}
              </ButtonLink>
            </div>
          </div>
        </Reveal>
      </Section>
    </>
  );
}
