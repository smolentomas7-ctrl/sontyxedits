import Image from "next/image";
import { MapPin } from "lucide-react";
import { images } from "@/config/images";
import { formattedAddress, site } from "@/config/miauto";
import { ROUTES, path } from "@/lib/i18n";
import { ButtonLink } from "@/components/ui/Button";
import { Parallax } from "@/components/ui/Parallax";
import { OpenBadge } from "@/components/ui/HoursTable";
import type { Locale, LocaleContent } from "@/content/types";

export function Hero({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const slot = images.hero;

  return (
    <section
      data-parallax-area=""
      className="relative isolate flex min-h-[86svh] items-end overflow-hidden pb-14 pt-[calc(var(--nav-h)+64px)] md:min-h-[92svh] md:pb-24"
    >
      {/* The hero bleeds full-width past the container on every edge. */}
      <div className="absolute inset-0 -z-10" style={{ backgroundColor: slot.placeholder }}>
        {/* The photograph answers the cursor across the whole hero; the scrims
            below it do not, and that difference is the depth. */}
        <Parallax className="absolute inset-0" shift={8} tilt={0.6}>
          <Image
            src={slot.src}
            alt={t.home.heroImageAlt}
            fill
            priority
            sizes="100vw"
            className="hero-image object-cover"
          />
        </Parallax>
        {/* Scrim, in two passes. The vertical pass sits the text block on solid
            ground; the horizontal one is weighted left so the headline column
            keeps its contrast while the right half of the photograph stays
            readable. Below 768px there is no second column to protect — the two
            scrims would stack over the whole frame and leave the photograph
            black — so the horizontal pass drops out and the vertical one carries
            the text alone. Both measured on the headline, not estimated. */}
        <div
          aria-hidden="true"
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(to top, var(--bg) 4%, color-mix(in srgb, var(--bg) 90%, transparent) 36%, color-mix(in srgb, var(--bg) 58%, transparent) 64%, color-mix(in srgb, var(--bg) 38%, transparent) 100%)",
          }}
        />
        <div
          aria-hidden="true"
          className="absolute inset-0 hidden md:block"
          style={{
            background:
              "linear-gradient(to right, color-mix(in srgb, var(--bg) 94%, transparent) 0%, color-mix(in srgb, var(--bg) 86%, transparent) 34%, color-mix(in srgb, var(--bg) 42%, transparent) 62%, transparent 86%)",
          }}
        />
      </div>

      <div className="container">
        <h1 className="max-w-[18ch]">
          {t.home.heroTitle}
          <span className="mt-3 block text-[0.5em] font-600 leading-[1.15] text-[color:var(--text-muted)]">
            {t.home.heroTitleSecond}
          </span>
        </h1>

        <p className="mt-7 max-w-[46ch] text-[1.0625rem] text-[color:var(--text)] md:text-[1.125rem]">
          {t.home.heroLead}
        </p>

        <div className="mt-9 flex flex-wrap gap-3">
          <ButtonLink href={site.phoneHref} size="lg" aria-label={t.common.callAria}>
            {t.common.callCta}
          </ButtonLink>
          <ButtonLink href={path(locale, ROUTES.services)} size="lg" variant="secondary">
            {t.common.servicesCta}
          </ButtonLink>
        </div>

        <p className="mt-7 flex flex-col gap-y-1.5 text-[0.9375rem] text-[color:var(--text-muted)] sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-3">
          <span className="inline-flex items-center gap-2">
            <MapPin size={16} aria-hidden="true" className="shrink-0" />
            {formattedAddress}
          </span>
          <span aria-hidden="true" className="hidden opacity-40 sm:inline">
            ·
          </span>
          <OpenBadge t={t} />
        </p>
      </div>
    </section>
  );
}
