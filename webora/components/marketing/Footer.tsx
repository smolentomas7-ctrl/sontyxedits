import Link from "next/link";
import { Mail, Phone, MapPin } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { AnimatedLogo } from "@/components/ui/AnimatedLogo";
import { siteConfig, isPlaceholder } from "@/config/site";
import type { Dictionary, Locale } from "@/content/i18n";

export function Footer({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const year = new Date().getFullYear();

  const pages = [
    { href: `/${locale}/services`, label: dict.nav.services },
    { href: `/${locale}/portfolio`, label: dict.nav.portfolio },
    { href: `/${locale}/features`, label: dict.nav.features },
    { href: `/${locale}/blog`, label: dict.nav.blog },
    { href: `/${locale}/about`, label: dict.nav.about },
    { href: `/${locale}/contact`, label: dict.nav.contact },
  ];

  const socials = [
    { label: "Instagram", href: siteConfig.social.instagram },
    { label: "Facebook", href: siteConfig.social.facebook },
    { label: "LinkedIn", href: siteConfig.social.linkedin },
  ];

  // Placeholder contact values must not become mailto:/tel: links.
  const emailIsReal = !isPlaceholder(siteConfig.email);
  const phoneIsReal = !isPlaceholder(siteConfig.phone);
  const anyPlaceholder =
    !emailIsReal ||
    !phoneIsReal ||
    isPlaceholder(siteConfig.city) ||
    socials.some((s) => isPlaceholder(s.href));

  return (
    <footer className="border-t border-border bg-bg">
      <Container>
        <div className="grid gap-12 py-16 md:grid-cols-[1.4fr_1fr_1fr_1fr] md:py-20">
          <div className="flex flex-col gap-4">
            <AnimatedLogo locale={locale} label={dict.nav.logoLabel} />
            <p className="max-w-[32ch] text-[15px] text-text-muted">{dict.footer.tagline}</p>
          </div>

          <nav aria-label={dict.footer.navTitle}>
            <h2 className="t-small mb-4 font-medium uppercase tracking-[0.14em] text-text">
              {dict.footer.navTitle}
            </h2>
            <ul className="flex flex-col gap-2.5">
              {pages.map((page) => (
                <li key={page.href}>
                  <Link
                    href={page.href}
                    className="text-[15px] text-text-muted transition-colors duration-150 hover:text-accent"
                  >
                    {page.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <h2 className="t-small mb-4 font-medium uppercase tracking-[0.14em] text-text">
              {dict.footer.contactTitle}
            </h2>
            <ul className="flex flex-col gap-2.5 text-[15px] text-text-muted">
              <li className="flex items-center gap-2">
                <Mail aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
                {emailIsReal ? (
                  <a
                    href={`mailto:${siteConfig.email}`}
                    className="transition-colors duration-150 hover:text-accent"
                  >
                    {siteConfig.email}
                  </a>
                ) : (
                  <span>{siteConfig.email}</span>
                )}
              </li>
              <li className="flex items-center gap-2">
                <Phone aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
                {phoneIsReal ? (
                  <a
                    href={`tel:${siteConfig.phone.replace(/\s/g, "")}`}
                    className="transition-colors duration-150 hover:text-accent"
                  >
                    {siteConfig.phone}
                  </a>
                ) : (
                  <span>{siteConfig.phone}</span>
                )}
              </li>
              <li className="flex items-center gap-2">
                <MapPin aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
                <span>{siteConfig.city}</span>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="t-small mb-4 font-medium uppercase tracking-[0.14em] text-text">
              {dict.footer.socialTitle}
            </h2>
            <ul className="flex flex-col gap-2.5 text-[15px] text-text-muted">
              {socials.map((social) => (
                <li key={social.label}>
                  {isPlaceholder(social.href) ? (
                    <span>
                      {social.label} <span className="text-text-muted">{social.href}</span>
                    </span>
                  ) : (
                    <a
                      href={social.href}
                      rel="noopener noreferrer"
                      target="_blank"
                      className="transition-colors duration-150 hover:text-accent"
                    >
                      {social.label}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {anyPlaceholder ? (
          <p className="mb-6 rounded-lg border border-border bg-surface px-4 py-3 text-[13px] text-text-muted">
            {dict.footer.placeholderNote}
          </p>
        ) : null}

        <div className="flex flex-col gap-3 border-t border-border py-6 text-[13px] text-text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {year} {siteConfig.name}. {dict.common.allRightsReserved}{" "}
            <span className="whitespace-nowrap">IČO: {siteConfig.companyId}</span>
          </p>
          <Link
            href={`/${locale}/legal/privacy`}
            className="transition-colors duration-150 hover:text-accent"
          >
            {dict.common.privacy}
          </Link>
        </div>
      </Container>
    </footer>
  );
}
