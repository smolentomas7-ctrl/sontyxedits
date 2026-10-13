"use client";

import clsx from "clsx";
import { Info } from "lucide-react";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { site } from "@/config/miauto";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * The shell every service widget sits in: heading, scene, readouts, disclaimer.
 *
 * The widgets differ only in what they draw and what they compute, so this
 * handles everything else once — the slider semantics, the live region, lazy
 * mounting, and the note saying this illustrates a principle rather than
 * measuring anyone's car.
 */
export function WidgetFrame({
  heading,
  lead,
  disclaimer,
  controls,
  readouts,
  children,
}: {
  heading: string;
  lead: string;
  disclaimer: string;
  controls: ReactNode;
  readouts?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      data-service-widget="true"
      className="rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--surface)] p-5 md:p-7"
    >
      <h2 className="text-[1.25rem] md:text-[1.5rem]">{heading}</h2>
      <p className="prose-width mt-3 text-[0.9375rem] text-[color:var(--text-muted)]">{lead}</p>

      <div className="mt-7">{children}</div>

      <div className="mt-6 grid gap-6 md:grid-cols-[1.1fr_1fr] md:items-start">
        <div>{controls}</div>
        {readouts ? <div>{readouts}</div> : null}
      </div>

      <p className="mt-7 flex gap-3 border-t border-[var(--border)] pt-5 text-[0.8125rem] leading-relaxed text-[color:var(--text-muted)]">
        <Info size={16} aria-hidden="true" className="mt-0.5 shrink-0" />
        <span>
          {disclaimer}{" "}
          <a href={site.phoneHref} className="whitespace-nowrap text-[color:var(--accent)]">
            {site.phone}
          </a>
        </span>
      </p>
    </section>
  );
}

/**
 * A labelled range control.
 *
 * It is a real `<input type="range">`, so keyboard support, screen-reader
 * semantics and touch behaviour come from the platform rather than from
 * re-implementation. `touch-action: pan-y` keeps a vertical swipe scrolling the
 * page instead of dragging the handle.
 */
export function WidgetSlider({
  label,
  value,
  min,
  max,
  step,
  display,
  onChange,
  marks,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  /** Human-readable current value, also used for aria-valuetext. */
  display: string;
  onChange: (value: number) => void;
  marks?: readonly { readonly at: number; readonly label: string }[];
}) {
  const id = useId();
  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <label htmlFor={id} className="text-[0.875rem] text-[color:var(--text-muted)]">
          {label}
        </label>
        <output htmlFor={id} className="font-heading text-[1.0625rem] font-semibold tabular-nums">
          {display}
        </output>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        aria-valuetext={display}
        onChange={(event) => onChange(Number(event.target.value))}
        className="mt-3 h-11 w-full cursor-grab touch-pan-y accent-[var(--accent)] active:cursor-grabbing"
      />
      {marks && marks.length > 0 ? (
        <div className="relative mt-1 h-4" aria-hidden="true">
          {marks.map((mark) => {
            // A mark sitting on either end would otherwise hang off the track
            // and wrap; the end marks align to their edge instead of centring.
            const at = ((mark.at - min) / (max - min)) * 100;
            const shift = at <= 1 ? "0" : at >= 99 ? "-100%" : "-50%";
            return (
              <span
                key={mark.label}
                className="absolute whitespace-nowrap text-[0.6875rem] tabular-nums text-[color:var(--text-muted)]"
                style={{ left: `${at}%`, transform: `translateX(${shift})` }}
              >
                {mark.label}
              </span>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

/** One figure in the readout block. `tone` colours the value, never alone. */
export function Readout({
  label,
  value,
  sub,
  tone = "default",
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: "default" | "accent" | "success" | "danger";
}) {
  return (
    <div>
      <p className="text-[0.75rem] uppercase tracking-[0.1em] text-[color:var(--text-muted)]">
        {label}
      </p>
      <p
        className={clsx(
          "mt-1 font-heading text-[1.375rem] font-bold tabular-nums md:text-[1.625rem]",
          tone === "accent" && "text-[color:var(--accent)]",
          tone === "success" && "text-[color:var(--success)]",
          tone === "danger" && "text-[color:var(--danger)]",
        )}
      >
        {value}
      </p>
      {sub ? (
        <p className="mt-0.5 text-[0.8125rem] text-[color:var(--text-muted)]">{sub}</p>
      ) : null}
    </div>
  );
}

/** Announces the current readings once they settle, not on every input event. */
export function LiveReadout({ text }: { text: string }) {
  const [settled, setSettled] = useState(text);
  useEffect(() => {
    const id = window.setTimeout(() => setSettled(text), 400);
    return () => window.clearTimeout(id);
  }, [text]);
  return (
    <p aria-live="polite" className="sr-only">
      {settled}
    </p>
  );
}

/**
 * Mounts its child only once the section is close to the viewport, so a widget
 * never delays the first render of the page it sits on.
 */
export function LazyMount({
  minHeight,
  children,
}: {
  minHeight: number;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || show) return;
    if (typeof IntersectionObserver === "undefined") {
      setShow(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setShow(true);
            observer.disconnect();
          }
        }
      },
      { rootMargin: "400px 0px" },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [show]);

  return (
    <div ref={ref} style={show ? undefined : { minHeight }}>
      {show ? children : null}
    </div>
  );
}

/** Formats a number with a Slovak-style thousands space and fixed decimals. */
export function fmt(value: number, decimals = 0): string {
  return value
    .toFixed(decimals)
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/**
 * Same, with the locale's decimal mark. Slovak writes 1,6 mm, not 1.6 mm, and a
 * figure in the wrong notation reads as a foreign website.
 */
export function num(value: number, decimals: number, locale: Locale): string {
  const out = fmt(value, decimals);
  return locale === "sk" ? out.replace(".", ",") : out;
}

/** Eases a displayed number toward its target, so readouts settle rather than jump. */
export function useCountUp(target: number, decimals = 0): number {
  const [shown, setShown] = useState(target);
  const raf = useRef<number | null>(null);
  const from = useRef(target);
  const start = useRef(0);

  useEffect(() => {
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setShown(target);
      return;
    }
    from.current = shown;
    start.current = performance.now();
    const tick = (now: number) => {
      const t = Math.min((now - start.current) / 320, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      const value = from.current + (target - from.current) * eased;
      setShown(Number(value.toFixed(decimals + 2)));
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
    };
    // `shown` is intentionally not a dependency: it is the animation's start point.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, decimals]);

  return shown;
}

export type WidgetStrings = LocaleContent["widgets"];
