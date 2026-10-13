"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./SignatureScene.module.css";
import { SignatureSvg } from "./SignatureSvg";
import type { LocaleContent } from "@/content/types";

const STAGE_POINTS = [0, 0.22, 0.46, 0.68, 1] as const;

/** Which of the five named beats a given --p falls in. */
function stageFor(p: number): number {
  if (p < 0.14) return 0;
  if (p < 0.33) return 1;
  if (p < 0.54) return 2;
  if (p < 0.86) return 3;
  return 4;
}

export function SignatureScene({ t }: { t: LocaleContent }) {
  const sceneRef = useRef<HTMLDivElement | null>(null);
  const rangeRef = useRef<HTMLInputElement | null>(null);
  const hintTimers = useRef<number[]>([]);
  const hintDone = useRef(false);
  // Stage is the ONLY React state here, and it changes at most four times
  // across a full drag. Nothing re-renders on pointermove.
  const [stage, setStage] = useState(0);

  const write = useCallback((value: number) => {
    const scene = sceneRef.current;
    if (!scene) return;
    scene.style.setProperty("--p", String(value));
    const next = stageFor(value);
    if (scene.dataset["stage"] !== String(next)) scene.dataset["stage"] = String(next);
    setStage((current) => (next === current ? current : next));
  }, []);

  /** Kills the autoplay hint permanently, on the first sign of real interaction. */
  const cancelHint = useCallback(() => {
    if (hintDone.current) return;
    hintDone.current = true;
    for (const id of hintTimers.current) window.clearTimeout(id);
    hintTimers.current = [];
    const scene = sceneRef.current;
    if (!scene) return;
    scene.classList.remove(styles.autoplay ?? "");
    write(Number(rangeRef.current?.value ?? 0));
  }, [write]);

  // Reduced motion opens on the final state. Everything stays operable.
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduced) {
      sceneRef.current?.setAttribute("data-stage", "0");
      return;
    }
    hintDone.current = true;
    if (rangeRef.current) rangeRef.current.value = "1";
    write(1);
  }, [write]);

  // Autoplay hint: --p 0 -> 0.3 -> 0, once, on first viewport entry. Never loops.
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene || hintDone.current) return;
    if (typeof IntersectionObserver === "undefined") return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting || hintDone.current) continue;
          observer.disconnect();
          scene.classList.add(styles.autoplay ?? "");
          hintTimers.current.push(
            window.setTimeout(() => write(0.3), 80),
            window.setTimeout(() => write(0), 620),
            window.setTimeout(() => {
              scene.classList.remove(styles.autoplay ?? "");
              hintDone.current = true;
            }, 1120),
          );
        }
      },
      { threshold: 0.35 },
    );
    observer.observe(scene);
    return () => {
      observer.disconnect();
      for (const id of hintTimers.current) window.clearTimeout(id);
    };
  }, [write]);

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    cancelHint();
    const input = rangeRef.current;
    if (!input) return;
    const current = Number(input.value);

    let next: number | null = null;
    if (event.key === "PageUp") next = STAGE_POINTS[Math.min(stageFor(current) + 1, 4)] ?? 1;
    else if (event.key === "PageDown") next = STAGE_POINTS[Math.max(stageFor(current) - 1, 0)] ?? 0;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = 1;

    if (next !== null) {
      event.preventDefault();
      input.value = String(next);
      write(next);
    }
    // Arrow keys fall through to the input's own fine stepping.
  };

  const beat = t.signature.stages[stage] ?? t.signature.stages[0];

  return (
    <div>
      <div ref={sceneRef} className={styles.scene} data-stage="0">
        <SignatureSvg t={t} />

        <input
          ref={rangeRef}
          type="range"
          min={0}
          max={1}
          step={0.001}
          defaultValue={0}
          className={styles.range}
          aria-label={t.signature.title}
          aria-valuetext={`${t.signature.stageLabel} ${stage + 1}: ${beat.name}`}
          onInput={(event) => {
            cancelHint();
            write(Number(event.currentTarget.value));
          }}
          onPointerDown={cancelHint}
          onKeyDown={onKeyDown}
        />

        <div className={styles.track} aria-hidden="true">
          <div className={styles.trackFill} />
          <div className={styles.ticks}>
            {[0, 1, 2, 3, 4].map((i) => (
              <span key={i} className={styles.tick} />
            ))}
          </div>
        </div>
        <div className={styles.handle} aria-hidden="true">
          <span className={styles.handleDot} />
        </div>
      </div>

      {/* The current beat, announced once per stage rather than per pointer move. */}
      <div aria-live="polite" className="mt-5">
        <p className="flex flex-wrap items-baseline gap-x-3 gap-y-1 font-heading text-[1.0625rem] font-semibold">
          <span className="tabular-nums text-[color:var(--accent)]">
            {stage + 1}/5
          </span>
          <span>{beat.name}</span>
        </p>
        <p className="prose-width mt-2 text-[0.9375rem] text-[color:var(--text-muted)]">
          {beat.body}
        </p>
      </div>

      <p className="mt-5 text-[0.875rem] text-[color:var(--text-muted)]">
        {t.signature.hint}
        <span className="sr-only"> {t.signature.keyboardHint}</span>
      </p>

      {/* Under reduced motion the animation carries no information, so the five
          beats are also available as plain text. Hidden from screen readers
          because the live region above already announces the current one. */}
      <ol
        className="mt-4 hidden flex-wrap gap-x-5 gap-y-1 text-[0.8125rem] text-[color:var(--text-muted)] motion-reduce:flex"
        aria-hidden="true"
      >
        {t.signature.stages.map((item, i) => (
          <li key={item.name} className="tabular-nums">
            <span className="text-[color:var(--accent)]">{i + 1}.</span> {item.name}
          </li>
        ))}
      </ol>
    </div>
  );
}
