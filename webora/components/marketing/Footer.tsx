import Link from "next/link";
import { Mail } from "lucide-react";
import { Container } from "@/components/ui/Container";
import { AnimatedLogo } from "@/components/ui/AnimatedLogo";
import { WhatsAppIcon } from "@/components/ui/WhatsAppIcon";
import { siteConfig, isPlaceholder, mailtoHref } from "@/config/site";
import type { Dictionary, Locale } from "@/content/i18n";

export function Footer({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const year = new Date().getFullYear();

  const pages = [
    { href: `/${locale}/services`, label: dict.nav.services },
    { href: `/${locale}/portfolio`, label: dict.nav.portfolio },
    { href: `/${locale}/features`, label: dict.nav.features },
    { href: `/${locale}/blog`, label: dict.nav.blog },
    { href: `/${locale}/contact`, label: dict.nav.contact },
  ];

  return (
    <footer className="border-t border-border bg-bg">
      <Container>
        <div className="grid gap-12 py-16 md:grid-cols-[1.6fr_1fr_1.2fr] md:py-20">
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

          {/* The only two contact routes on the site. Both are real links. */}
          <div>
            <h2 className="t-small mb-4 font-medium uppercase tracking-[0.14em] text-text">
              {dict.footer.contactTitle}
            </h2>
            <ul className="flex flex-col gap-3 text-[15px] text-text-muted">
              <li>
                <a
                  href={mailtoHref(dict.contact.mailSubject)}
                  className="inline-flex items-center gap-2.5 transition-colors duration-150 hover:text-accent"
                >
                  <Mail aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
                  {siteConfig.email}
                </a>
              </li>
              <li>
                <a
                  href={siteConfig.whatsapp.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`${dict.contact.whatsappCta} — ${siteConfig.whatsapp.display}`}
                  className="inline-flex items-center gap-2.5 transition-colors duration-150 hover:text-[#4AE08A]"
                >
                  <WhatsAppIcon className="size-4 shrink-0" />
                  {siteConfig.whatsapp.display}
                </a>
              </li>
            </ul>
          </div>
        </div>

        {isPlaceholder(siteConfig.companyId) ? (
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
