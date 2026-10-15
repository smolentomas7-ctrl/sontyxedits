import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Info } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Section } from "@/components/ui/Section";
import { ButtonLink } from "@/components/ui/Button";
import { Reveal } from "@/components/ui/Reveal";
import { ContactButtons } from "@/components/marketing/ContactOptions";
import { FeatureGroups } from "@/components/marketing/FeatureGroups";
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
    title: dict.features.metaTitle,
    description: dict.features.metaDescription,
    alternates: buildAlternates("features"),
    openGraph: {
      title: dict.features.metaTitle,
      description: dict.features.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function FeaturesPage({
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
          <span className="t-small font-medium uppercase tracking-[0.18em] text-accent">
            {dict.features.eyebrow}
          </span>
          <h1 className="t-h1 max-w-[16ch] text-text">{dict.features.title}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.features.subtitle}</p>
          <p className="t-small flex max-w-[64ch] gap-2.5 rounded-xl border border-border bg-surface px-4 py-3 text-text-muted">
            <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
            {dict.features.note}
          </p>
        </div>
      </Container>

      <Section className="border-t border-border pt-10 md:pt-14">
        <FeatureGroups dict={dict} />
      </Section>

      <Section className="pb-24 pt-0 md:pb-32">
        <Reveal>
          <div className="rounded-3xl border border-accent/20 bg-accent-soft px-7 py-14 text-center md:px-16 md:py-20">
            <h2 className="t-h2 mx-auto max-w-[20ch] text-balance text-text">
              {dict.features.ctaTitle}
            </h2>
            <p className="mx-auto mt-5 max-w-[54ch] text-text-muted">{dict.features.ctaBody}</p>
            <ContactButtons dict={dict} className="mt-8 items-center justify-center" />
          </div>
        </Reveal>
      </Section>
    </>
  );
}
