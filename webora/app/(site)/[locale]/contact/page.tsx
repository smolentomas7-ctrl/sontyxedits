import type { Metadata } from "next";
import { Suspense } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Mail, Phone, MapPin, Clock } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { Card } from "@/components/ui/Card";
import { ContactForm } from "@/components/marketing/ContactForm";
import { getDictionary, isLocale, type Locale } from "@/content/i18n";
import { siteConfig, isPlaceholder } from "@/config/site";
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

export default async function ContactPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const typedLocale: Locale = locale;
  const dict = getDictionary(typedLocale);

  const emailIsReal = !isPlaceholder(siteConfig.email);
  const phoneIsReal = !isPlaceholder(siteConfig.phone);

  const socials = [
    { label: "Instagram", href: siteConfig.social.instagram },
    { label: "Facebook", href: siteConfig.social.facebook },
    { label: "LinkedIn", href: siteConfig.social.linkedin },
  ];

  return (
    <Container>
      <div className="flex flex-col gap-6 py-20 md:py-28">
        <h1 className="t-h1 max-w-[12ch] text-text">{dict.contact.heroTitle}</h1>
        <p className="t-prose text-lg text-text-muted">{dict.contact.heroSubtitle}</p>
      </div>

      <div className="grid gap-12 pb-24 lg:grid-cols-[1.25fr_1fr] lg:gap-16 md:pb-32">
        <Suspense fallback={<div className="h-96" />}>
          <ContactForm locale={typedLocale} dict={dict} />
        </Suspense>

        <aside className="flex flex-col gap-6">
          <Card interactive={false} className="flex flex-col gap-5 p-7">
            <h2 className="t-h3 text-text">{dict.contact.detailsTitle}</h2>

            <ul className="flex flex-col gap-4 text-[15px]">
              <li className="flex items-start gap-3">
                <Mail aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
                <span className="flex flex-col">
                  <span className="t-small text-text-muted">{dict.contact.emailLabel}</span>
                  {emailIsReal ? (
                    <a href={`mailto:${siteConfig.email}`} className="text-text hover:text-accent">
                      {siteConfig.email}
                    </a>
                  ) : (
                    <span className="text-text">{siteConfig.email}</span>
                  )}
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Phone aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
                <span className="flex flex-col">
                  <span className="t-small text-text-muted">{dict.contact.phoneLabel}</span>
                  {phoneIsReal ? (
                    <a
                      href={`tel:${siteConfig.phone.replace(/\s/g, "")}`}
                      className="text-text hover:text-accent"
                    >
                      {siteConfig.phone}
                    </a>
                  ) : (
                    <span className="text-text">{siteConfig.phone}</span>
                  )}
                </span>
              </li>
              <li className="flex items-start gap-3">
                <MapPin aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
                <span className="flex flex-col">
                  <span className="t-small text-text-muted">{dict.contact.cityLabel}</span>
                  <span className="text-text">{siteConfig.city}</span>
                </span>
              </li>
              <li className="flex items-start gap-3">
                <Clock aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
                <span className="flex flex-col">
                  <span className="t-small text-text-muted">{dict.contact.responseLabel}</span>
                  <span className="text-text">{siteConfig.responseTime[typedLocale]}</span>
                </span>
              </li>
            </ul>

            <div className="border-t border-border pt-5">
              <h3 className="t-small mb-3 font-medium uppercase tracking-[0.12em] text-text">
                {dict.contact.followLabel}
              </h3>
              <ul className="flex flex-col gap-2 text-[15px] text-text-muted">
                {socials.map((social) => (
                  <li key={social.label}>
                    {isPlaceholder(social.href) ? (
                      <span>
                        {social.label} <span className="text-text-muted/70">{social.href}</span>
                      </span>
                    ) : (
                      <a
                        href={social.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-accent"
                      >
                        {social.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </Card>

          <Card interactive={false} className="flex flex-col gap-5 p-7">
            <h2 className="t-h3 text-text">{dict.contact.faqTitle}</h2>
            <ul className="flex flex-col gap-5">
              {dict.contact.faq.map((item) => (
                <li key={item.q}>
                  <h3 className="text-[15px] font-medium text-text">{item.q}</h3>
                  <p className="t-small mt-1.5 text-text-muted">{item.a}</p>
                </li>
              ))}
            </ul>
            <p className="t-small text-text-muted">
              <Link href={`/${typedLocale}/pricing`} className="text-accent hover:underline">
                {dict.home.pricingLink}
              </Link>
              {" · "}
              <Link href={`/${typedLocale}/portfolio`} className="text-accent hover:underline">
                {dict.common.seeDemos}
              </Link>
            </p>
          </Card>
        </aside>
      </div>
    </Container>
  );
}
