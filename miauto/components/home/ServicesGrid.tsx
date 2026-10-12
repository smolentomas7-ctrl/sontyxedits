import clsx from "clsx";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { SERVICE_SLUGS } from "@/content/types";
import { servicePath } from "@/lib/i18n";
import { Reveal } from "@/components/ui/Reveal";
import { ServiceIcon } from "@/components/ui/ServiceIcon";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * Not seven identical cards. Diagnostics spans two columns because it is the
 * entry point for most faults, so scale does the ranking rather than colour.
 */
export function ServicesGrid({ locale, t }: { locale: Locale; t: LocaleContent }) {
  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {SERVICE_SLUGS.map((slug, index) => {
        const service = t.services[slug];
        const wide = index === 0;
        return (
          <Reveal
            as="li"
            key={slug}
            index={index}
            className={clsx(wide && "sm:col-span-2")}
          >
            <article
              className={clsx(
                "card tappable tappable--card relative flex h-full flex-col p-6 md:p-7",
                wide && "lg:p-9",
              )}
            >
              <span
                className={clsx(
                  "mb-5 inline-flex items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--bg)] text-[color:var(--accent)]",
                  wide ? "size-14" : "size-12",
                )}
              >
                <ServiceIcon name={service.icon} size={wide ? 26 : 22} />
              </span>

              <h3
                className={clsx(
                  "font-heading font-semibold tracking-[-0.02em]",
                  wide ? "text-[1.5rem] md:text-[1.875rem]" : "text-[1.1875rem]",
                )}
              >
                {/* The one real anchor; the overlay makes the whole card the target. */}
                <Link href={servicePath(locale, slug)} className="card-link no-underline">
                  {service.name}
                </Link>
              </h3>

              <p
                className={clsx(
                  "mt-3 text-[color:var(--text-muted)]",
                  wide ? "max-w-[52ch] text-[1.0625rem]" : "text-[0.9375rem]",
                )}
              >
                {service.cardDescription}
              </p>

              <span
                aria-hidden="true"
                className="mt-auto inline-flex items-center gap-2 pt-6 text-[0.875rem] font-medium text-[color:var(--accent)]"
              >
                {t.common.readMore}
                <ArrowRight size={16} />
              </span>
            </article>
          </Reveal>
        );
      })}
    </ul>
  );
}
