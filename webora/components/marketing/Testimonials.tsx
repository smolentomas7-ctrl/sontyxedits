import { AlertTriangle, Quote } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import type { Dictionary } from "@/content/i18n";

/**
 * Demonstration testimonials.
 *
 * These are invented, and the UI says so three times over: a disclaimer panel
 * above the cards, a per-card badge, and fictional company names. Avatars are
 * initials rather than photographs — putting a real face on an invented quote
 * would misrepresent a real person, and a stock portrait would imply a real
 * customer that does not exist.
 *
 * Replacing this with genuine feedback means swapping `dict.testimonials.items`
 * and deleting the disclaimer and badge.
 */
export function Testimonials({ dict }: { dict: Dictionary }) {
  return (
    <>
      <Reveal>
        <p
          role="note"
          className="mb-10 flex gap-3 rounded-xl border border-[#F59E0B]/35 bg-[#F59E0B]/10 px-5 py-4 text-[14px] leading-relaxed text-text"
        >
          <AlertTriangle
            aria-hidden="true"
            strokeWidth={1.5}
            className="mt-0.5 size-5 shrink-0 text-[#F59E0B]"
          />
          {dict.testimonials.disclaimer}
        </p>
      </Reveal>

      <ul className="grid gap-6 md:grid-cols-3">
        {dict.testimonials.items.map((item, index) => {
          const initials = item.name
            .split(" ")
            .map((part) => part.charAt(0))
            .slice(0, 2)
            .join("");

          return (
            <Reveal as="li" key={item.name} delay={index * 70} className="flex">
              <figure className="flex w-full flex-col gap-5 rounded-2xl border border-border bg-surface p-7 transition-colors duration-200 hover:border-text-muted/35">
                <div className="flex items-start justify-between gap-3">
                  <Quote
                    aria-hidden="true"
                    strokeWidth={1.5}
                    className="size-6 shrink-0 text-accent/70"
                  />
                  <span className="rounded-full border border-border px-2.5 py-1 text-[11px] uppercase tracking-[0.1em] text-text-muted">
                    {dict.testimonials.badge}
                  </span>
                </div>

                <blockquote className="flex-1 text-[15px] leading-relaxed text-text-muted">
                  {item.text}
                </blockquote>

                <figcaption className="flex items-center gap-3 border-t border-border pt-5">
                  <span
                    aria-hidden="true"
                    className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent-soft font-[family-name:var(--font-space-grotesk)] text-[13px] font-bold text-accent"
                  >
                    {initials}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-[15px] font-medium text-text">
                      {item.name}
                    </span>
                    <span className="block truncate text-[13px] text-text-muted">
                      {item.role}, {item.company}
                    </span>
                  </span>
                </figcaption>
              </figure>
            </Reveal>
          );
        })}
      </ul>
    </>
  );
}
