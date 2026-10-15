import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Clock } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { ContactOptions } from "@/components/marketing/ContactOptions";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
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
    title: dict.contact.metaTitle,
    description: dict.contact.metaDescription,
    alternates: buildAlternates("contact"),
    openGraph: {
      title: dict.contact.metaTitle,
      description: dict.contact.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

/**
 * Two ways to get in touch and nothing else.
 *
 * There is deliberately no form here: a form that cannot send is worse than
 * no form, and e-mail and WhatsApp reach a one-person studio faster than any
 * inbox-shaped widget would.
 */
export default async function ContactPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);
  const t = dict.contact;

  return (
    <Container>
      <div className="flex flex-col gap-6 py-20 md:py-28">
        <h1 className="t-h1 max-w-[12ch] text-text">{t.heroTitle}</h1>
        <p className="t-prose text-lg text-text-muted">{t.heroSubtitle}</p>
      </div>

      <div className="grid gap-12 pb-24 lg:grid-cols-[1.3fr_1fr] lg:gap-16 md:pb-32">
        <Reveal className="min-w-0">
          <h2 className="t-h3 text-text">{t.title}</h2>
          <p className="t-prose mt-3 text-text-muted">{t.body}</p>

          <ContactOptions dict={dict} className="mt-8" />

          <p className="t-small mt-5 text-text-muted">{t.whatsappNote}</p>
        </Reveal>

        <aside className="flex min-w-0 flex-col gap-6">
          <Reveal delay={80}>
            <Card interactive={false} className="flex flex-col gap-5 p-7">
              <h2 className="t-h3 text-text">{t.nextStepsTitle}</h2>
              <ol className="flex flex-col gap-4">
                {t.nextSteps.map((step, index) => (
                  <li key={step} className="flex items-start gap-3 text-[15px] text-text-muted">
                    <span
                      aria-hidden="true"
                      className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-accent-soft text-[12px] font-bold text-accent"
                    >
                      {index + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>

              <p className="flex items-start gap-3 border-t border-border pt-5 text-[15px]">
                <Clock
                  aria-hidden="true"
                  strokeWidth={1.5}
                  className="mt-0.5 size-4 shrink-0 text-accent"
                />
                <span className="flex flex-col">
                  <span className="t-small text-text-muted">{t.responseLabel}</span>
                  <span className="text-text">{siteConfig.responseTime[typedLocale]}</span>
                </span>
              </p>
            </Card>
          </Reveal>
        </aside>
      </div>
    </Container>
  );
}
