"use client";

import { Phone } from "lucide-react";
import { useEffect, useState } from "react";
import { site } from "@/config/miauto";
import { usePressHandlers } from "@/lib/motion";
import type { LocaleContent } from "@/content/types";

/**
 * Sticky bottom call bar below 768px. Slides up once after 120px of scroll and
 * stays — it does not reappear and re-hide as the visitor scrolls around.
 *
 * It sits at z-40 and the page reserves space for it, so the chat launcher
 * (z-50, offset above this bar's height) never covers it and it never covers
 * the launcher.
 */
export function MobileCallBar({ t }: { t: LocaleContent }) {
  const [shown, setShown] = useState(false);
  const press = usePressHandlers();

  useEffect(() => {
    if (shown) return;
    const onScroll = () => {
      if (window.scrollY > 120) setShown(true);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [shown]);

  return (
    <div
      className="call-bar fixed inset-x-0 bottom-0 z-40 border-t border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_92%,transparent)] p-3 backdrop-blur-xl md:hidden"
      data-shown={shown ? "true" : "false"}
      style={{ paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))" }}
    >
      <a
        href={site.phoneHref}
        aria-label={t.common.callAria}
        className="tappable flex h-12 w-full items-center justify-center gap-2 rounded-[var(--radius-control)] bg-[var(--accent)] font-semibold text-[color:var(--accent-ink)] no-underline"
        {...press}
      >
        <Phone size={18} aria-hidden="true" />
        {t.common.callCta} {site.phone}
      </a>
    </div>
  );
}
