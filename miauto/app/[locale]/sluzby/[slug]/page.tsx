import type { Metadata } from "next";
import { ArrowRight, ChevronRight, Info, Phone } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getContent, isLocale, LOCALES, SERVICE_SLUGS } from "@/content";
import { ROUTES, canonicalFor, path, servicePath } from "@/lib/i18n";
import { SERVICE_IMAGE } from "@/lib/service-images";
import { breadcrumbJsonLd } from "@/lib/jsonld";
import { site } from "@/config/miauto";
import { Container, Section } from "@/components/ui/Section";
import { Reveal } from "@/components/ui/Reveal";
import { SlotImage } from "@/components/ui/SlotImage";
import { ServiceIcon } from "@/components/ui/ServiceIcon";
import { ButtonLink } from "@/components/ui/Button";
import { ServiceWidget } from "@/components/widgets/ServiceWidget";
import type { ServiceSlug } from "@/content/types";

export function generateStaticParams() {
  return LOCALES.flatMap((locale) => SERVICE_SLUGS.map((slug) => ({ locale, slug })));
}

function isServiceSlug(value: string): value is ServiceSlug {
  return (SERVICE_SLUGS as readonly string[]).includes(value);
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  if (!isLocale(locale) || !isServiceSlug(slug)) return {};
  const service = getContent(locale).services[slug];
  return {
    title: service.meta.title,
    description: service.meta.description,
    alternates: canonicalFor(locale, `${ROUTES.services}/${slug}`),
    openGraph: {
      title: service.meta.title,
      description: service.meta.description,
      type: "article",
    },
  };
}

