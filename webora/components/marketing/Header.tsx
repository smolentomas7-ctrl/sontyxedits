"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { AnimatedLogo } from "@/components/ui/AnimatedLogo";
import { ButtonLink } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { cn } from "@/lib/utils";
import type { Dictionary, Locale } from "@/content/i18n";

/** Scroll distance after which the header gains its background. */
const SCROLL_THRESHOLD = 40;

export function Header({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const links = [
    { href: `/${locale}/services`, label: dict.nav.services },
    { href: `/${locale}/portfolio`, label: dict.nav.portfolio },
    { href: `/${locale}/features`, label: dict.nav.features },
    { href: `/${locale}/blog`, label: dict.nav.blog },
    { href: `/${locale}/about`, label: dict.nav.about },
    { href: `/${locale}/contact`, label: dict.nav.contact },
  ];

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > SCROLL_THRESHOLD);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close the overlay whenever the route changes.
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  // Lock scroll and wire Escape while the overlay is open.
  useEffect(() => {
    if (!menuOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setMenuOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [menuOpen]);

  /** Swaps the locale segment while keeping the rest of the path. */
  const otherLocale: Locale = locale === "sk" ? "en" : "sk";
  const switchedPath = (() => {
    const segments = (pathname ?? `/${locale}`).split("/");
    // segments[0] is "" because the path starts with a slash.
    if (segments.length > 1) segments[1] = otherLocale;
    return segments.join("/") || `/${otherLocale}`;
  })();

  function isActive(href: string) {
    if (!pathname) return false;
    return pathname === href || pathname.startsWith(`${href}/`);
  }

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-[background-color,border-color,backdrop-filter] duration-200",
        scrolled
          ? "border-b border-border bg-bg/80 backdrop-blur-xl"
          : "border-b border-transparent bg-transparent",
      )}
    >
      <Container>
        <div className="flex h-16 items-center justify-between gap-6 md:h-20">
          <AnimatedLogo locale={locale} label={dict.nav.logoLabel} priority />

          <nav aria-label={dict.common.menu} className="hidden lg:block">
            <ul className="flex items-center gap-1">
              {links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    aria-current={isActive(link.href) ? "page" : undefined}
                    className={cn(
                      "rounded-lg px-3 py-2 text-[15px] transition-colors duration-150",
                      isActive(link.href)
                        ? "text-accent"
                        : "text-text-muted hover:text-text",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div className="flex items-center gap-2">
            <Link
              href={switchedPath}
              hrefLang={otherLocale}
              aria-label={`${dict.nav.switchLanguage}: ${otherLocale.toUpperCase()}`}
              className="rounded-lg border border-border px-2.5 py-1.5 text-[13px] font-medium uppercase text-text-muted transition-colors duration-150 hover:border-text-muted hover:text-text"
            >
              {otherLocale}
            </Link>

            <ButtonLink
              href={`/${locale}/contact`}
              size="sm"
              className="hidden sm:inline-flex"
            >
              {dict.common.getQuote}
            </ButtonLink>

            <button
              type="button"
              onClick={() => setMenuOpen(true)}
              aria-label={dict.nav.openMenu}
              aria-expanded={menuOpen}
              className="inline-flex size-10 items-center justify-center rounded-lg border border-border text-text transition-colors duration-150 hover:bg-surface lg:hidden"
            >
              <Menu aria-hidden="true" strokeWidth={1.5} className="size-5" />
            </button>
          </div>
        </div>
      </Container>

      {menuOpen ? (
        <div className="fixed inset-0 z-50 bg-bg lg:hidden">
          <Container>
            <div className="flex h-16 items-center justify-between md:h-20">
              <AnimatedLogo locale={locale} label={dict.nav.logoLabel} />
              <button
                type="button"
                onClick={() => setMenuOpen(false)}
                aria-label={dict.nav.closeMenu}
                autoFocus
                className="inline-flex size-10 items-center justify-center rounded-lg border border-border text-text transition-colors duration-150 hover:bg-surface"
              >
                <X aria-hidden="true" strokeWidth={1.5} className="size-5" />
              </button>
            </div>

            <nav aria-label={dict.common.menu} className="mt-8">
              <ul className="flex flex-col gap-1">
                <li>
                  <Link
                    href={`/${locale}`}
                    className="block border-b border-border py-4 font-[family-name:var(--font-space-grotesk)] text-2xl text-text"
                  >
                    {dict.nav.home}
                  </Link>
                </li>
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      aria-current={isActive(link.href) ? "page" : undefined}
                      className={cn(
                        "block border-b border-border py-4 font-[family-name:var(--font-space-grotesk)] text-2xl",
                        isActive(link.href) ? "text-accent" : "text-text",
                      )}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>

            <ButtonLink href={`/${locale}/contact`} className="mt-8 w-full">
              {dict.common.getQuote}
            </ButtonLink>
          </Container>
        </div>
      ) : null}
    </header>
  );
}
