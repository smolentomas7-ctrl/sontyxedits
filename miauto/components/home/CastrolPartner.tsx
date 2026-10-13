import { ClipboardCheck, Droplets, Handshake, ShieldCheck } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import type { LocaleContent } from "@/content/types";

/**
 * The Castrol Service partnership.
 *
 * Typographic on purpose: the site reproduces no Castrol artwork and claims no
 * certification. What it states is what the owners state — a contractual
 * partnership, Castrol oils in the oil service, and the oil chosen to the
 * manufacturer's specification for the particular engine.
 *
 * The icons are assigned by position, so the order of `castrol.points` in the
 * content files is part of the meaning.
 */
const ICONS = [Handshake, Droplets, ClipboardCheck, ShieldCheck] as const;

export function CastrolPartner({ t }: { t: LocaleContent }) {
  const c = t.castrol;

  return (
    <Reveal>
      <div className="relative overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)]">
        {/* One warm edge, lit from the top left, instead of a badge. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-[var(--accent)] via-[color-mix(in_srgb,var(--accent)_35%,transparent)] to-transparent"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -left-24 -top-32 size-80 rounded-full bg-[var(--accent)] opacity-[0.07] blur-3xl"
        />

        <div className="relative grid gap-10 p-6 md:gap-14 md:p-10 lg:grid-cols-[1.05fr_1fr] lg:items-center lg:gap-16 lg:p-14">
          <div>
            <p className="text-[0.75rem] font-semibold uppercase tracking-[0.16em] text-[color:var(--accent)]">
              {c.eyebrow}
            </p>
            <h2 className="mt-4 text-[1.75rem] md:text-[2.25rem]">{c.heading}</h2>
            <p className="mt-4 font-heading text-[1.125rem] font-semibold tracking-[-0.01em] text-[color:var(--text)] md:text-[1.25rem]">
              {c.lead}
            </p>
            <p className="prose-width mt-5 text-[1.0625rem] leading-relaxed text-[color:var(--text-muted)]">
              {c.body}
            </p>
          </div>

          <ul className="grid gap-3 sm:grid-cols-2 lg:gap-4">
            {c.points.map((point, index) => {
              const Icon = ICONS[index] ?? ShieldCheck;
              return (
                <Reveal as="li" key={point} index={index}>
                  <div className="flex h-full items-start gap-3.5 rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--bg)] p-4 md:p-5">
                    <span className="mt-0.5 inline-flex size-9 shrink-0 items-center justify-center rounded-[var(--radius-control)] bg-[var(--accent-soft)] text-[color:var(--accent)]">
                      <Icon size={18} aria-hidden="true" />
                    </span>
                    <span className="text-[0.9375rem] leading-snug">{point}</span>
                  </div>
                </Reveal>
              );
            })}
          </ul>
        </div>
      </div>
    </Reveal>
  );
}