export default async function ServiceDetailPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  if (!isLocale(locale) || !isServiceSlug(slug)) notFound();

  const t = getContent(locale);
  const service = t.services[slug];
  const slot = SERVICE_IMAGE[slug];

  const crumbs = [
    { name: t.common.home, url: path(locale) },
    { name: t.nav.services, url: path(locale, ROUTES.services) },
    { name: service.name, url: servicePath(locale, slug) },
  ];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd(crumbs)) }}
      />

      <Section rhythm="tight" className="pt-[calc(var(--nav-h)+40px)]">
        <Container>
          <nav aria-label="breadcrumb">
            <ol className="flex flex-wrap items-center gap-1.5 text-[0.8125rem] text-[color:var(--text-muted)]">
              {crumbs.map((crumb, index) => {
                const last = index === crumbs.length - 1;
                return (
                  <li key={crumb.url} className="flex items-center gap-1.5">
                    {index > 0 ? (
                      <ChevronRight size={14} aria-hidden="true" className="opacity-50" />
                    ) : null}
                    {last ? (
                      <span aria-current="page" className="text-[color:var(--text)]">
                        {crumb.name}
                      </span>
                    ) : (
                      <Link href={crumb.url} className="no-underline hover:text-[color:var(--text)]">
                        {crumb.name}
                      </Link>
                    )}
                  </li>
                );
              })}
            </ol>
          </nav>

          <span className="mt-9 inline-flex size-14 items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--surface)] text-[color:var(--accent)]">
            <ServiceIcon name={service.icon} size={26} />
          </span>

          <h1 className="mt-6 max-w-[16ch]">{service.h1}</h1>

          <p className="prose-width mt-7 text-[1.0625rem] text-[color:var(--text-muted)] md:text-[1.1875rem]">
            {service.lead}
          </p>
        </Container>
      </Section>

      <Container>
        <SlotImage
          slot={slot}
          alt={service.name}
          priority
          parallax
          sizes="(min-width: 1200px) 1100px, 100vw"
          className="rounded-[var(--radius-card)] border border-[var(--border)]"
        />
      </Container>

      <Section>
        <Container>
          <div className="grid gap-14 md:grid-cols-2 md:gap-16">
            <Reveal>
              <h2 className="text-[1.5rem] md:text-[1.875rem]">
                {locale === "sk" ? "Kedy to riešiť" : "When to deal with it"}
              </h2>
              <ul className="mt-6 space-y-4">
                {service.when.map((item) => (
                  <li key={item} className="flex gap-3.5">
                    <span
                      aria-hidden="true"
                      className="mt-[0.6em] size-1.5 shrink-0 rounded-full bg-[var(--accent)]"
                    />
                    <span className="text-[color:var(--text-muted)]">{item}</span>
                  </li>
                ))}
              </ul>
            </Reveal>

            <Reveal index={1}>
              <h2 className="text-[1.5rem] md:text-[1.875rem]">
                {locale === "sk" ? "Čo robíme" : "What we do"}
              </h2>
              <ol className="mt-6 space-y-5">
                {service.what.map((item, index) => (
                  <li key={item} className="flex gap-4">
                    <span
                      aria-hidden="true"
                      className="mt-0.5 inline-flex size-7 shrink-0 items-center justify-center rounded-full border border-[var(--border)] font-heading text-[0.8125rem] font-semibold tabular-nums text-[color:var(--accent)]"
                    >
                      {index + 1}
                    </span>
                    <span className="text-[color:var(--text-muted)]">{item}</span>
                  </li>
                ))}
              </ol>
            </Reveal>
          </div>

          {service.note ? (
            <Reveal className="mt-14">
              <div className="flex max-w-[64ch] gap-4 rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)] p-5 md:p-6">
                <Info
                  size={20}
                  aria-hidden="true"
                  className="mt-0.5 shrink-0 text-[color:var(--text-muted)]"
                />
                <p className="text-[0.9375rem] text-[color:var(--text)]">{service.note}</p>
              </div>
            </Reveal>
          ) : null}
        </Container>
      </Section>

      {/* One interactive piece per service, mounted only near the viewport. */}
      <Section rhythm="tight">
        <Container>
          <ServiceWidget slug={slug} t={t} />
        </Container>
      </Section>

      {/* CTA: phone primary, form secondary. */}
      <Section rhythm="tight" className="border-y border-[var(--border)] bg-[var(--surface)]">
        <Container>
          <div className="flex flex-col items-start gap-7 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="text-[1.5rem] md:text-[2rem]">
                {locale === "sk"
                  ? `${service.name} — zavolajte a dohodnime sa`
                  : `${service.name} — call and let us sort it`}
              </h2>
              <p className="mt-3 max-w-[48ch] text-[color:var(--text-muted)]">
                {locale === "sk"
                  ? "Popíšte, čo vozidlo robí. Podľa toho si dohodneme termín."
                  : "Describe what the car is doing and we will arrange a time."}
              </p>
            </div>
            <div className="flex shrink-0 flex-wrap gap-3">
              <ButtonLink href={site.phoneHref} size="lg" aria-label={t.common.callAria}>
                <Phone size={18} aria-hidden="true" />
                {site.phone}
              </ButtonLink>
              <ButtonLink href={path(locale, ROUTES.contact)} size="lg" variant="secondary">
                {t.common.contactCta}
              </ButtonLink>
            </div>
          </div>
        </Container>
      </Section>

      {/* Two related services, plus the route back to the overview. */}
      <Section rhythm="tight">
        <Container>
          <h2 className="text-[1.25rem] md:text-[1.5rem]">{t.common.relatedServices}</h2>
          <ul className="mt-6 grid gap-4 sm:grid-cols-2">
            {service.related.map((relatedSlug, index) => {
              const related = t.services[relatedSlug];
              return (
                <Reveal as="li" key={relatedSlug} index={index}>
                  <article className="card tappable tappable--card relative flex h-full items-start gap-4 p-5 md:p-6">
                    <span className="inline-flex size-11 shrink-0 items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--bg)] text-[color:var(--accent)]">
                      <ServiceIcon name={related.icon} size={20} />
                    </span>
                    <div>
                      <h3 className="text-[1.0625rem]">
                        <Link
                          href={servicePath(locale, relatedSlug)}
                          className="card-link no-underline"
                        >
                          {related.name}
                        </Link>
                      </h3>
                      <p className="mt-1.5 text-[0.875rem] text-[color:var(--text-muted)]">
                        {related.cardDescription}
                      </p>
                    </div>
                  </article>
                </Reveal>
              );
            })}
          </ul>

          <Link
            href={path(locale, ROUTES.services)}
            className="mt-8 inline-flex items-center gap-2 text-[0.9375rem] font-medium text-[color:var(--accent)] no-underline hover:gap-3"
          >
            {t.common.backToServices}
            <ArrowRight size={16} aria-hidden="true" />
          </Link>
        </Container>
      </Section>
    </>
  );
}
