"use client";

import { ExternalLink, Map as MapIcon } from "lucide-react";
import { useState } from "react";
import { formattedAddress, site } from "@/config/miauto";
import { Button, ButtonLink } from "@/components/ui/Button";
import { HoursTable } from "@/components/ui/HoursTable";
import { MapFrame } from "@/components/contact/MapFrame";
import type { LocaleContent } from "@/content/types";

/**
 * Click-to-load. The home page makes no third-party request until the visitor
 * asks for one, so landing here contacts nobody but this site.
 *
 * If the iframe never loads, the address, phone and directions button beside it
 * stay fully usable and the section does not collapse.
 */
export function MapTeaser({ t }: { t: LocaleContent }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="grid gap-10 lg:grid-cols-[1fr_1.15fr] lg:items-start lg:gap-14">
      <div>
        <h2>{t.home.mapHeading}</h2>
        <p className="mt-5 max-w-[42ch] text-[color:var(--text-muted)]">{t.home.mapLead}</p>

        <div className="mt-8">
          <h3 className="mb-2 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
            {t.common.addressHeading}
          </h3>
          <address className="not-italic">{formattedAddress}</address>
        </div>

        <div className="mt-7">
          <h3 className="mb-3 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
            {t.common.hoursHeading}
          </h3>
          <HoursTable t={t} compact />
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <ButtonLink href={site.mapDirectionsUrl} variant="secondary" external>
            {t.common.navigateCta}
            <ExternalLink size={16} aria-hidden="true" />
          </ButtonLink>
          <ButtonLink href={site.phoneHref} aria-label={t.common.callAria}>
            {site.phone}
          </ButtonLink>
        </div>
      </div>

      <div>
        {loaded ? (
          <MapFrame t={t} ratio="4 / 3" />
        ) : (
          <div
            className="relative overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)]"
            style={{ aspectRatio: "4 / 3" }}
          >
            <div className="absolute inset-0 grid place-items-center p-7 text-center">
              <div>
                <MapIcon
                  size={30}
                  aria-hidden="true"
                  className="mx-auto mb-5 text-[color:var(--text-muted)]"
                />
                <p className="font-heading text-[1.0625rem] font-semibold">{formattedAddress}</p>
                <p className="mx-auto mt-3 max-w-[38ch] text-[0.875rem] text-[color:var(--text-muted)]">
                  {t.home.mapLoadNote}
                </p>
                <Button variant="secondary" className="mt-6" onClick={() => setLoaded(true)}>
                  {t.home.mapLoadButton}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
