import Link from "next/link";
import { SERVICE_SLUGS } from "@/content/types";
import { formattedAddress, has, mailtoHref, site } from "@/config/miauto";
import { ROUTES, path, servicePath } from "@/lib/i18n";
import { Logo } from "@/components/brand/Logo";
import type { Locale, LocaleContent } from "@/content/types";

export function Footer({ locale, t }: { locale: Locale; t: LocaleContent }) {
  // Social links exist only when a real URL does; no dead icons.
  const social = [
    { href: site.social.facebook, label: "Facebook" },
    { href: site.social.instagram, label: "Instagram" },
  ].filter((item) => has(item.href));

  /**
   * § 3a of the Slovak Commercial Code requires the company number and the
   * commercial-register entry on a business website. Each line appears as soon
   * as config/miauto.ts holds it, and nothing is invented to fill the gap.
   */
  const registration = [
    { label: t.footer.icoLabel, value: site.ico },
    { label: t.footer.dicLabel, value: site.dic },
    { label: t.footer.icDphLabel, value: site.icDph },
    { label: t.footer.registryLabel, value: site.zapisVOR },
  ].filter((item) => has(item.value));

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--bg)]">
      <div className="container grid gap-12 py-16 md:grid-cols-[1.4fr_1fr_1fr] md:gap-8 md:py-20">
        <div>
          <Logo markClassName="size-11" wordmarkClassName="text-[1.25rem] md:text-[1.375rem]" />
          <p className="prose-width mt-4 max-w-[34ch] text-[color:var(--text-muted)]">
            {t.footer.tagline}
          </p>
          {social.length > 0 ? (
            <ul className="mt-6 flex gap-4">
              {social.map((item) => (
                <li key={item.label}>
                  <a
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[0.9375rem] text-[color:var(--text-muted)] hover:text-[color:var(--text)]"
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          ) : null}
        </div>

        <div>
          <h2 className="mb-4 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
            {t.footer.servicesHeading}
          </h2>
          <ul className="space-y-2.5">
            {SERVICE_SLUGS.map((slug) => (
              <li key={slug}>
                <Link
                  href={servicePath(locale, slug)}
                  className="text-[0.9375rem] text-[color:var(--text-muted)] no-underline hover:text-[color:var(--text)]"
                >
                  {t.services[slug].name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="mb-4 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
              {t.footer.contactHeading}
            </h2>
            <address className="space-y-2.5 not-italic text-[0.9375rem] text-[color:var(--text-muted)]">
              <p>{formattedAddress}</p>
              <p>
                <a
                  href={site.phoneHref}
                  className="font-semibold text-[color:var(--text)] no-underline hover:text-[color:var(--accent)]"
                >
                  {site.phone}
                </a>
              </p>
              <p>
                <a href={mailtoHref} className="no-underline hover:text-[color:var(--text)]">
                  {site.email}
                </a>
              </p>
            </address>
          </div>

          <div>
            <h2 className="mb-4 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
              {t.footer.legalHeading}
            </h2>
            <ul className="space-y-2.5">
              <li>
                <Link
                  href={path(locale, ROUTES.privacy)}
                  className="text-[0.9375rem] text-[color:var(--text-muted)] no-underline hover:text-[color:var(--text)]"
                >
                  {t.nav.privacy}
                </Link>
              </li>
              <li>
                <Link
                  href={path(locale, ROUTES.about)}
                  className="text-[0.9375rem] text-[color:var(--text-muted)] no-underline hover:text-[color:var(--text)]"
                >
                  {t.nav.about}
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="border-t border-[var(--border)]">
        {/* The chat launcher is fixed to the bottom right, so the last line of
            the page keeps clear of it on the narrow layout where they collide. */}
        <div className="container flex flex-wrap items-center justify-between gap-x-6 gap-y-3 py-6 pb-24 text-[0.8125rem] text-[color:var(--text-muted)] md:pb-6">
          <p>
            {/* The legal name ends in a full stop of its own, hence the middle dot. */}
            © {new Date().getFullYear()} {site.legalName} · {t.footer.rights}
          </p>
          {registration.length > 0 ? (
            <p className="flex flex-wrap items-center gap-x-4 gap-y-1">
              {registration.map((item) => (
                <span key={item.label}>
                  {item.label}: {item.value}
                </span>
              ))}
            </p>
          ) : null}
        </div>
      </div>
    </footer>
  );
}
