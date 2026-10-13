"use client";

import clsx from "clsx";
import { ChevronRight, RotateCcw } from "lucide-react";
import { useState } from "react";
import { LiveReadout, Readout, WidgetFrame } from "./WidgetFrame";
import { usePressHandlers } from "@/lib/motion";
import type { LocaleContent } from "@/content/types";

/** Geometry of the funnel: lanes in on the left, one cause out on the right. */
const FUN = { x0: 40, x1: 600, yTop: 26, yBottom: 154, yOut: 90 };

/** How many causes are still standing after `step` of `steps` measurements. */
function remainingAt(total: number, steps: number, step: number): number {
  return Math.max(1, Math.round(total - ((total - 1) * step) / steps));
}

/** x of the dashed line that marks measurement `step` (1-based). */
function markerX(steps: number, step: number): number {
  return FUN.x0 + (step / (steps + 1)) * (FUN.x1 - FUN.x0);
}

/**
 * Diagnostics widget: a set of candidate causes that measurement narrows down.
 *
 * The point it makes is the one the page makes in prose — a code tells you which
 * circuit is complaining, and the work is everything between that and knowing
 * which part has actually failed.
 */
export function DiagnosticsWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.diagnostics;
  const [symptomId, setSymptomId] = useState(w.symptoms[0]?.id ?? "");
  const [step, setStep] = useState(0);
  const press = usePressHandlers();

  const symptom = w.symptoms.find((s) => s.id === symptomId) ?? w.symptoms[0];
  if (!symptom) return null;

  const total = symptom.causes.length;
  // Each measurement step eliminates a share of what is left, ending at one.
  const remaining = Math.max(1, Math.round(total - ((total - 1) * step) / symptom.steps.length));
  const done = step >= symptom.steps.length;

  const pick = (id: string) => {
    setSymptomId(id);
    setStep(0);
  };

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <div>
          <p className="text-[0.875rem] text-[color:var(--text-muted)]">{w.pick}</p>
          <ul className="mt-3 flex flex-wrap gap-2">
            {w.symptoms.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => pick(item.id)}
                  aria-pressed={item.id === symptomId}
                  className={clsx(
                    "tappable rounded-[var(--radius-pill)] border px-3.5 py-2 text-[0.875rem]",
                    item.id === symptomId
                      ? "border-[var(--accent)] bg-[var(--accent-soft)] text-[color:var(--accent)]"
                      : "border-[var(--border)] text-[color:var(--text)] hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))]",
                  )}
                  {...press}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              disabled={done}
              onClick={() => setStep((s) => Math.min(s + 1, symptom.steps.length))}
              className="tappable inline-flex h-11 items-center gap-2 rounded-[var(--radius-control)] bg-[var(--accent)] px-5 text-[0.9375rem] font-semibold text-[color:var(--accent-ink)] disabled:bg-[var(--surface-hover)] disabled:text-[color:var(--text-muted)]"
              {...press}
            >
              {w.stepLabel}
              <ChevronRight size={16} aria-hidden="true" />
            </button>
            {step > 0 ? (
              <button
                type="button"
                onClick={() => setStep(0)}
                className="tappable inline-flex h-11 items-center gap-2 rounded-[var(--radius-control)] border border-[var(--border)] px-4 text-[0.875rem]"
                {...press}
              >
                <RotateCcw size={15} aria-hidden="true" />
                {w.reset}
              </button>
            ) : null}
          </div>
        </div>
      }
      readouts={
        <Readout
          label={done ? w.narrowed : w.remaining}
          value={done ? "1" : String(remaining)}
          sub={done ? symptom.causes[symptom.causes.length - 1] : undefined}
          tone={done ? "success" : "accent"}
        />
      }
    >
      <LiveReadout
        text={
          done
            ? `${w.narrowed}: ${symptom.causes[symptom.causes.length - 1]}`
            : `${w.remaining}: ${remaining}`
        }
      />

      {/* ── the funnel: every candidate enters, measurement takes them out ── */}
      <svg
        viewBox="0 0 640 180"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 180" }}
      >
        <defs>
          <radialGradient id="dg-out">
            <stop offset="0%" stopColor={done ? "var(--success)" : "var(--accent)"} stopOpacity="0.5" />
            <stop offset="100%" stopColor={done ? "var(--success)" : "var(--accent)"} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* measurement steps */}
        {symptom.steps.map((_, i) => {
          const x = markerX(symptom.steps.length, i + 1);
          const taken = i < step;
          return (
            <g key={i}>
              <line
                x1={x}
                y1="22"
                x2={x}
                y2="158"
                stroke={taken ? "var(--accent)" : "#2b3238"}
                strokeOpacity={taken ? 0.5 : 1}
                strokeWidth="1"
                strokeDasharray="3 5"
                style={{ transition: "stroke 240ms var(--ease-ios)" }}
              />
              <circle
                cx={x}
                cy="14"
                r="8.5"
                fill={taken ? "var(--accent-soft)" : "var(--bg)"}
                stroke={taken ? "var(--accent)" : "#39434b"}
                strokeWidth="1.2"
                style={{ transition: "stroke 240ms var(--ease-ios), fill 240ms var(--ease-ios)" }}
              />
              <text
                x={x}
                y="18"
                textAnchor="middle"
                fontSize="10"
                fontWeight="600"
                fill={taken ? "var(--accent)" : "var(--text-muted)"}
              >
                {i + 1}
              </text>
            </g>
          );
        })}

        {/* one lane per candidate cause */}
        {symptom.causes.map((cause, i) => {
          const y = total < 2 ? FUN.yOut : FUN.yTop + (i / (total - 1)) * (FUN.yBottom - FUN.yTop);
          const survives = i === total - 1;
          const eliminated = i < total - remaining;

          // The step that rules this lane out, and how far it reaches before it.
          let cut = symptom.steps.length;
          for (let s = 1; s <= symptom.steps.length; s += 1) {
            if (total - remainingAt(total, symptom.steps.length, s) > i) {
              cut = s;
              break;
            }
          }
          const reach =
            (markerX(symptom.steps.length, cut) - FUN.x0) / (FUN.x1 - FUN.x0);
          const span = eliminated ? reach : 1;

          return (
            <g key={cause}>
              <circle
                cx={FUN.x0}
                cy={y}
                r="3.4"
                fill={
                  eliminated
                    ? "#46525b"
                    : survives && remaining === 1
                      ? "var(--success)"
                      : "var(--accent)"
                }
              />
              <path
                d={`M${FUN.x0} ${y} C${FUN.x0 + 210} ${y}, ${FUN.x1 - 210} ${FUN.yOut}, ${FUN.x1} ${FUN.yOut}`}
                fill="none"
                stroke={
                  eliminated
                    ? "#39434b"
                    : survives && remaining === 1
                      ? "var(--success)"
                      : "var(--accent)"
                }
                strokeWidth={survives && remaining === 1 ? 2.6 : eliminated ? 1.1 : 1.8}
                strokeLinecap="round"
                pathLength={1}
                strokeDasharray={`${span.toFixed(4)} 1`}
                style={{
                  transition:
                    "stroke-dasharray 420ms var(--ease-ios), stroke 240ms var(--ease-ios), stroke-width 240ms var(--ease-ios)",
                  transitionDelay: `${Math.min(i, 5) * 50}ms`,
                }}
              />
            </g>
          );
        })}

        {/* what is left */}
        <circle cx={FUN.x1} cy={FUN.yOut} r="26" fill="url(#dg-out)" />
        <circle
          cx={FUN.x1}
          cy={FUN.yOut}
          r="6"
          fill={done ? "var(--success)" : "var(--accent)"}
          style={{ transition: "fill 240ms var(--ease-ios)" }}
        />
      </svg>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        {/* candidate causes, struck through as they are eliminated */}
        <ul className="space-y-2">
          {symptom.causes.map((cause, i) => {
            const eliminated = i < total - remaining;
            return (
              <li
                key={cause}
                className={clsx(
                  "flex items-center gap-3 rounded-[var(--radius-control)] border px-3.5 py-2.5 text-[0.9375rem] transition-[opacity,border-color,background-color] duration-[var(--dur-state)] ease-[var(--ease-ios)]",
                  eliminated
                    ? "border-[var(--border)] text-[color:var(--text-muted)] line-through opacity-45"
                    : remaining === 1
                      ? "border-[var(--success)] bg-[color-mix(in_srgb,var(--success)_10%,transparent)]"
                      : "border-[var(--border)] bg-[var(--bg)]",
                )}
                style={{ transitionDelay: `${Math.min(i, 5) * 50}ms` }}
              >
                <span
                  aria-hidden="true"
                  className={clsx(
                    "size-2 shrink-0 rounded-full",
                    eliminated
                      ? "bg-[var(--text-muted)]"
                      : remaining === 1
                        ? "bg-[var(--success)]"
                        : "bg-[var(--accent)]",
                  )}
                />
                {cause}
              </li>
            );
          })}
        </ul>

        {/* what each step actually does */}
        <ol className="space-y-2.5">
          {symptom.steps.map((text, i) => (
            <li
              key={text}
              className={clsx(
                "flex gap-3 text-[0.9375rem] transition-opacity duration-[var(--dur-state)]",
                i < step ? "opacity-100" : "opacity-35",
              )}
            >
              <span
                aria-hidden="true"
                className={clsx(
                  "mt-0.5 inline-flex size-6 shrink-0 items-center justify-center rounded-full border text-[0.75rem] font-semibold tabular-nums",
                  i < step
                    ? "border-[var(--accent)] text-[color:var(--accent)]"
                    : "border-[var(--border)] text-[color:var(--text-muted)]",
                )}
              >
                {i + 1}
              </span>
              <span className={i < step ? "text-[color:var(--text)]" : "text-[color:var(--text-muted)]"}>
                {text}
              </span>
            </li>
          ))}
        </ol>
      </div>
    </WidgetFrame>
  );
}
