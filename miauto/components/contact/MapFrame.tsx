"use client";

import clsx from "clsx";
import { ExternalLink, MapPin } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { formattedAddress, site } from "@/config/miauto";
import { ButtonLink } from "@/components/ui/Button";
import type { LocaleContent } from "@/content/types";

/**
 * The Google Maps embed, with its states handled properly.
 *
 * A cross-origin iframe paints its own opaque background, so a map that fails
 * to load leaves a glaring white rectangle in the middle of a dark page. The
 * iframe's own `load` event is no help: it fires for the browser's error page
 * too, so "loaded" and "failed" look identical from here.
 *
 * So the component probes first. A no-cors request to Google resolves opaquely
 * when Google is reachable and rejects when it is not — blocked by an extension,
 * blocked by a network, or offline. The iframe is only mounted after the probe
 * succeeds; otherwise the visitor keeps a styled panel carrying the address and
 * a directions link, and the section never collapses or flashes white.
 *
 * The probe is itself a request to Google, which is exactly what the privacy
 * notice beside this component already discloses. It is shared process-wide, so
 * however many maps are on a page the probe goes out once. On the home page
 * nothing runs at all until the visitor clicks to load the map.
 */
let probe: Promise<boolean> | null = null;

function googleReachable(): Promise<boolean> {
  if (probe) return probe;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4000);
  probe = fetch("https://www.google.com/favicon.ico", {
    mode: "no-cors",
    cache: "no-store",
    signal: controller.signal,
  })
    .then(() => true)
    .catch(() => false)
    .finally(() => clearTimeout(timeout));
  return probe;
}

export function MapFrame({
  t,
  className,
  /** Fixed aspect ratio. Omit for the responsive box: 4:3 mobile, 16:9 desktop. */
  ratio,
}: {
  t: LocaleContent;
  className?: string;
  ratio?: string;
}) {
  const [reachable, setReachable] = useState<boolean | null>(null);
  const [loaded, setLoaded] = useState(false);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    void googleReachable().then((ok) => {
      if (alive.current) setReachable(ok);
    });
    return () => {
      alive.current = false;
    };
  }, []);

  return (
    <div
      className={clsx(
        "relative overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)]",
        !ratio && "map-ratio",
        className,
      )}
      // Box reserved before anything loads, so CLS stays at zero whatever happens.
      style={ratio ? { aspectRatio: ratio } : undefined}
    >
      <div className="absolute inset-0 grid place-items-center p-7 text-center">
        <div>
          <MapPin
            size={28}
            aria-hidden="true"
            className="mx-auto mb-4 text-[color:var(--text-muted)]"
          />
          <p className="font-heading text-[1.0625rem] font-semibold">{formattedAddress}</p>
          {reachable === false ? (
            <>
              <p className="mx-auto mt-3 max-w-[34ch] text-[0.875rem] text-[color:var(--text-muted)]">
                {t.contact.mapDisclosure}
              </p>
              <ButtonLink
                href={site.mapDirectionsUrl}
                variant="secondary"
                external
                className="mt-5"
              >
                {t.common.navigateCta}
                <ExternalLink size={16} aria-hidden="true" />
              </ButtonLink>
            </>
          ) : null}
        </div>
      </div>

      {reachable ? (
        <iframe
          src={site.mapEmbedUrl}
          title={t.contact.mapTitle}
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          onLoad={() => setLoaded(true)}
          className="absolute inset-0 size-full border-0 transition-opacity duration-[var(--dur-reveal)] ease-[var(--ease-ios)]"
          style={{ opacity: loaded ? 1 : 0, pointerEvents: loaded ? "auto" : "none" }}
        />
      ) : null}
    </div>
  );
}
