"use client";

import { useId, useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export type AccordionItem = {
  q: string;
  a: string;
};

/**
 * FAQ accordion. Real <button> triggers with aria-expanded / aria-controls.
 *
 * The height animates using the grid-template-rows 0fr -> 1fr technique, which
 * transitions to the content's natural height without measuring it in JS. The
 * collapsed panel is also visibility:hidden, which keeps anything inside it out
 * of the tab order and out of the accessibility tree while still allowing the
 * transition to run. prefers-reduced-motion collapses the duration globally.
 */
export function Accordion({
  items,
  className,
}: {
  items: AccordionItem[];
  className?: string;
}) {
  const [open, setOpen] = useState<number | null>(null);
  const baseId = useId();

  return (
    <div className={cn("divide-y divide-border border-y border-border", className)}>
      {items.map((item, index) => {
        const isOpen = open === index;
        const buttonId = `${baseId}-trigger-${index}`;
        const panelId = `${baseId}-panel-${index}`;

        return (
          <div key={item.q}>
            <h3>
              <button
                type="button"
                id={buttonId}
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpen(isOpen ? null : index)}
                className="flex w-full items-center justify-between gap-6 py-5 text-left transition-colors duration-150 hover:text-accent"
              >
                <span className="text-[17px] font-medium text-text">{item.q}</span>
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
                <p className="t-prose pb-6 pr-10 text-text-muted">{item.a}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
