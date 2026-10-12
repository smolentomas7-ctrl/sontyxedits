import type { Metadata } from "next";
import { AlertTriangle } from "lucide-react";
import { notFound } from "next/navigation";
import { getContent, isLocale } from "@/content";
import { ROUTES, canonicalFor } from "@/lib/i18n";
import { Container, Section } from "@/components/ui/Section";
import { PlaceholderToken } from "@/components/ui/Placeholder";

/** Renders [IČO], [EMAIL] and [TO CONFIRM: …] visibly wherever they appear. */
function withPlaceholders(text: string) {
  const parts = text.split(/(\[[^\]]+\])/g);
  return parts.map((part, index) =>
    /^\[[^\]]+\]$/.test(part) ? (
      <PlaceholderToken key={index}>{part}</PlaceholderToken>
    ) : (
      <span key={index}>{part}</span>
    ),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getContent(locale);
  return {
    title: t.privacy.meta.title,
    description: t.privacy.meta.description,
    alternates: canonicalFor(locale, ROUTES.privacy),
    robots: { index: true, follow: true },
  };
}

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const t = getContent(locale);

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

          <p className="mt-6 text-[0.875rem] text-[color:var(--text-muted)]">{t.privacy.updated}</p>

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
                        className="flex flex-wrap items-center gap-x-1 leading-relaxed text-[color:var(--text-muted)]"
                      >
                        {withPlaceholders(paragraph)}
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
