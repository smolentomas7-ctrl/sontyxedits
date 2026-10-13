"use client";

import clsx from "clsx";
import { Menu, Phone, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { site } from "@/config/miauto";
import { ROUTES, path } from "@/lib/i18n";
import { usePressHandlers } from "@/lib/motion";
import { LangSwitcher } from "./LangSwitcher";
import { Logo } from "@/components/brand/Logo";
import type { Locale, LocaleContent } from "@/content/types";

export function Nav({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const [closing, setClosing] = useState(false);
  const pathname = usePathname();
  const toggleRef = useRef<HTMLButtonElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const press = usePressHandlers();

  // Transparent over the hero; after 40px of scroll it gains a blurred
  // background and a hairline bottom border.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const close = useCallback(() => {
    setClosing(true);
    window.setTimeout(() => {
      setOpen(false);
      setClosing(false);
      toggleRef.current?.focus();
    }, 200);
  }, []);

  useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
        return;
      }
      if (event.key !== "Tab") return;

      // Focus trap.
      const focusables = panelRef.current?.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if (!focusables || focusables.length === 0) return;
      const first = focusables[0] as HTMLElement;
      const last = focusables[focusables.length - 1] as HTMLElement;
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    document.body.style.overflow = "hidden";
    // Move focus into the panel when it opens.
    window.setTimeout(() => {
      panelRef.current?.querySelector<HTMLElement>("a[href]")?.focus();
    }, 50);

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, close]);

  const links = [
    { href: path(locale, ROUTES.services), label: t.nav.services },
    { href: path(locale, ROUTES.about), label: t.nav.about },
    { href: path(locale, ROUTES.contact), label: t.nav.contact },
  ];

  return (
    <header
      className={clsx(
        "fixed inset-x-0 top-0 z-50 transition-[background-color,border-color,backdrop-filter] duration-[var(--dur-state)] ease-[var(--ease-ios-in)]",
        scrolled
          ? "border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_80%,transparent)] backdrop-blur-xl"
          : "border-b border-transparent bg-transparent",
      )}
      style={{ height: "var(--nav-h)" }}
    >
      <div className="container flex h-[var(--nav-h)] items-center justify-between gap-4">
        <Link
          href={path(locale)}
          className="tappable -mx-2 flex items-center rounded-[var(--radius-control)] px-2 py-1 no-underline"
          aria-label={site.legalName}
          {...press}
        >
          <Logo />
        </Link>

        <nav aria-label={t.nav.services} className="hidden items-center gap-1 md:flex">
          {links.map((link) => {
            const active = pathname?.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={clsx(
                  "tappable rounded-[var(--radius-control)] px-3.5 py-2 text-[0.9375rem] font-medium no-underline",
                  active
                    ? "text-[color:var(--accent)]"
                    : "text-[color:var(--text-muted)] hover:text-[color:var(--text)]",
                )}
                style={{ ["--press-scale" as string]: "0.97" }}
                {...press}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <LangSwitcher locale={locale} t={t} className="hidden sm:inline-flex" />
          <a
            href={site.phoneHref}
            aria-label={t.common.callAria}
            className="tappable hidden h-10 items-center gap-2 rounded-[var(--radius-pill)] bg-[var(--accent)] px-4 text-[0.875rem] font-semibold text-[color:var(--accent-ink)] no-underline hover:bg-[var(--accent-hover)] lg:inline-flex"
            {...press}
          >
            <Phone size={16} aria-hidden="true" />
            {site.phone}
          </a>

          <button
            ref={toggleRef}
            type="button"
            onClick={() => (open ? close() : setOpen(true))}
            aria-expanded={open}
            aria-label={open ? t.common.closeMenu : t.common.menu}
            className="tappable inline-flex size-11 items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] text-[color:var(--text)] md:hidden"
            {...press}
          >
            {open ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}
          </button>
        </div>
      </div>

      {open ? (
        <div
          ref={panelRef}
          role="dialog"
          aria-modal="true"
          aria-label={t.common.menu}
          data-open={closing ? "false" : "true"}
          data-closing={closing ? "true" : "false"}
          className="overlay-enter fixed inset-0 top-0 z-50 flex h-[100dvh] flex-col bg-[var(--bg)] px-[var(--gutter)] pb-10 pt-[calc(var(--nav-h)+24px)] md:hidden"
        >
          <nav aria-label={t.common.menu} className="flex flex-col">
            {links.map((link, i) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={close}
                className="tappable border-b border-[var(--border)] py-5 font-heading text-[1.75rem] font-semibold tracking-[-0.02em] no-underline"
                style={{ ["--press-scale" as string]: "0.99", transitionDelay: `${i * 20}ms` }}
                {...press}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="mt-auto flex flex-col gap-4 pt-8">
            <LangSwitcher locale={locale} t={t} className="self-start" />
            <a
              href={site.phoneHref}
              aria-label={t.common.callAria}
              className="tappable inline-flex h-[52px] items-center justify-center gap-2 rounded-[var(--radius-control)] bg-[var(--accent)] font-semibold text-[color:var(--accent-ink)] no-underline"
              {...press}
            >
              <Phone size={18} aria-hidden="true" />
              {site.phone}
            </a>
          </div>
        </div>
      ) : null}
    </header>
  );
}
