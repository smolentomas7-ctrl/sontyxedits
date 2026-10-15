import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Tilt } from "@/components/ui/Tilt";
import { Reveal } from "@/components/ui/Reveal";
import { BrowserFrame } from "@/components/ui/BrowserFrame";
import { projects } from "@/content/projects";
import type { Dictionary, Locale } from "@/content/i18n";
import { cn } from "@/lib/utils";

/**
 * The three portfolio examples.
 *
 * Each card tilts toward the cursor with a parallax offset between the frame
 * and the screenshot inside it, which is what gives the preview depth. The
 * badge distinguishes real client work from a capability demonstration — that
 * distinction is never left to the reader to infer.
 */
export function WorkShowcase({
  locale,
  dict,
  limit,
}: {
  locale: Locale;
  dict: Dictionary;
  limit?: number;
}) {
  const shown = typeof limit === "number" ? projects.slice(0, limit) : projects;

  return (
    <ul className="grid gap-7 lg:grid-cols-3">
      {shown.map((project, index) => {
        const isClient = project.kind === "client";
        return (
          <Reveal as="li" key={project.slug} delay={index * 80} className="flex">
            <Tilt
              className="flex w-full"
              max={5}
              scale={1.012}
              depth={8}
              glare
            >
              <article
                className={cn(
                  "flex h-full w-full flex-col overflow-hidden rounded-2xl border bg-surface p-4",
                  "transition-colors duration-300",
                  isClient
                    ? "border-accent/25 hover:border-accent/50"
                    : "border-border hover:border-text-muted/40",
                )}
              >
                <BrowserFrame url={`webora.sk${project.href}`}>
                  <div className="relative aspect-[16/10] overflow-hidden bg-bg">
                    <Image
                      src={project.preview.src}
                      alt={project.preview.alt}
                      fill
                      sizes="(max-width: 1024px) 100vw, 33vw"
                      className="object-cover object-top"
                    />
                  </div>
                </BrowserFrame>

                <div className="flex flex-1 flex-col gap-3 px-1 pb-1 pt-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={cn(
                        "rounded-full px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.1em]",
                        isClient
                          ? "bg-accent-soft text-accent"
                          : "border border-border text-text-muted",
                      )}
                    >
                      {isClient ? dict.portfolio.clientBadge : dict.portfolio.demoBadge}
                    </span>
                    <span className="t-small text-text-muted">
                      {project.categoryLabel[locale]}
                    </span>
                  </div>

                  <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-medium text-text">
                    {project.name}
                  </h3>

                  <p className="t-small flex-1 text-text-muted">{project.summary[locale]}</p>

                  <ul className="flex flex-wrap gap-1.5 pt-1">
                    {project.capabilities[locale].slice(0, 3).map((cap) => (
                      <li
                        key={cap}
                        className="rounded-md border border-border px-2 py-1 text-[12px] text-text-muted"
                      >
                        {cap}
                      </li>
                    ))}
                  </ul>

                  <Link
                    href={`/${locale}/portfolio/${project.slug}`}
                    className="group/link mt-3 inline-flex items-center gap-1.5 text-[14px] font-medium text-accent transition-colors duration-150 hover:text-accent-hover"
                  >
                    {dict.common.viewExample}
                    <ArrowUpRight
                      aria-hidden="true"
                      strokeWidth={1.5}
                      className="size-4 transition-transform duration-200 group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 motion-reduce:transition-none"
                    />
                    <span className="sr-only">— {project.name}</span>
                  </Link>
                </div>
              </article>
            </Tilt>
          </Reveal>
        );
      })}
    </ul>
  );
}
