import type { Metadata } from "next";
import { AlertTriangle } from "lucide-react";
import { notFound } from "next/navigation";
import { getContent, isLocale } from "@/content";
import { ROUTES, pageSeo } from "@/lib/i18n";
import { formattedAddress, has, mailtoHref, site } from "@/config/miauto";
import { Container, Section } from "@/components/ui/Section";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return { ...pageSeo(locale, ROUTES.privacy, t.privacy.meta), robots: { index: true, follow: true } };
}

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const t = getContent(locale);

  /**
   * Identification of the controller, rendered from config/miauto.ts so it
   * matches the footer exactly. Registration lines appear as soon as they hold
   * a value; nothing is invented to fill a gap.
   */
  const registration = [
    { label: t.footer.icoLabel, value: site.ico },
    { label: t.footer.dicLabel, value: site.dic },
    { label: t.footer.icDphLabel, value: site.icDph },
    { label: t.footer.registryLabel, value: site.zapisVOR },
  ].filter((item) => has(item.value));

  return (
    <Section rhythm="tight" className="pt-[calc(var(--nav-h)+56px)]">
      <Container>
        <div className="max-w-[68ch]">
          <h1>{t.privacy.h1}</h1>

          {/* Visible at the top of the page, not buried in a footnote. */}
          <div className="mt-8 flex gap-4 rounded-[var(--radius-card)] border border-[var(--danger)] bg-[color-mix(in_srgb,var(--danger)_10%,transparent)] p-5 md:p-6">
            <AlertTriangle
              size={22}
              aria-hidden="true"
              className="mt-0.5 shrink-0 text-[color:var(--danger)]"
            />
            <p className="text-[0.9375rem] leading-relaxed">{t.privacy.reviewNotice}</p>
          </div>

          <p className="mt-6 text-[0.875rem] text-[color:var(--text-muted)]">
            {t.privacy.updated}
          </p>

          <section className="mt-12">
            <h2 className="text-[1.375rem] md:text-[1.625rem]">
              {t.privacy.controller.heading}
            </h2>
            <p className="mt-5 text-[color:var(--text-muted)]">{t.privacy.controller.intro}</p>
            <address className="mt-4 not-italic leading-relaxed">
              <strong className="font-semibold">{site.legalName}</strong>
              <br />
              {formattedAddress}
              <br />
              <a href={site.phoneHref} className="no-underline hover:text-[color:var(--accent)]">
                {site.phone}
              </a>
              {" · "}
              <a href={mailtoHref} className="no-underline hover:text-[color:var(--accent)]">
                {site.email}
              </a>
              {registration.length > 0 ? (
                <>
                  <br />
                  <span className="text-[0.9375rem] text-[color:var(--text-muted)]">
                    {registration.map((item, index) => (
                      <span key={item.label}>
                        {index > 0 ? " · " : null}
                        {item.label}: {item.value}
                      </span>
                    ))}
                  </span>
                </>
              ) : null}
            </address>
          </section>

          <div className="mt-12 space-y-12">
            {t.privacy.sections.map((section) => (
              <section key={section.heading}>
                <h2 className="text-[1.375rem] md:text-[1.625rem]">{section.heading}</h2>
                <div className="mt-5 space-y-4">
                  {section.body
                    .filter((paragraph) => paragraph.trim() !== "")
                    .map((paragraph) => (
                      <p
                        key={paragraph.slice(0, 28)}
                        className="leading-relaxed text-[color:var(--text-muted)]"
                      >
                        {paragraph}
                      </p>
                    ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      </Container>
    </Section>
  );
}
