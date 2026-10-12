import type { Metadata } from "next";
import { ExternalLink, MapPin, Phone } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getContent, isLocale } from "@/content";
import { ROUTES, canonicalFor, path } from "@/lib/i18n";
import { formattedAddress, isPlaceholder, site } from "@/config/miauto";
import { Container, Section } from "@/components/ui/Section";
import { HoursTable, OpenBadge } from "@/components/ui/HoursTable";
import { PlaceholderToken } from "@/components/ui/Placeholder";
import { ButtonLink } from "@/components/ui/Button";
import { CopyAddress } from "@/components/contact/CopyAddress";
import { MapFrame } from "@/components/contact/MapFrame";
import { ContactForm } from "@/components/contact/ContactForm";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return {
    title: t.contact.meta.title,
    description: t.contact.meta.description,
    alternates: canonicalFor(locale, ROUTES.contact),
    openGraph: { title: t.contact.meta.title, description: t.contact.meta.description },
  };
}

export default async function ContactPage({
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
          <h1 className="max-w-[12ch]">{t.contact.h1}</h1>
          <p className="prose-width mt-6 text-[1.0625rem] text-[color:var(--text-muted)] md:text-[1.125rem]">
            {t.contact.lead}
          </p>

          <div className="mt-12 grid gap-10 md:grid-cols-2 md:gap-14">
            <div>
              <h2 className="text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
                {t.common.addressHeading}
              </h2>
              <address className="mt-4 flex items-start gap-3 not-italic text-[1.125rem]">
                <MapPin
                  size={20}
                  aria-hidden="true"
                  className="mt-1 shrink-0 text-[color:var(--accent)]"
                />
                <span>{formattedAddress}</span>
              </address>
              <div className="mt-4">
                <CopyAddress t={t} />
              </div>

              <h2 className="mt-10 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
                {t.common.phoneHeading}
              </h2>
              <p className="mt-4">
                <a
                  href={site.phoneHref}
                  aria-label={t.common.callAria}
                  className="font-heading text-[1.75rem] font-bold tracking-[-0.02em] no-underline hover:text-[color:var(--accent)] md:text-[2.25rem]"
                >
                  {site.phone}
                </a>
              </p>
              <p className="mt-3 flex flex-wrap items-center gap-2 text-[0.9375rem]">
                {isPlaceholder(site.email) ? (
                  <>
                    <PlaceholderToken>{site.email}</PlaceholderToken>
                    <span className="text-[color:var(--text-muted)]">
                      {t.contact.emailPendingNote}
                    </span>
                  </>
                ) : (
                  <a href={`mailto:${site.email}`}>{site.email}</a>
                )}
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <ButtonLink href={site.phoneHref} aria-label={t.common.callAria}>
                  <Phone size={17} aria-hidden="true" />
                  {t.common.callCta}
                </ButtonLink>
                <ButtonLink href={site.mapDirectionsUrl} variant="secondary" external>
                  {t.common.navigateCta}
                  <ExternalLink size={16} aria-hidden="true" />
                </ButtonLink>
              </div>
            </div>

            <div>
              <h2 className="text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
                {t.common.hoursHeading}
              </h2>
              <div className="mt-4">
                <HoursTable t={t} />
              </div>
              <p className="mt-5 text-[0.9375rem]">
                <OpenBadge t={t} />
              </p>
            </div>
          </div>
        </Container>
      </Section>

      {/* The map is the purpose of this page, so it loads directly here. */}
      <Section rhythm="tight">
        <Container>
          <h2 className="text-[1.25rem] md:text-[1.5rem]">{t.contact.mapHeading}</h2>
          {/* 4:3 on mobile, 16:9 from md — one element, one embed, one probe.
              The map loads directly here, because the map is the point of this page. */}
          <MapFrame t={t} className="mt-6" />
          <p className="mt-4 max-w-[62ch] text-[0.875rem] text-[color:var(--text-muted)]">
            {t.contact.mapDisclosure}{" "}
            <Link href={path(locale, ROUTES.privacy)} className="text-[color:var(--accent)]">
              {t.contact.mapDisclosureLink}
            </Link>
            .
          </p>
        </Container>
      </Section>

      <Section className="border-t border-[var(--border)] bg-[var(--surface)]">
        <Container>
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
            <div>
              <h2>{t.contact.formHeading}</h2>
              <p className="mt-5 max-w-[40ch] text-[color:var(--text-muted)]">
                {t.contact.formLead}
              </p>
            </div>
            <ContactForm locale={locale} t={t} />
          </div>
        </Container>
      </Section>
    </>
  );
}
