import type { Metadata } from "next";
import Image from "next/image";
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
  RefreshCw,
  Check,
} from "lucide-react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Container } from "@/components/ui/Container";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { Accordion } from "@/components/ui/Accordion";
import { Parallax } from "@/components/ui/Parallax";
import { WorkShowcase } from "@/components/marketing/WorkShowcase";
import { Testimonials } from "@/components/marketing/Testimonials";
import { ContactOptions, ContactButtons } from "@/components/marketing/ContactOptions";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { WhatsAppIcon } from "@/components/ui/WhatsAppIcon";
import { siteConfig } from "@/config/site";
import { marketing } from "@/config/images";
import { buildAlternates, ogImages } from "@/lib/seo";

const TRUST_ICONS = [Smartphone, Gauge, Search, GraduationCap];
/** config/images.ts keeps alt text in Slovak, the default locale. */
const HERO_ALT_EN = "A dark desk with a monitor, keyboard and laptop lit at night";
/** One per service, in the order services are listed. */
const SERVICE_ICONS = [FileText, Layout, RefreshCw];

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

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
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
    // The WhatsApp number is a real line, so it belongs here as telephone.
    telephone: siteConfig.whatsapp.display,
    contactPoint: {
      "@type": "ContactPoint",
      contactType: "sales",
      email: siteConfig.email,
      telephone: siteConfig.whatsapp.display,
      availableLanguage: ["sk", "en"],
    },
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

      {/* ---------- 1. HERO ----------
          Full-bleed photograph with the text set on it, bottom-left, the way
          the M.I.Auto build does it. The section slides up under the fixed,
          transparent header so the photo reaches the top edge. */}
      <section
        data-parallax-area=""
        className="relative isolate -mt-16 flex min-h-[86svh] items-end overflow-hidden pb-14 pt-32 md:-mt-20 md:min-h-[92svh] md:pb-24 md:pt-40"
      >
        <div className="absolute inset-0 -z-10 bg-bg">
          {/* Not wrapped in Reveal: it is the largest element in the first
              viewport, so it paints immediately. */}
          <Parallax className="absolute inset-0" shift={8} tilt={0.6}>
            <Image
              src={marketing.hero.src}
              alt={typedLocale === "sk" ? marketing.hero.alt : HERO_ALT_EN}
              fill
              priority
              sizes="100vw"
              className="hero-image object-cover brightness-[1.35] saturate-[1.1]"
            />
          </Parallax>
          {/* Two scrims, as on M.I.Auto: the vertical one gives the text block
              solid ground, the horizontal one (tablet and up) keeps the
              headline column dark while the monitor on the right stays lit.
              On phones the text covers the whole photo, so it gets an even
              extra layer instead. */}
          <div aria-hidden="true" className="absolute inset-0 bg-bg/55 md:hidden" />
          <div
            aria-hidden="true"
            className="absolute inset-0"
            style={{
              background:
                "linear-gradient(to top, var(--bg) 3%, color-mix(in srgb, var(--bg) 72%, transparent) 28%, color-mix(in srgb, var(--bg) 22%, transparent) 60%, color-mix(in srgb, var(--bg) 10%, transparent) 100%)",
            }}
          />
          <div
            aria-hidden="true"
            className="absolute inset-0 hidden md:block"
            style={{
              background:
                "linear-gradient(to right, color-mix(in srgb, var(--bg) 88%, transparent) 0%, color-mix(in srgb, var(--bg) 62%, transparent) 34%, color-mix(in srgb, var(--bg) 12%, transparent) 60%, transparent 80%)",
            }}
          />
        </div>

        <Container>
          <div className="flex flex-col items-start">
            <Reveal>
              <span className="t-small inline-flex rounded-full border border-white/15 bg-bg/50 px-3.5 py-1.5 font-semibold uppercase tracking-[0.14em] text-accent backdrop-blur-sm">
                {dict.home.heroEyebrow}
              </span>
            </Reveal>

            <Reveal delay={70}>
              <h1 className="t-display mt-6 max-w-[16ch] text-balance text-text">
                {dict.home.heroTitle}{" "}
                <span className="text-accent">{dict.home.heroTitleAccent}</span>
              </h1>
            </Reveal>

            <Reveal delay={140}>
              <p className="t-lead mt-7 max-w-[46ch] text-text/85">{dict.home.heroSubtitle}</p>
            </Reveal>

            <Reveal delay={210}>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
                <ButtonLink href={siteConfig.whatsapp.href} external target="_blank" size="lg">
                  <WhatsAppIcon className="size-[18px]" />
                  {dict.home.heroPrimary}
                </ButtonLink>
                <ButtonLink href={`/${typedLocale}/portfolio`} variant="secondary" size="lg">
                  {dict.home.heroSecondary}
                </ButtonLink>
              </div>
            </Reveal>

            <Reveal delay={280}>
              <dl className="mt-10 flex flex-wrap gap-x-10 gap-y-5">
                {dict.home.heroStats.map((stat) => (
                  <div key={stat.label}>
                    <dt className="sr-only">{stat.label}</dt>
                    <dd>
                      <span className="block font-display text-[1.75rem] font-bold tracking-[-0.035em] text-text">
                        {stat.value}
                      </span>
                      <span className="t-small mt-0.5 block max-w-[20ch] text-text-muted">
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
                <h3 className="font-display text-[17px] font-semibold text-text">{item.title}</h3>
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
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-accent/30 bg-accent-soft font-display text-sm font-bold text-accent">
                  {index + 1}
                </span>
                {index < dict.home.process.length - 1 ? (
                  <span className="mt-2 w-px flex-1 bg-border md:hidden" />
                ) : null}
              </div>

              <div className="pb-2 md:mt-5">
                <h3 className="font-display text-[17px] font-semibold text-text">{step.title}</h3>
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
          <Reveal className="min-w-0">
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
            <ContactButtons dict={dict} className="mt-8" />
          </Reveal>

          <Reveal delay={80}>
            <h3 className="t-small mb-5 font-medium uppercase tracking-[0.12em] text-text">
              {dict.pricing.factorsTitle}
            </h3>
            <ul className="grid gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-2">
              {dict.pricing.factors.map((factor) => (
                <li key={factor.title} className="bg-surface p-6">
                  <h4 className="font-display text-[16px] font-semibold text-text">
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
            <ContactOptions dict={dict} className="mx-auto mt-10 max-w-[760px] text-left" />

            <div className="mt-8 flex justify-center">
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
