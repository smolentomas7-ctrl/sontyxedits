"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import { DEMO_BAR_HEIGHT } from "./DemoBar";

export type NavLink = { href: string; label: string };

/**
 * Shared mobile-capable header for the demos. Colors come in as props so each
 * demo keeps its own identity while the behaviour stays consistent.
 */
export function DemoNav({
  brand,
  links,
  action,
  bg,
  fg,
  border,
  accent,
  fontClass,
}: {
  brand: React.ReactNode;
  links: NavLink[];
  action?: { href: string; label: string };
  bg: string;
  fg: string;
  border: string;
  accent: string;
  fontClass?: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <header
      className="sticky z-40 border-b backdrop-blur"
      style={{ top: DEMO_BAR_HEIGHT, background: bg, borderColor: border, color: fg }}
    >
      <div className="mx-auto flex h-16 max-w-[1200px] items-center justify-between gap-6 px-5 md:h-20 md:px-8">
        <a href="#top" className={fontClass} style={{ color: fg }}>
          {brand}
        </a>

        <nav aria-label="Hlavné menu" className="hidden md:block">
          <ul className="flex items-center gap-7">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  className="text-[15px] transition-opacity duration-150 hover:opacity-65"
                  style={{ color: fg }}
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex items-center gap-3">
          {action ? (
            <a
              href={action.href}
              className="hidden rounded-lg px-4 py-2.5 text-[14px] font-medium transition-opacity duration-150 hover:opacity-85 sm:inline-flex"
              style={{ background: accent, color: bg }}
            >
              {action.label}
            </a>
          ) : null}

          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? "Zavrieť menu" : "Otvoriť menu"}
            aria-expanded={open}
            className="inline-flex size-10 items-center justify-center rounded-lg border md:hidden"
            style={{ borderColor: border, color: fg }}
          >
            {open ? (
              <X aria-hidden="true" strokeWidth={1.5} className="size-5" />
            ) : (
              <Menu aria-hidden="true" strokeWidth={1.5} className="size-5" />
            )}
          </button>
        </div>
      </div>

      {open ? (
        <nav
          aria-label="Mobilné menu"
          className="border-t md:hidden"
          style={{ borderColor: border, background: bg }}
        >
          <ul className="mx-auto flex max-w-[1200px] flex-col px-5 py-2">
            {links.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="block border-b py-3.5 text-[16px]"
                  style={{ borderColor: border, color: fg }}
                >
                  {link.label}
                </a>
              </li>
            ))}
            {action ? (
              <li className="py-3">
                <a
                  href={action.href}
                  onClick={() => setOpen(false)}
                  className="block rounded-lg px-4 py-3 text-center text-[15px] font-medium"
                  style={{ background: accent, color: bg }}
                >
                  {action.label}
                </a>
              </li>
            ) : null}
          </ul>
        </nav>
      ) : null}
    </header>
  );
}
