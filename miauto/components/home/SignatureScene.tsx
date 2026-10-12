"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./SignatureScene.module.css";
import type { LocaleContent } from "@/content/types";

const STAGE_POINTS = [0, 0.25, 0.5, 0.72, 1] as const;

/** Which of the five named beats a given --p falls in. */
function stageFor(p: number): number {
  if (p < 0.17) return 0;
  if (p < 0.37) return 1;
  if (p < 0.58) return 2;
  if (p < 0.85) return 3;
  return 4;
}

export function SignatureScene({ t }: { t: LocaleContent }) {
  const sceneRef = useRef<HTMLDivElement | null>(null);
  const rangeRef = useRef<HTMLInputElement | null>(null);
  const hintTimers = useRef<number[]>([]);
  const hintDone = useRef(false);
  // Stage is the ONLY React state here, and it changes at most four times across
  // a full drag. Nothing re-renders on pointermove.
  const [stage, setStage] = useState(0);

  const write = useCallback((value: number) => {
    sceneRef.current?.style.setProperty("--p", String(value));
    setStage((current) => {
      const next = stageFor(value);
      return next === current ? current : next;
    });
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
    scene.style.setProperty("--p", rangeRef.current?.value ?? "0");
  }, []);

  // Reduced motion opens on the final state. Everything stays operable from there.
  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!reduced) return;
    hintDone.current = true;
    if (rangeRef.current) rangeRef.current.value = "1";
    write(1);
  }, [write]);

  // Autoplay hint: --p 0 -> 0.35 -> 0 over ~900ms, once, on first viewport entry.
  // Driven by a transition on the registered property. It never loops.
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
            window.setTimeout(() => scene.style.setProperty("--p", "0.35"), 60),
            window.setTimeout(() => scene.style.setProperty("--p", "0"), 520),
            window.setTimeout(() => {
              scene.classList.remove(styles.autoplay ?? "");
              scene.style.removeProperty("--p");
              hintDone.current = true;
            }, 1000),
          );
        }
      },
      { threshold: 0.4 },
    );
    observer.observe(scene);
    return () => {
      observer.disconnect();
      for (const id of hintTimers.current) window.clearTimeout(id);
    };
  }, []);

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

  const stageName = t.signature.stages[stage] ?? t.signature.stages[0];

  return (
    <div>
      <div ref={sceneRef} className={styles.scene}>
        <Scene t={t} />

        <input
          ref={rangeRef}
          type="range"
          min={0}
          max={1}
          step={0.001}
          defaultValue={0}
          className={styles.range}
          aria-label={t.signature.title}
          aria-valuetext={`${t.signature.stageLabel} ${stage + 1}: ${stageName}`}
          onInput={(event) => {
            cancelHint();
            write(Number(event.currentTarget.value));
          }}
          onPointerDown={cancelHint}
          onKeyDown={onKeyDown}
        />

        <div className={styles.track} aria-hidden="true">
          <div className={styles.trackFill} />
        </div>
        <div className={styles.handle} aria-hidden="true">
          <span className={styles.handleDot} />
        </div>
      </div>

      <p
        aria-live="polite"
        className="mt-5 flex flex-wrap items-baseline gap-x-3 gap-y-1 font-heading text-[1.0625rem] font-semibold"
      >
        <span className="text-[color:var(--accent)] tabular-nums">
          {t.signature.stageLabel} {stage + 1}/5
        </span>
        <span>{stageName}</span>
      </p>

      <p className="mt-2 text-[0.875rem] text-[color:var(--text-muted)]">
        {t.signature.instructions}{" "}
        <span className="sr-only">{t.signature.keyboardHint}</span>
      </p>

      {/* Under reduced motion the animation carries no information, so the five
          beats are also available as plain text. Hidden from screen readers
          because the live region above already announces the current one. */}
      <ol
        className="mt-4 hidden flex-wrap gap-x-5 gap-y-1 text-[0.8125rem] text-[color:var(--text-muted)] motion-reduce:flex"
        aria-hidden="true"
      >
        {t.signature.stages.map((name, i) => (
          <li key={name} className="tabular-nums">
            <span className="text-[color:var(--accent)]">{i + 1}.</span> {name}
          </li>
        ))}
      </ol>
    </div>
  );
}

/**
 * The scene itself. Drawn in code — no photograph, no asset. Every element takes
 * its state from --p through the stylesheet; nothing here holds state.
 */
