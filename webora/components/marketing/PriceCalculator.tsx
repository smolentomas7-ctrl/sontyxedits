"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Minus, Plus, Info } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  calculatePrice,
  describeConfiguration,
  ADDON_IDS,
  MIN_PAGES,
  MAX_PAGES,
  MIN_LANGUAGES,
  MAX_LANGUAGES,
  type AddonId,
  type SiteType,
} from "@/lib/pricing";
import type { Dictionary, Locale } from "@/content/i18n";
import { cn } from "@/lib/utils";

/** Counts up/down to a target over ~380ms, respecting reduced motion. */
function useAnimatedNumber(target: number): number {
  const [display, setDisplay] = useState(target);
  const frame = useRef<number | null>(null);
  const fromRef = useRef(target);

  useEffect(() => {
    const prefersReduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (prefersReduced) {
      setDisplay(target);
      fromRef.current = target;
      return;
    }

    const from = fromRef.current;
    const delta = target - from;
    if (delta === 0) return;

    const duration = 380;
    const start = performance.now();

    function step(now: number) {
      const progress = Math.min(1, (now - start) / duration);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = Math.round(from + delta * eased);
      setDisplay(value);
      if (progress < 1) {
        frame.current = requestAnimationFrame(step);
      } else {
        fromRef.current = target;
      }
    }

    frame.current = requestAnimationFrame(step);
    return () => {
      if (frame.current !== null) cancelAnimationFrame(frame.current);
      fromRef.current = target;
    };
  }, [target]);

  return display;
}

