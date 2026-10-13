import { GraduationCap, ShieldCheck, Wrench } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import type { LocaleContent } from "@/content/types";

/**
 * What the two owners bring to the work.
 *
 * Every figure here comes from the owners themselves: the years, the schooling
 * and the approach. Nothing is attributed to one of them rather than the other,
 * because nothing establishes which is whose — the copy speaks for both, which
 * is also how they describe it.
 */
const ICONS = [Wrench, GraduationCap, ShieldCheck] as const;

export function Experience({ t }: { t: LocaleContent }) {
  const e = t.about.experience;

  return (
    <div className="grid gap-10 lg:grid-cols-[1fr_1.05fr] lg:items-start lg:gap-16">
      <Reveal>
        <h2 className="text-[1.5rem] md:text-[2rem]">{e.heading}</h2>
        <p className="mt-4 font-heading text-[1.125rem] font-semibold tracking-[-0.01em] md:text-[1.25rem]">
          {e.lead}
        </p>
        <p className="prose-width mt-5 text-[1.0625rem] leading-[1.75] text-[color:var(--text-muted)]">
          {e.body}
        </p>
      </Reveal>

      <ul className="grid gap-3.5">
        {e.points.map((point, index) => {
          const Icon = ICONS[index] ?? ShieldCheck;
          return (
            <Reveal as="li" key={point.title} index={index}>
              <div className="flex items-start gap-4 rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)] p-5 md:p-6">
                <span className="inline-flex size-11 shrink-0 items-center justify-center rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--bg)] text-[color:var(--accent)]">
                  <Icon size={20} aria-hidden="true" />
                </span>
                <div>
                  <p className="font-heading text-[1.0625rem] font-semibold tracking-[-0.01em]">
                    {point.title}
                  </p>
                  <p className="mt-1.5 text-[0.9375rem] leading-relaxed text-[color:var(--text-muted)]">
                    {point.body}
                  </p>
                </div>
              </div>
            </Reveal>
          );
        })}
      </ul>
    </div>
  );
}
