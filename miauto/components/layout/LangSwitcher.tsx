"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { otherLocale, swapLocale } from "@/lib/i18n";
import { usePressHandlers } from "@/lib/motion";
import type { Locale, LocaleContent } from "@/content/types";

/** Preserves the current path; slugs are identical across locales. */
export function LangSwitcher({
  locale,
  t,
  className,
}: {
  locale: Locale;
  t: LocaleContent;
  className?: string;
}) {
  const pathname = usePathname() ?? `/${locale}`;
  const target = otherLocale(locale);
  const press = usePressHandlers();

  return (
    <Link
      href={swapLocale(pathname, target)}
      hrefLang={target}
      lang={target}
      aria-label={`${t.common.languageLabel}: ${t.common.switchTo}`}
      className={`tappable inline-flex h-10 items-center rounded-[var(--radius-pill)] border border-[var(--border)] px-3.5 text-[0.8125rem] font-medium text-[color:var(--text-muted)] no-underline hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))] hover:text-[color:var(--text)] ${className ?? ""}`}
      {...press}
    >
      {t.common.switchTo}
    </Link>
  );
}