export function PriceCalculator({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const router = useRouter();
  const calc = dict.pricing.calc;

  const [siteType, setSiteType] = useState<SiteType>("business");
  const [pages, setPages] = useState(5);
  const [languages, setLanguages] = useState(1);
  const [addons, setAddons] = useState<AddonId[]>([]);

  const result = useMemo(
    () => calculatePrice({ siteType, pages, languages, addons }),
    [siteType, pages, languages, addons],
  );

  const animatedLow = useAnimatedNumber(result.low);
  const animatedHigh = useAnimatedNumber(result.high);

  function toggleAddon(id: AddonId) {
    setAddons((current) =>
      current.includes(id) ? current.filter((a) => a !== id) : [...current, id],
    );
  }

  /** Carries the configuration into the contact form as a prefilled message. */
  function sendAsInquiry() {
    const siteTypeName =
      calc.siteTypes.find((type) => type.id === siteType)?.label ?? siteType;

    const summary = describeConfiguration(
      { siteType, pages, languages, addons },
      result,
      {
        siteType: calc.siteType,
        siteTypeName,
        pages: calc.pages,
        languages: calc.languages,
        addons: calc.addons,
        estimate: calc.estimate,
        addonLabels: calc.addonLabels,
        none: locale === "sk" ? "žiadne" : "none",
      },
    );

    const pkg = siteType === "eshop" ? "eshop" : siteType === "landing" ? "starter" : "business";
    const params = new URLSearchParams({ package: pkg, message: summary });
    router.push(`/${locale}/contact?${params.toString()}`);
  }

  /** Maps a breakdown line id to its human label. */
  function lineLabel(id: string, count?: number): string {
    if (id === "base") return calc.base;
    if (id === "extraPages") return `${calc.extraPages} (${count})`;
    if (id === "extraLanguages") return `${calc.extraLanguages} (${count})`;
    return calc.addonLabels[id] ?? id;
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1.15fr_1fr] lg:gap-10">
      {/* ---------- inputs ---------- */}
      <div className="flex flex-col gap-9">
        <fieldset>
          <legend className="t-small mb-3 font-medium uppercase tracking-[0.12em] text-text">
            {calc.siteType}
          </legend>
          <div className="grid gap-3 sm:grid-cols-3">
            {calc.siteTypes.map((type) => {
              const checked = siteType === type.id;
              return (
                <label
                  key={type.id}
                  className={cn(
                    "flex cursor-pointer flex-col gap-1 rounded-xl border p-4 transition-colors duration-150",
                    checked
                      ? "border-accent bg-accent-soft"
                      : "border-border bg-surface hover:border-text-muted",
                  )}
                >
                  <span className="flex items-center gap-2.5">
                    <input
                      type="radio"
                      name="site-type"
                      value={type.id}
                      checked={checked}
                      onChange={() => setSiteType(type.id as SiteType)}
                      className="size-4 accent-[#5B8DFF]"
                    />
                    <span className="text-[15px] font-medium text-text">{type.label}</span>
                  </span>
                  <span className="pl-[26px] text-[13px] text-text-muted">{type.hint}</span>
                </label>
              );
            })}
          </div>
        </fieldset>

        <div>
          <label
            htmlFor="calc-pages"
            className="t-small mb-3 flex items-baseline justify-between font-medium uppercase tracking-[0.12em] text-text"
          >
            {calc.pages}
            <span className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold normal-case tracking-normal text-accent">
              {pages}
            </span>
          </label>
          <input
            id="calc-pages"
            type="range"
            min={MIN_PAGES}
            max={MAX_PAGES}
            step={1}
            value={pages}
            onChange={(event) => setPages(Number(event.target.value))}
            aria-describedby="calc-pages-hint"
            className="w-full accent-[#5B8DFF]"
          />
          <p id="calc-pages-hint" className="mt-2 text-[13px] text-text-muted">
            {calc.pagesHint}
          </p>
        </div>

        <div>
          <span className="t-small mb-3 block font-medium uppercase tracking-[0.12em] text-text">
            {calc.languages}
          </span>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setLanguages((n) => Math.max(MIN_LANGUAGES, n - 1))}
              disabled={languages <= MIN_LANGUAGES}
              aria-label={`${calc.decrease}: ${calc.languages}`}
              className="inline-flex size-10 items-center justify-center rounded-lg border border-border text-text transition-colors duration-150 hover:bg-surface disabled:opacity-40"
            >
              <Minus aria-hidden="true" strokeWidth={1.5} className="size-4" />
            </button>
            <output
              aria-live="polite"
              className="min-w-10 text-center font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-accent"
            >
              {languages}
            </output>
            <button
              type="button"
              onClick={() => setLanguages((n) => Math.min(MAX_LANGUAGES, n + 1))}
              disabled={languages >= MAX_LANGUAGES}
              aria-label={`${calc.increase}: ${calc.languages}`}
              className="inline-flex size-10 items-center justify-center rounded-lg border border-border text-text transition-colors duration-150 hover:bg-surface disabled:opacity-40"
            >
              <Plus aria-hidden="true" strokeWidth={1.5} className="size-4" />
            </button>
          </div>
          <p className="mt-2 text-[13px] text-text-muted">{calc.languagesHint}</p>
        </div>

        <fieldset>
          <legend className="t-small mb-3 font-medium uppercase tracking-[0.12em] text-text">
            {calc.addons}
          </legend>
          <div className="grid gap-2.5 sm:grid-cols-2">
            {ADDON_IDS.map((id) => {
              const checked = addons.includes(id);
              return (
                <label
                  key={id}
                  className={cn(
                    "flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 transition-colors duration-150",
                    checked
                      ? "border-accent/50 bg-accent-soft"
                      : "border-border bg-surface hover:border-text-muted",
                  )}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleAddon(id)}
                    className="size-[18px] rounded accent-[#5B8DFF]"
                  />
                  <span className="text-[15px] text-text">{calc.addonLabels[id]}</span>
                </label>
              );
            })}
          </div>
        </fieldset>
      </div>

      {/* ---------- result ---------- */}
      <div className="lg:sticky lg:top-28 lg:self-start">
        <Card interactive={false} className="flex flex-col gap-6 p-7">
          <div>
            <p className="t-small font-medium uppercase tracking-[0.12em] text-text-muted">
              {calc.estimate}
            </p>
            <p
              aria-live="polite"
              className="mt-2 font-[family-name:var(--font-space-grotesk)] text-4xl font-bold tracking-[-0.03em] text-accent"
            >
              {animatedLow.toLocaleString(locale === "sk" ? "sk-SK" : "en-IE")} –{" "}
              {animatedHigh.toLocaleString(locale === "sk" ? "sk-SK" : "en-IE")} €
            </p>
            {result.monthly > 0 ? (
              <p className="mt-1.5 text-[15px] text-text-muted">
                + {result.monthly} € / {locale === "sk" ? "mesiac" : "month"}
              </p>
            ) : null}
          </div>

          <div className="border-t border-border pt-5">
            <h3 className="t-small mb-3 font-medium uppercase tracking-[0.12em] text-text">
              {calc.breakdown}
            </h3>
            <ul className="flex flex-col gap-2">
              {result.lines.map((line) => (
                <li
                  key={`${line.id}-${line.detail?.count ?? ""}`}
                  className="flex items-baseline justify-between gap-4 text-[14px]"
                >
                  <span className="text-text-muted">
                    {lineLabel(line.id, line.detail?.count)}
                  </span>
                  <span className="shrink-0 font-medium text-text">
                    {line.amount} €{line.monthly ? ` / ${locale === "sk" ? "mes." : "mo"}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <p className="flex gap-2 rounded-lg border border-border bg-bg px-4 py-3 text-[13px] leading-relaxed text-text-muted">
            <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0 text-accent" />
            {calc.disclaimer}
          </p>

          <Button onClick={sendAsInquiry} className="w-full">
            {calc.sendCta}
          </Button>
        </Card>
      </div>
    </div>
  );
}
