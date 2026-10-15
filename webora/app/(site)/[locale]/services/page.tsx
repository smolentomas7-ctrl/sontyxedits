import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Check, Clock, Tag } from "lucide-react";
import { Section, SectionHeading } from "@/components/ui/Section";
import { Container } from "@/components/ui/Container";
import { ButtonLink } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";
import { mailtoHref } from "@/config/site";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { buildAlternates, ogImages } from "@/lib/seo";
import { cn } from "@/lib/utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const dict = getDictionary(locale);

  return {
    title: dict.services.metaTitle,
    description: dict.services.metaDescription,
    alternates: buildAlternates("services"),
    openGraph: {
      title: dict.services.metaTitle,
      description: dict.services.metaDescription,
      type: "website",
      images: ogImages(locale),
    },
  };
}

export default async function ServicesPage({
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
          <h1 className="t-h1 max-w-[14ch] text-text">{dict.services.heroTitle}</h1>
          <p className="t-prose text-lg text-text-muted">{dict.services.heroSubtitle}</p>
        </div>
      </Container>

      {dict.services.items.map((service, index) => {
        const reversed = index % 2 === 1;

        return (
          <Section
            key={service.slug}
            id={service.slug}
            className={cn("border-t border-border", index === 0 && "border-t")}
          >
            <div
              className={cn(
                "grid items-start gap-10 lg:grid-cols-2 lg:gap-16",
                reversed && "lg:[&>*:first-child]:order-2",
              )}
            >
              <Reveal className="flex flex-col gap-5">
                <span className="t-small font-medium uppercase tracking-[0.16em] text-accent">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <h2 className="t-h2 text-text">{service.name}</h2>

                <div className="flex flex-col gap-4">
                  <div>
                    <h3 className="t-small mb-1.5 font-medium uppercase tracking-[0.12em] text-text-muted">
                      {dict.services.whatItIs}
                    </h3>
                    <p className="t-prose text-text-muted">{service.what}</p>
                  </div>
                  <div>
                    <h3 className="t-small mb-1.5 font-medium uppercase tracking-[0.12em] text-text-muted">
                      {dict.services.whoItSuits}
                    </h3>
                    <p className="t-prose text-text-muted">{service.who}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-6 pt-1">
                  <p className="flex items-center gap-2 text-[15px]">
                    <Clock aria-hidden="true" strokeWidth={1.5} className="size-4 text-accent" />
                    <span className="text-text-muted">{dict.services.timeline}:</span>
                    <span className="font-medium text-text">{service.timeline}</span>
                  </p>
                </div>

                <div className="pt-2">
                  <ButtonLink
                    href={mailtoHref(`${dict.contact.mailSubject} — ${service.name}`)}
                    external
                  >
                    {dict.services.cta}
                  </ButtonLink>
                </div>
              </Reveal>

              <Reveal delay={80}>
                <Card interactive={false} className="p-7 md:p-9">
                  <h3 className="t-small mb-5 font-medium uppercase tracking-[0.12em] text-text">
                    {dict.services.included}
                  </h3>
                  <ul className="flex flex-col gap-3.5">
                    {service.includes.map((item) => (
                      <li key={item} className="flex items-start gap-3 text-[15px] text-text-muted">
                        <Check
                          aria-hidden="true"
                          strokeWidth={1.5}
                          className="mt-0.5 size-4 shrink-0 text-accent"
                        />
                        {item}
                      </li>
                    ))}
                  </ul>
                </Card>
              </Reveal>
            </div>
          </Section>
        );
      })}

      <Section className="border-t border-border" ariaLabelledBy="always-heading">
        <SectionHeading
          id="always-heading"
          title={dict.services.alwaysTitle}
          subtitle={dict.services.alwaysSubtitle}
          className="mb-14"
        />
        <ul className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {dict.services.always.map((item, index) => (
            <Reveal as="li" key={item.title} delay={index * 60} className="flex">
              <Card className="flex w-full flex-col gap-2.5 p-6">
                <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-medium text-text">
                  {item.title}
                </h3>
                <p className="t-small text-text-muted">{item.body}</p>
              </Card>
            </Reveal>
          ))}
        </ul>

        <div className="mt-12 flex flex-col gap-3 sm:flex-row">
          <ButtonLink href={mailtoHref(dict.contact.mailSubject)} external size="lg">
            {dict.contact.emailCta}
          </ButtonLink>
          <ButtonLink href={`/${typedLocale}/features`} variant="secondary" size="lg">
            {dict.nav.features}
          </ButtonLink>

        </div>
      </Section>
    </>
  );
}
