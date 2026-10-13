import type { Metadata } from "next";
import { MapPin, Phone } from "lucide-react";
import { notFound } from "next/navigation";
import { getContent, isLocale, SERVICE_SLUGS } from "@/content";
import { ROUTES, canonicalFor, path, servicePath } from "@/lib/i18n";
import { images } from "@/config/images";
import { formattedAddress, site } from "@/config/miauto";
import { Container, Section } from "@/components/ui/Section";
import { Reveal } from "@/components/ui/Reveal";
import { SlotImage } from "@/components/ui/SlotImage";
import { HoursTable } from "@/components/ui/HoursTable";
import { Owners } from "@/components/about/Owners";
import { Experience } from "@/components/about/Experience";
import { ServiceIcon } from "@/components/ui/ServiceIcon";
import { ButtonLink } from "@/components/ui/Button";
import { CtaBand } from "@/components/layout/CtaBand";
import Link from "next/link";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return {
    title: t.about.meta.title,
    description: t.about.meta.description,
    alternates: canonicalFor(locale, ROUTES.about),
    openGraph: { title: t.about.meta.title, description: t.about.meta.description },
  };
}

export default async function AboutPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const t = getContent(locale);

  return (
    <>
      <Section rhythm="tight" className="pt-[calc(var(--nav-h)+56px)]">
        <Container>
          <div className="grid gap-12 lg:grid-cols-[1.15fr_1fr] lg:items-end lg:gap-16">
            <div>
              <h1 className="max-w-[12ch]">{t.about.h1}</h1>
              <p className="prose-width mt-6 text-[1.0625rem] text-[color:var(--text-muted)] md:text-[1.125rem]">
                {t.about.lead}
              </p>
            </div>
            <SlotImage
              slot={images.aboutInterior}
              alt={t.about.interiorAlt}
              priority
              sizes="(min-width: 1024px) 40vw, 100vw"
              className="rounded-[var(--radius-card)] border border-[var(--border)]"
            />
          </div>
        </Container>
      </Section>

      {/* One quiet section that is nothing but well-set words. */}
      <Section className="border-y border-[var(--border)]">
        <Container>
          <div className="mx-auto max-w-[62ch]">
            <h2 className="text-[1.5rem] md:text-[2rem]">{t.about.quietHeading}</h2>
            <div className="mt-8 space-y-6 text-[1.0625rem] leading-[1.75] md:text-[1.125rem] md:leading-[1.8]">
              {t.about.quietBody.map((paragraph) => (
                <p key={paragraph.slice(0, 24)}>{paragraph}</p>
              ))}
            </div>
          </div>
        </Container>
      </Section>

      <Section>
        <Container>
          <Owners locale={locale} t={t} />
        </Container>
      </Section>

      {/* Who they are, then what they bring to it. */}
      <Section rhythm="tight" className="border-t border-[var(--border)]">
        <Container>
          <Experience t={t} />
        </Container>
      </Section>

      {/* What is actually confirmed: the services. */}
      <Section rhythm="tight" className="border-t border-[var(--border)]">
        <Container>
          <h2 className="text-[1.5rem] md:text-[2rem]">{t.about.whatWeDoHeading}</h2>
          <ul className="mt-8 grid gap-x-8 gap-y-5 sm:grid-cols-2 lg:grid-cols-3">
            {SERVICE_SLUGS.map((slug, index) => (
              <Reveal as="li" key={slug} index={index}>
                <Link
                  href={servicePath(locale, slug)}
                  className="flex items-center gap-3 rounded-[var(--radius-control)] py-1 text-[0.9375rem] no-underline hover:text-[color:var(--accent)]"
                >
                  <ServiceIcon
                    name={t.services[slug].icon}
                    size={19}
                    className="shrink-0 text-[color:var(--accent)]"
                  />
                  {t.services[slug].name}
                </Link>
              </Reveal>
            ))}
          </ul>

          <div className="mt-14 grid gap-5 md:grid-cols-2">
            <SlotImage
              slot={images.aboutDetail01}
              alt={t.about.detail01Alt}
              index={0}
              sizes="(min-width: 768px) 50vw, 100vw"
              variant="card"
              className="rounded-[var(--radius-card)] border border-[var(--border)]"
            />
            <SlotImage
              slot={images.aboutDetail02}
              alt={t.about.detail02Alt}
              index={1}
              sizes="(min-width: 768px) 50vw, 100vw"
              variant="card"
              className="rounded-[var(--radius-card)] border border-[var(--border)]"
            />
          </div>
        </Container>
      </Section>

      {/* Confirmed facts: where, when, what number. */}
      <Section rhythm="tight">
        <Container>
          <div className="grid gap-10 md:grid-cols-2 md:gap-14">
            <div>
              <h2 className="text-[1.25rem] md:text-[1.5rem]">{t.about.factsHeading}</h2>
              <address className="mt-5 flex items-start gap-3 not-italic text-[1.0625rem]">
                <MapPin
                  size={19}
                  aria-hidden="true"
                  className="mt-1 shrink-0 text-[color:var(--accent)]"
                />
                <span>
                  {formattedAddress}
                  <br />
                  <a
                    href={site.phoneHref}
                    className="mt-2 inline-block font-semibold no-underline hover:text-[color:var(--accent)]"
                  >
                    {site.phone}
                  </a>
                </span>
              </address>
              <ButtonLink
                href={path(locale, ROUTES.contact)}
                variant="secondary"
                className="mt-7"
              >
                {t.nav.contact}
              </ButtonLink>
            </div>
            <div>
              <h2 className="text-[1.25rem] md:text-[1.5rem]">{t.common.hoursHeading}</h2>
              <div className="mt-5">
                <HoursTable t={t} />
              </div>
            </div>
          </div>
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
