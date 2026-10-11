import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { buildAlternates } from "@/lib/seo";
import { formatDate } from "@/lib/utils";

/** Bump this when the policy text is actually revised. */
const LAST_UPDATED = "2026-10-11";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.privacy.metaTitle,
    description: dict.privacy.metaDescription,
    alternates: buildAlternates("legal/privacy"),
    robots: { index: false, follow: true },
  };
}

export default async function PrivacyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  return (
    <Container>
      <article className="flex flex-col gap-8 py-20 md:py-28">
        <header className="flex flex-col gap-4">
          <h1 className="t-h1 text-text">{dict.privacy.title}</h1>
          <p className="t-small text-text-muted">
            {dict.privacy.lastUpdated}: {formatDate(LAST_UPDATED, typedLocale)}
          </p>
        </header>

        <div
          role="note"
          className="flex gap-3 rounded-xl border border-[#F59E0B]/40 bg-[#F59E0B]/10 p-5"
        >
          <AlertTriangle
            aria-hidden="true"
            strokeWidth={1.5}
            className="mt-0.5 size-5 shrink-0 text-[#F59E0B]"
          />
          <p className="t-prose text-[15px] leading-relaxed text-text">
            {dict.privacy.templateWarning}
          </p>
        </div>

        <div className="prose-webora">
          {dict.privacy.sections.map((section) => (
            <section key={section.title}>
              <h2>{section.title}</h2>
              {section.body.map((paragraph) => (
                <p key={paragraph.slice(0, 32)}>{paragraph}</p>
              ))}
            </section>
          ))}
        </div>

        <p className="t-small text-text-muted">
          <Link href={`/${typedLocale}/contact`} className="text-accent hover:underline">
            {dict.nav.contact}
          </Link>
          {" · "}
          <Link href={`/${typedLocale}`} className="text-accent hover:underline">
            {dict.nav.home}
          </Link>
        </p>
      </article>
    </Container>
  );
}
