"use client";

import { useId, useState } from "react";
import { ChevronDown, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Dictionary } from "@/content/i18n";

/**
 * The capability catalogue, as accordion groups rather than one long list.
 *
 * Twelve categories of features is a lot of text; collapsing them keeps the
 * page scannable and lets someone open only the two that concern them. The
 * first group starts open so the section never reads as empty.
 *
 * Groups carrying a `caveat` render it inline — those are the categories
 * where a feature depends on an external service, a paid API or a backend,
 * and saying so beside the list is more honest than one footnote at the end.
 */
export function FeatureGroups({ dict }: { dict: Dictionary }) {
  const [open, setOpen] = useState<string | null>(dict.features.groups[0]?.id ?? null);
  const baseId = useId();

  return (
    <div className="divide-y divide-border border-y border-border">
      {dict.features.groups.map((group, index) => {
        const isOpen = open === group.id;
        const buttonId = `${baseId}-t-${group.id}`;
        const panelId = `${baseId}-p-${group.id}`;

        return (
          <div key={group.id}>
            <h3>
              <button
                type="button"
                id={buttonId}
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpen(isOpen ? null : group.id)}
                className="group/row flex w-full items-center gap-5 py-5 text-left transition-colors duration-150"
              >
                <span
                  aria-hidden="true"
                  className={cn(
                    "font-display text-[13px] font-bold tabular-nums transition-colors duration-150",
                    isOpen ? "text-accent" : "text-text-muted",
                  )}
                >
                  {String(index + 1).padStart(2, "0")}
                </span>

                <span className="flex-1">
                  <span
                    className={cn(
                      "block font-display text-[17px] font-semibold transition-colors duration-150",
                      isOpen ? "text-accent" : "text-text group-hover/row:text-accent",
                    )}
                  >
                    {group.title}
                  </span>
                  <span className="t-small mt-0.5 block text-text-muted">{group.summary}</span>
                </span>

                <ChevronDown
                  aria-hidden="true"
                  strokeWidth={1.5}
                  className={cn(
                    "size-5 shrink-0 text-text-muted transition-transform duration-200",
                    isOpen && "rotate-180 text-accent",
                  )}
                />
              </button>
            </h3>

            <div
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              className={cn(
                "grid transition-[grid-template-rows,visibility] duration-200 ease-out",
                isOpen ? "visible grid-rows-[1fr]" : "invisible grid-rows-[0fr]",
              )}
            >
              <div className="overflow-hidden">
                <div className="pb-7 pl-9 pr-4">
                  <ul className="grid gap-x-8 gap-y-2.5 sm:grid-cols-2">
                    {group.items.map((item) => (
                      <li
                        key={item}
                        className="flex items-start gap-2.5 text-[15px] text-text-muted"
                      >
                        <span
                          aria-hidden="true"
                          className="mt-[9px] size-1 shrink-0 rounded-full bg-accent"
                        />
                        {item}
                      </li>
                    ))}
                  </ul>

                  {group.caveat ? (
                    <p className="mt-5 flex gap-2.5 rounded-xl border border-border bg-bg px-4 py-3 text-[13px] leading-relaxed text-text-muted">
                      <Info
                        aria-hidden="true"
                        strokeWidth={1.5}
                        className="mt-0.5 size-4 shrink-0 text-accent"
                      />
                      {group.caveat}
                    </p>
                  ) : null}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
