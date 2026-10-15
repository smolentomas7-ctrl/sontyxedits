import type { Metadata } from "next";
import { ArrowRight, Check } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getContent, isLocale, SERVICE_SLUGS } from "@/content";
import { ROUTES, pageSeo, servicePath } from "@/lib/i18n";
import { SERVICE_IMAGE } from "@/lib/service-images";
import { Container, Section } from "@/components/ui/Section";
import { Reveal } from "@/components/ui/Reveal";
import { SlotImage } from "@/components/ui/SlotImage";
import { Accordion } from "@/components/ui/Accordion";
import { ServiceIcon } from "@/components/ui/ServiceIcon";
import { CtaBand } from "@/components/layout/CtaBand";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return pageSeo(locale, ROUTES.services, t.servicesPage.meta);
}

export default async function ServicesPage({
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
          <h1 className="max-w-[14ch]">{t.servicesPage.h1}</h1>
          <p className="prose-width mt-6 text-[1.0625rem] text-[color:var(--text-muted)] md:text-[1.125rem]">
            {t.servicesPage.lead}
          </p>
        </Container>
      </Section>

      <Section rhythm="tight">
        <Container>
          <div className="flex flex-col gap-20 md:gap-28">
            {SERVICE_SLUGS.map((slug, index) => {
              const service = t.services[slug];
              const slot = SERVICE_IMAGE[slug];
              const flipped = index % 2 === 1;
              return (
                <Reveal
                  as="article"
                  key={slug}
                  className="grid items-center gap-8 md:grid-cols-2 md:gap-14"
                >
                  <div className={flipped ? "md:order-2" : undefined}>
                    <SlotImage
                      slot={slot}
                      alt={service.name}
                      index={0}
                      sizes="(min-width: 768px) 50vw, 100vw"
                      className="rounded-[var(--radius-card)] border border-[var(--border)]"
                    />
                  </div>

                  <div className={flipped ? "md:order-1" : undefined}>
                    <span className="mb-5 inline-flex size-12 items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--surface)] text-[color:var(--accent)]">
                      <ServiceIcon name={service.icon} size={22} />
                    </span>
                    <h2 className="text-[1.75rem] md:text-[2.25rem]">{service.name}</h2>
                    <p className="prose-width mt-4 text-[color:var(--text-muted)]">
                      {service.overview}
                    </p>

                    <ul className="mt-6 space-y-2.5">
                      {service.covers.map((item) => (
                        <li key={item} className="flex gap-3 text-[0.9375rem]">
                          <Check
                            size={18}
                            aria-hidden="true"
                            className="mt-0.5 shrink-0 text-[color:var(--accent)]"
                          />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>

                    <Link
                      href={servicePath(locale, slug)}
                      className="mt-7 inline-flex items-center gap-2 font-medium text-[color:var(--accent)] no-underline hover:gap-3"
                    >
                      {t.common.readMore}
                      <ArrowRight size={17} aria-hidden="true" />
                    </Link>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </Container>
      </Section>

      <Section id="faq" className="border-t border-[var(--border)]">
        <Container>
          <Reveal className="mb-10 max-w-[40ch]">
            <h2>{t.servicesPage.faqHeading}</h2>
          </Reveal>
          <div className="max-w-[56rem]">
            <Accordion items={t.faq} />
          </div>
        </Container>
      </Section>

      <CtaBand
        locale={locale}
        t={t}
        heading={t.servicesPage.ctaHeading}
        lead={t.servicesPage.ctaLead}
      />
    </>
  );
}
