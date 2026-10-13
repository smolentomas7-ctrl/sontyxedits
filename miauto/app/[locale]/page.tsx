import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getContent, isLocale } from "@/content";
import { canonicalFor } from "@/lib/i18n";
import { Container, Section } from "@/components/ui/Section";
import { CastrolPartner } from "@/components/home/CastrolPartner";
import { Reveal } from "@/components/ui/Reveal";
import { CtaBand } from "@/components/layout/CtaBand";
import { Hero } from "@/components/home/Hero";
import { ServicesGrid } from "@/components/home/ServicesGrid";
import { SignatureScene } from "@/components/home/SignatureScene";
import { MapTeaser } from "@/components/home/MapTeaser";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return {
    title: t.home.meta.title,
    description: t.home.meta.description,
    alternates: canonicalFor(locale, ""),
    openGraph: {
      title: t.home.meta.title,
      description: t.home.meta.description,
      locale: locale === "sk" ? "sk_SK" : "en_GB",
      type: "website",
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
  const t = getContent(locale);

  return (
    <>
      <Hero locale={locale} t={t} />

      {/* Services. Airy. */}
      <Section rhythm="loose">
        <Container>
          <Reveal className="mb-12 max-w-[46ch] md:mb-16">
            <h2>{t.home.servicesHeading}</h2>
            <p className="mt-5 text-[1.0625rem] text-[color:var(--text-muted)]">
              {t.home.servicesLead}
            </p>
          </Reveal>
          <ServicesGrid locale={locale} t={t} />
        </Container>
      </Section>

      {/* Signature interaction. Dense section after the airy one. */}
      <Section
        rhythm="tight"
        className="border-y border-[var(--border)] bg-[var(--surface)]"
      >
        <Container>
          <Reveal className="mb-10 max-w-[48ch]">
            <h2>{t.home.signatureHeading}</h2>
            <p className="mt-4 text-[color:var(--text-muted)]">{t.home.signatureLead}</p>
          </Reveal>
          <div className="mx-auto max-w-[62rem]">
            <SignatureScene t={t} />
          </div>
        </Container>
      </Section>

      {/* Why this workshop. */}
      <Section>
        <Container>
          <Reveal className="mb-12 max-w-[40ch]">
            <h2>{t.home.whyHeading}</h2>
          </Reveal>
          <ul className="grid gap-x-10 gap-y-10 md:grid-cols-2 md:gap-y-14">
            {t.home.why.map((item, index) => (
              <Reveal as="li" key={item.title} index={index}>
                <h3 className="flex items-baseline gap-3 text-[1.1875rem] md:text-[1.375rem]">
                  <span
                    aria-hidden="true"
                    className="font-heading text-[0.875rem] font-semibold tabular-nums text-[color:var(--accent)]"
                  >
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  {item.title}
                </h3>
                <p className="prose-width mt-3 pl-[2.1rem] text-[color:var(--text-muted)]">
                  {item.body}
                </p>
              </Reveal>
            ))}
          </ul>
        </Container>
      </Section>

      {/* The partnership, where it follows the reasons to trust the workshop. */}
      <Section rhythm="tight">
        <Container>
          <CastrolPartner t={t} />
        </Container>
      </Section>

      {/* Map teaser, click-to-load. */}
      <Section rhythm="tight" className="border-t border-[var(--border)]">
        <Container>
          <MapTeaser t={t} />
        </Container>
      </Section>

      <CtaBand
        locale={locale}
        t={t}
        heading={t.home.finalHeading}
        lead={t.home.finalLead}
      />
    </>
  );
}
