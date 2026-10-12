"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";
import { usePressHandlers } from "@/lib/motion";
import type { FaqItem } from "@/content/types";

/**
 * Real button triggers with aria-expanded / aria-controls. The answer stays in
 * the DOM whether open or not, so search engines index it; the panel animates
 * on grid-template-rows, which is a layout-safe height transition.
 */
export function Accordion({ items }: { items: readonly FaqItem[] }) {
  const [open, setOpen] = useState<string | null>(items[0]?.id ?? null);
  const base = useId();

  return (
    <div className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
      {items.map((item) => {
        const isOpen = open === item.id;
        const panelId = `${base}-${item.id}-panel`;
        const buttonId = `${base}-${item.id}-button`;
        return (
          <AccordionRow
            key={item.id}
            item={item}
            isOpen={isOpen}
            panelId={panelId}
            buttonId={buttonId}
            onToggle={() => setOpen(isOpen ? null : item.id)}
          />
        );
      })}
    </div>
  );
}

function AccordionRow({
  item,
  isOpen,
  panelId,
  buttonId,
  onToggle,
}: {
  item: FaqItem;
  isOpen: boolean;
  panelId: string;
  buttonId: string;
  onToggle: () => void;
}) {
  const press = usePressHandlers();
  return (
    <div>
      <h3>
        <button
          type="button"
          id={buttonId}
          aria-expanded={isOpen}
          aria-controls={panelId}
          onClick={onToggle}
          {...press}
          className="tappable flex w-full items-center justify-between gap-4 py-5 text-left text-[1.0625rem] font-semibold text-[color:var(--text)] md:py-6 md:text-[1.1875rem]"
          style={{ ["--press-scale" as string]: "0.99" }}
        >
          <span className="font-heading">{item.q}</span>
          <ChevronDown
            size={20}
            aria-hidden="true"
            className="shrink-0 text-[color:var(--accent)] transition-transform duration-[var(--dur-state)] ease-[var(--ease-ios)]"
            style={{ transform: isOpen ? "rotate(180deg)" : "none" }}
          />
        </button>
      </h3>
      <div
        id={panelId}
        role="region"
        aria-labelledby={buttonId}
        className="accordion-panel"
        data-open={isOpen ? "true" : "false"}
      >
        <div>
          <p className="prose-width pb-6 text-[color:var(--text-muted)]">{item.a}</p>
        </div>
      </div>
    </div>
  );
}