function Scene({ t }: { t: LocaleContent }) {
  const rows = [0, 1, 2];
  return (
    <svg
      className={styles.svg}
      viewBox="0 0 800 450"
      role="img"
      preserveAspectRatio="xMidYMid meet"
    >
      <title>{t.signature.svgTitle}</title>

      <defs>
        <radialGradient id="mi-warn-glow">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.55" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="mi-part-glow">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.4" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* ---------- instrument cluster ---------- */}
      <g aria-hidden="true">
        <rect
          x="48" y="96" width="330" height="214" rx="26"
          fill="var(--bg)" stroke="var(--border)" strokeWidth="1.5"
        />
        {/* dials */}
        <circle cx="140" cy="190" r="56" fill="none" stroke="var(--border)" strokeWidth="1.5" />
        <circle cx="286" cy="190" r="56" fill="none" stroke="var(--border)" strokeWidth="1.5" />
        <path d="M140 190 L112 152" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" />
        <path d="M286 190 L286 146" stroke="var(--text-muted)" strokeWidth="3" strokeLinecap="round" />
        {[0, 1, 2, 3, 4].map((i) => {
          const a = (-120 + i * 60) * (Math.PI / 180);
          return (
            <g key={i}>
              <line
                x1={140 + Math.cos(a) * 44} y1={190 + Math.sin(a) * 44}
                x2={140 + Math.cos(a) * 50} y2={190 + Math.sin(a) * 50}
                stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" opacity="0.5"
              />
              <line
                x1={286 + Math.cos(a) * 44} y1={190 + Math.sin(a) * 44}
                x2={286 + Math.cos(a) * 50} y2={190 + Math.sin(a) * 50}
                stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" opacity="0.5"
              />
            </g>
          );
        })}

        {/* warning lamp — lit while the fault stands */}
        <circle className={styles.warnGlow} cx="213" cy="268" r="52" fill="url(#mi-warn-glow)" />
        <g transform="translate(190 250)">
          {/* simplified engine glyph */}
          <path
            className={styles.warnLit}
            d="M4 14 h7 V7 h12 v7 h9 l7-7 v7 h6 v13 h-6 v7 h-9 v5 H11 v-5 H4 z"
            fill="var(--accent)"
          />
          <path
            className={styles.warnDim}
            d="M4 14 h7 V7 h12 v7 h9 l7-7 v7 h6 v13 h-6 v7 h-9 v5 H11 v-5 H4 z"
            fill="none" stroke="var(--border)" strokeWidth="2"
          />
        </g>
        {/* secondary telltales */}
        <circle className={styles.warnLit} cx="150" cy="268" r="6" fill="var(--accent)" opacity="0.6" />
        <circle className={styles.warnDim} cx="150" cy="268" r="6" fill="none" stroke="var(--border)" strokeWidth="2" />

        {/* cleared tick — sits beside the lamp, not on top of it, so the final
            frame reads as "the lamp is out" rather than as two overlaid glyphs */}
        <path
          className={styles.cleared}
          d="M296 268 l11 11 l22 -24"
          fill="none" stroke="var(--success)" strokeWidth="5"
          strokeLinecap="round" strokeLinejoin="round"
        />
      </g>

      {/* ---------- OBD port, cable and connector ---------- */}
      <g aria-hidden="true">
        <rect x="150" y="340" width="52" height="22" rx="6" fill="var(--bg)" stroke="var(--border)" strokeWidth="1.5" />
        <rect className={styles.portLive} x="156" y="346" width="40" height="10" rx="3" fill="var(--accent)" opacity="0.8" />
        <path
          className={styles.cable}
          d="M202 351 C 290 351, 300 392, 372 392 C 452 392, 470 300, 540 300"
          pathLength="1"
          fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round"
        />
        <g className={styles.plug}>
          <rect x="206" y="336" width="34" height="30" rx="7" fill="var(--surface-hover)" stroke="var(--accent)" strokeWidth="2" />
          <line x1="214" y1="344" x2="214" y2="358" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="223" y1="344" x2="223" y2="358" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" />
          <line x1="232" y1="344" x2="232" y2="358" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" />
        </g>
      </g>

      {/* ---------- read-out panel ---------- */}
      <g className={styles.codeListOut} aria-hidden="true">
        <g className={styles.codeList}>
          <rect
            x="440" y="104" width="312" height="200" rx="20"
            fill="var(--bg)" stroke="var(--border)" strokeWidth="1.5"
          />
          <text x="464" y="136" fill="var(--text-muted)" fontSize="13" fontFamily="var(--font-body)" letterSpacing="0.08em">
            {t.signature.codeListLabel.toUpperCase().slice(0, 28)}
          </text>
          <line x1="464" y1="150" x2="728" y2="150" stroke="var(--border)" strokeWidth="1" />

          {rows.map((i) => {
            const cls = [styles.codeRow1, styles.codeRow2, styles.codeRow3][i];
            const y = 176 + i * 40;
            return (
              <g key={i} className={cls}>
                <text x="464" y={y + 5} fill="var(--text)" fontSize="15" fontFamily="var(--font-body)">
                  {t.signature.codeRowLabel}
                </text>
                {/* Deliberately blank bars, not invented diagnostic trouble codes. */}
                <rect x="610" y={y - 9} width="86" height="13" rx="4" fill="var(--surface-hover)" />
                <circle cx="716" cy={y - 3} r="5" fill="var(--accent)" opacity={i === 0 ? 1 : 0.45} />
                {i === 0 ? (
                  <line
                    className={styles.codeResolved}
                    x1="464" y1={y - 3} x2="700" y2={y - 3}
                    pathLength="1"
                    stroke="var(--success)" strokeWidth="2" strokeLinecap="round"
                  />
                ) : null}
              </g>
            );
          })}
        </g>
      </g>

      {/* ---------- the implicated part, and a tool moving to it ---------- */}
      <g className={styles.repairOut} aria-hidden="true">
        <circle className={styles.partHalo} cx="596" cy="372" r="58" fill="url(#mi-part-glow)" />
        <rect
          className={styles.partRing}
          x="566" y="346" width="60" height="52" rx="12"
          fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeDasharray="7 6"
        />
        <g className={styles.tool}>
          <path
            d="M676 330 l-34 34 a16 16 0 1 1-16-16 l34-34 a22 22 0 0 0 16 16 z"
            fill="var(--text-muted)"
          />
        </g>
      </g>
    </svg>
  );
}
