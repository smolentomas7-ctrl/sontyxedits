"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { brand } from "@/config/images";
import type { Locale } from "@/content/i18n";
import { cn } from "@/lib/utils";

/**
 * The Webora mark. Always navigates to the current locale's home page, from
 * any route including the demo sites, and scrolls to the top rather than
 * leaving the viewport wherever the previous page happened to be.
 *
 * Already on home: the click is intercepted so it smooth-scrolls to the top
 * instead of pushing a duplicate history entry.
 *
 * Motion is a short press-in plus a mark that lifts and brightens on hover.
 * The accent ring behind the mark fades in rather than scaling, so nothing
 * around the logo shifts and the hit area never moves under the cursor.
 */
export function AnimatedLogo({
  locale,
  label = "Webora — domov",
  className,
  priority = false,
}: {
  locale: Locale;
  label?: string;
  className?: string;
  priority?: boolean;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const home = `/${locale}`;
  const isHome = pathname === home || pathname === `${home}/`;

  function onClick(event: React.MouseEvent<HTMLAnchorElement>) {
    // Let modified clicks (new tab, download) behave normally.
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    if (isHome) {
      event.preventDefault();
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
      return;
    }
    // Pushing then scrolling keeps the new page at the top; Next restores
    // scroll position on back navigation, which is the behaviour we want.
    event.preventDefault();
    router.push(home);
    window.scrollTo({ top: 0 });
  }

  return (
    <Link
      href={home}
      onClick={onClick}
      aria-label={label}
      aria-current={isHome ? "page" : undefined}
      className={cn(
        "group/logo relative inline-flex shrink-0 items-center rounded-lg",
        "transition-transform duration-200 ease-[cubic-bezier(0.32,0.72,0,1)]",
        "active:scale-[0.96] active:duration-75",
        "motion-reduce:transition-none motion-reduce:active:scale-100",
        className,
      )}
    >
      {/* Accent bloom behind the mark. Opacity only — no layout influence. */}
      <span
        aria-hidden="true"
        className={cn(
          "pointer-events-none absolute -inset-x-2 -inset-y-1.5 rounded-xl opacity-0 blur-md",
          "bg-accent/18 transition-opacity duration-300",
          "group-hover/logo:opacity-100 motion-reduce:transition-none",
        )}
      />
      <Image
        src={brand.logoLight.src}
        width={brand.logoLight.width}
        height={brand.logoLight.height}
        alt=""
        priority={priority}
        className={cn(
          "relative h-7 w-auto md:h-8",
          "transition-[transform,filter] duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]",
          "group-hover/logo:-translate-y-px group-hover/logo:brightness-110",
          "motion-reduce:transition-none motion-reduce:group-hover/logo:translate-y-0",
        )}
      />
    </Link>
  );
}
