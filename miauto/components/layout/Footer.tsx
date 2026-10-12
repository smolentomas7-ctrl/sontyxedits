import Link from "next/link";
import { SERVICE_SLUGS } from "@/content/types";
import { formattedAddress, isPlaceholder, site } from "@/config/miauto";
import { ROUTES, path, servicePath } from "@/lib/i18n";
import { PlaceholderToken } from "@/components/ui/Placeholder";
import { Wordmark } from "./Wordmark";
import type { Locale, LocaleContent } from "@/content/types";

export function Footer({ locale, t }: { locale: Locale; t: LocaleContent }) {
  // Social links render only when their value is a real URL, never as "[FACEBOOK_URL]".
  const social = [
    { href: site.social.facebook, label: "Facebook" },
    { href: site.social.instagram, label: "Instagram" },
  ].filter((item) => !isPlaceholder(item.href));

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--bg)]">
      <div className="container grid gap-12 py-16 md:grid-cols-[1.4fr_1fr_1fr] md:gap-8 md:py-20">
        <div>
          <Wordmark className="text-[1.25rem]" />
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
              <p className="flex flex-wrap items-center gap-2">
                {isPlaceholder(site.email) ? (
                  <PlaceholderToken>{site.email}</PlaceholderToken>
                ) : (
                  <a href={`mailto:${site.email}`} className="no-underline hover:text-[color:var(--text)]">
                    {site.email}
                  </a>
                )}
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
        <div className="container flex flex-wrap items-center justify-between gap-x-6 gap-y-3 py-6 text-[0.8125rem] text-[color:var(--text-muted)]">
          <p>
            © {new Date().getFullYear()} {site.legalName}. {t.footer.rights}
          </p>
          <p className="flex items-center gap-2">
            {t.footer.icoLabel}:{" "}
            {isPlaceholder(site.ico) ? (
              <PlaceholderToken>{site.ico}</PlaceholderToken>
            ) : (
              <span>{site.ico}</span>
            )}
          </p>
        </div>
      </div>
    </footer>
  );
}
