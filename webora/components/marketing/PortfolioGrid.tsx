"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { ArrowUpRight, Maximize2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { BrowserFrame } from "@/components/ui/BrowserFrame";
import { Button } from "@/components/ui/Button";
import { Lightbox, type LightboxItem } from "@/components/ui/Lightbox";
import { projects } from "@/content/projects";
import type { Dictionary, Locale } from "@/content/i18n";
import { cn } from "@/lib/utils";

export function PortfolioGrid({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const rawFilter = searchParams.get("filter") ?? "all";
  // Guard against an unknown value arriving in the URL.
  const activeFilter = dict.portfolio.filters.some((f) => f.id === rawFilter) ? rawFilter : "all";

  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const triggerRefs = useRef<Record<string, HTMLButtonElement | null>>({});

  const visible = useMemo(
    () =>
      activeFilter === "all"
        ? projects
        : projects.filter((project) => project.category === activeFilter),
    [activeFilter],
  );

  /** Lightbox walks every project, not just the filtered subset. */
  const lightboxItems: LightboxItem[] = useMemo(
    () =>
      projects.map((project) => ({
        src: project.preview.src,
        width: project.preview.width,
        height: project.preview.height,
        alt: project.preview.alt,
        title: `${project.name} — ${project.industry[locale]}`,
        href: project.href,
        hrefLabel: dict.common.openDemo,
      })),
    [locale, dict.common.openDemo],
  );

  const setFilter = useCallback(
    (id: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (id === "all") {
        params.delete("filter");
      } else {
        params.set("filter", id);
      }
      const query = params.toString();
      // scroll:false keeps the viewport where it is while the grid re-flows.
      router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
    },
    [router, pathname, searchParams],
  );

  return (
    <>
      <div role="group" aria-label={dict.portfolio.filterLabel} className="flex flex-wrap gap-2">
        {dict.portfolio.filters.map((filter) => {
          const isActive = filter.id === activeFilter;
          return (
            <button
              key={filter.id}
              type="button"
              onClick={() => setFilter(filter.id)}
              aria-pressed={isActive}
              className={cn(
                "rounded-full border px-4 py-2 text-[14px] transition-colors duration-150",
                isActive
                  ? "border-accent bg-accent-soft font-medium text-accent"
                  : "border-border text-text-muted hover:border-text-muted hover:text-text",
              )}
            >
              {filter.label}
            </button>
          );
        })}
      </div>

      {visible.length === 0 ? (
        <div className="mt-14 rounded-2xl border border-border bg-surface px-6 py-16 text-center">
          <h2 className="t-h3 text-text">{dict.portfolio.emptyTitle}</h2>
          <p className="mx-auto mt-3 max-w-[44ch] text-text-muted">{dict.portfolio.emptyBody}</p>
          <Button onClick={() => setFilter("all")} variant="secondary" className="mt-7">
            {dict.portfolio.clearFilter}
          </Button>
        </div>
      ) : (
        <ul className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((project, index) => {
            // Index within the full list, so the lightbox opens on the right item.
            const absoluteIndex = projects.findIndex((p) => p.slug === project.slug);

            return (
              <li
                key={project.slug}
                className="flex animate-[fadeIn_0.3s_ease-out_both]"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <Card as="div" className="group flex w-full flex-col overflow-hidden p-4">
                  <BrowserFrame url={`webora.sk${project.href}`}>
                    <div className="relative aspect-[16/10] overflow-hidden bg-bg">
                      <Image
                        src={project.preview.src}
                        alt={project.preview.alt}
                        fill
                        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                        className="object-cover transition-transform duration-300 ease-out group-hover:scale-[1.03]"
                      />
                    </div>
                  </BrowserFrame>

                  <div className="flex flex-1 flex-col gap-2 px-1 pb-1 pt-4">
                    <p className="t-small font-medium uppercase tracking-[0.14em] text-accent">
                      {project.industry[locale]}
                    </p>
                    <h2 className="font-[family-name:var(--font-space-grotesk)] text-lg font-medium text-text">
                      {project.name}
                    </h2>
                    <p className="t-small flex-1 text-text-muted">
                      {project.description[locale]}
                    </p>

                    <div className="mt-3 flex items-center justify-between gap-3">
                      <Link
                        href={project.href}
                        className="inline-flex items-center gap-1.5 text-[14px] font-medium text-text transition-colors duration-150 hover:text-accent"
                      >
                        {dict.common.openDemo}
                        <ArrowUpRight aria-hidden="true" strokeWidth={1.5} className="size-4" />
                      </Link>

                      <button
                        ref={(node) => {
                          triggerRefs.current[project.slug] = node;
                        }}
                        type="button"
                        onClick={() => setLightboxIndex(absoluteIndex)}
                        aria-label={`${dict.portfolio.enlarge}: ${project.name}`}
                        className="inline-flex size-9 items-center justify-center rounded-lg border border-border text-text-muted transition-colors duration-150 hover:border-accent/40 hover:text-accent"
                      >
                        <Maximize2 aria-hidden="true" strokeWidth={1.5} className="size-4" />
                      </button>
                    </div>
                  </div>
                </Card>
              </li>
            );
          })}
        </ul>
      )}

      <Lightbox
        items={lightboxItems}
        index={lightboxIndex}
        onClose={() => setLightboxIndex(null)}
        onIndexChange={setLightboxIndex}
        label={dict.portfolio.lightboxLabel}
        counterWord={dict.portfolio.counter}
        closeLabel={dict.common.close}
        prevLabel={dict.common.previous}
        nextLabel={dict.common.next}
      />
    </>
  );
}
