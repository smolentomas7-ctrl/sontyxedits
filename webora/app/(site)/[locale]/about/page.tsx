import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Image from "next/image";
import { Container } from "@/components/ui/Container";
import { Section, SectionHeading } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { brand } from "@/config/images";
import { siteConfig } from "@/config/site";
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
    title: dict.about.metaTitle,
    description: dict.about.metaDescription,
    alternates: buildAlternates("about"),
    openGraph: {
      title: dict.about.metaTitle,
      description: dict.about.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function AboutPage({
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
          <h1 className="t-h1 max-w-[12ch] text-text">{dict.about.heroTitle}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.about.heroSubtitle}</p>
        </div>
      </Container>

      {/* ---------- story + studio photo ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="story-heading">
        <div className="grid items-start gap-10 lg:grid-cols-2 lg:gap-16">
          <Reveal className="flex flex-col gap-5">
            <h2 id="story-heading" className="t-h2 text-text">
              {dict.about.storyTitle}
            </h2>
            {dict.about.story.map((paragraph) => (
              <p key={paragraph.slice(0, 32)} className="t-prose text-text-muted">
                {paragraph}
              </p>
            ))}
          </Reveal>

          <Reveal delay={80} className="overflow-hidden rounded-2xl border border-border">
            <Image
              src={brand.studio2.src}
              width={brand.studio2.width}
              height={brand.studio2.height}
              alt={brand.studio2.alt}
              sizes="(max-width: 1024px) 100vw, 50vw"
              className="h-full w-full object-cover"
            />
          </Reveal>
        </div>
      </Section>

      {/* ---------- approach ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="approach-heading">
        <SectionHeading id="approach-heading" title={dict.about.approachTitle} className="mb-12" />
        <ul className="grid gap-6 sm:grid-cols-2">
          {dict.about.approach.map((item, index) => (
            <Reveal as="li" key={item.title} delay={index * 60} className="flex">
              <Card className="flex w-full flex-col gap-3 p-7">
                <span className="font-[family-name:var(--font-space-grotesk)] text-sm font-bold text-accent">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <h3 className="t-h3 text-text">{item.title}</h3>
                <p className="text-[15px] text-text-muted">{item.body}</p>
              </Card>
            </Reveal>
          ))}
        </ul>
      </Section>

      {/* ---------- founder ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="founder-heading">
        <div className="grid items-center gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
          <Reveal className="overflow-hidden rounded-2xl border border-border">
            <Image
              src={brand.founder.src}
              width={brand.founder.width}
              height={brand.founder.height}
              alt={brand.founder.alt}
              sizes="(max-width: 1024px) 100vw, 40vw"
              className="h-full w-full object-cover"
            />
          </Reveal>

          <Reveal delay={80} className="flex flex-col gap-4">
            <h2 id="founder-heading" className="t-h2 text-text">
              {dict.about.founderTitle}
            </h2>
            <div>
              {/* Name is a placeholder until it is filled in config/site.ts. */}
              <p className="font-[family-name:var(--font-space-grotesk)] text-xl font-medium text-text">
                {siteConfig.founder}
              </p>
              <p className="t-small text-accent">{dict.about.founderRole}</p>
            </div>
            <p className="t-prose text-text-muted">{dict.about.founderBody}</p>
          </Reveal>
        </div>
      </Section>

      {/* ---------- tools ---------- */}
      <Section className="border-t border-border" ariaLabelledBy="tools-heading">
        <SectionHeading
          id="tools-heading"
          title={dict.about.toolsTitle}
          subtitle={dict.about.toolsBody}
          className="mb-10"
        />
        <ul className="flex flex-wrap gap-2.5">
          {dict.about.tools.map((tool, index) => (
            <Reveal as="li" key={tool} delay={index * 40}>
              <span className="inline-flex rounded-full border border-border bg-surface px-4 py-2 text-[14px] text-text-muted">
                {tool}
              </span>
            </Reveal>
          ))}
        </ul>

        <Reveal className="mt-14 overflow-hidden rounded-2xl border border-border">
          <Image
            src={brand.studio1.src}
            width={brand.studio1.width}
            height={brand.studio1.height}
            alt={brand.studio1.alt}
            sizes="100vw"
            className="w-full object-cover"
          />
        </Reveal>
      </Section>

      {/* ---------- CTA ---------- */}
      <Section className="pb-24 pt-0 md:pb-32">
        <Reveal>
          <div className="rounded-3xl border border-accent/20 bg-accent-soft px-7 py-14 text-center md:px-16 md:py-20">
            <h2 className="t-h2 mx-auto max-w-[18ch] text-balance text-text">
              {dict.about.ctaTitle}
            </h2>
            <p className="mx-auto mt-5 max-w-[52ch] text-text-muted">{dict.about.ctaBody}</p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <ButtonLink href={`/${typedLocale}/contact`}>{dict.about.ctaButton}</ButtonLink>
              <ButtonLink href={`/${typedLocale}/portfolio`} variant="secondary">
                {dict.common.seeDemos}
              </ButtonLink>
            </div>
          </div>
        </Reveal>
      </Section>
    </>
  );
}
