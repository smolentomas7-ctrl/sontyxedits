"use client";

import { useState } from "react";
import { alignment } from "@/config/widgets";
import { LiveReadout, Readout, WidgetFrame, WidgetSlider, num } from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

/** The three panels: front view, top view, tyre in section. */
const FRONT = { cx: 118, road: 196, left: 58, right: 178 };
const TOP = { cx: 322, axle: 130, left: 256, right: 388 };
const SEC = { x: 436, w: 180, casing: 96, road: 170 };
/** Full tread thickness in drawing units, and how far the angles are exaggerated. */
const TREAD = 30;
const EXAGGERATE = 5;

/** Wheel alignment: what toe and camber do to the tread and to the steering. */
export function AlignmentWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.alignment;
  const dec = (value: number, places = 1) => num(value, places, t.locale);
  const [toe, setToe] = useState(0);
  const [camber, setCamber] = useState(-0.4);

  const camberOk = camber >= alignment.camber.okFrom && camber <= alignment.camber.okTo;
  const toeOk = Math.abs(toe) <= alignment.toe.ok;
  const allOk = camberOk && toeOk;

  // Camber decides which edge takes the load; toe decides how fast it scrubs.
  const wearSide = camber < alignment.camber.okFrom ? "inner" : camber > alignment.camber.okTo ? "outer" : "even";
  const wearLabel = wearSide === "inner" ? w.wearInner : wearSide === "outer" ? w.wearOuter : w.wearEven;
  const pullLabel = toe > alignment.toe.ok ? w.pullRight : toe < -alignment.toe.ok ? w.pullLeft : w.pullNone;

  const severity = Math.min(
    1,
    Math.max(
      Math.abs(toe) / alignment.toe.max,
      camberOk ? 0 : Math.abs(camber - (camber < 0 ? alignment.camber.okFrom : alignment.camber.okTo)) / 1.8,
    ),
  );

  /** Tread left at a point across the tread, 0 = inner edge, 1 = outer edge. */
  const left = (u: number) => {
    const bias = wearSide === "inner" ? 1 - u : wearSide === "outer" ? u : 0;
    return TREAD * (1 - 0.72 * bias * severity);
  };

  /** The tread/casing boundary: it drops where the shoulder has been scrubbed off. */
  const profile = () => {
    const pts: string[] = [];
    for (let i = 0; i <= 24; i += 1) {
      const u = i / 24;
      pts.push(`${(SEC.x + u * SEC.w).toFixed(1)} ${(SEC.road - left(u)).toFixed(1)}`);
    }
    return `M${SEC.x} ${SEC.road} L${pts.join(" L")} L${SEC.x + SEC.w} ${SEC.road} Z`;
  };

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <div className="space-y-5">
          <WidgetSlider
            label={w.toe}
            value={toe}
            min={alignment.toe.min}
            max={alignment.toe.max}
            step={alignment.toe.step}
            display={`${toe > 0 ? "+" : ""}${dec(toe, 2)}°`}
            onChange={setToe}
          />
          <WidgetSlider
            label={w.camber}
            value={camber}
            min={alignment.camber.min}
            max={alignment.camber.max}
            step={alignment.camber.step}
            display={`${camber > 0 ? "+" : ""}${dec(camber, 1)}°`}
            onChange={setCamber}
          />
        </div>
      }
      readouts={
        <div className="grid grid-cols-2 gap-5">
          <Readout
            label={w.wear}
            value={wearLabel}
            tone={wearSide === "even" ? "success" : "danger"}
          />
          <Readout
            label={w.pull}
            value={pullLabel}
            tone={pullLabel === w.pullNone ? "success" : "danger"}
          />
        </div>
      }
    >
      <LiveReadout text={`${w.wear}: ${wearLabel}. ${w.pull}: ${pullLabel}.`} />

      <svg
        viewBox="0 0 640 250"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 250" }}
      >
        <defs>
          <linearGradient id="al-wheel" x1="0.1" y1="0" x2="0.9" y2="1">
            <stop offset="0%" stopColor="#333c43" />
            <stop offset="55%" stopColor="#1b2127" />
            <stop offset="100%" stopColor="#11161a" />
          </linearGradient>
          <linearGradient id="al-rubber" x1="0.15" y1="0" x2="0.7" y2="1">
            <stop offset="0%" stopColor="#39424a" />
            <stop offset="50%" stopColor="#20262b" />
            <stop offset="100%" stopColor="#13181c" />
          </linearGradient>
        </defs>

        {/* ── front view: what camber does ── */}
        <g>
          <line x1="24" y1={FRONT.road} x2="212" y2={FRONT.road} stroke="#4a555e" strokeWidth="1.6" />
          <rect x={FRONT.left} y="134" width={FRONT.right - FRONT.left} height="9" rx="4" fill="#2b333a" stroke="#454f58" strokeWidth="1" />
          {[
            { x: FRONT.left, dir: -1 },
            { x: FRONT.right, dir: 1 },
          ].map((wheel) => (
            <g
              key={wheel.x}
              style={{
                // The wheel pivots on its hub, as it does on the car, so it stays
                // on the end of the axle instead of swinging off it.
                transformOrigin: `${wheel.x}px ${FRONT.road - 38}px`,
                transformBox: "view-box",
                transform: `rotate(${camber * EXAGGERATE * wheel.dir}deg)`,
                transition: "transform 260ms var(--ease-ios)",
              }}
            >
              <rect
                x={wheel.x - 12}
                y={FRONT.road - 76}
                width="24"
                height="76"
                rx="5"
                fill="url(#al-wheel)"
                stroke={camberOk ? "var(--success)" : "var(--accent)"}
                strokeWidth="1.8"
                style={{ transition: "stroke 240ms var(--ease-ios)" }}
              />
              <circle cx={wheel.x} cy={FRONT.road - 38} r="9" fill="#232b31" stroke="#4a555e" strokeWidth="1.1" />
              <circle cx={wheel.x} cy={FRONT.road - 38} r="3" fill="#5e6a74" />
            </g>
          ))}
          <line x1={FRONT.cx} y1="112" x2={FRONT.cx} y2={FRONT.road} stroke="#39434b" strokeWidth="1" strokeDasharray="4 5" />
          <text x={FRONT.cx} y="220" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            {w.frontView}
          </text>
          <text
            x={FRONT.cx}
            y="236"
            textAnchor="middle"
            fontSize="11.5"
            fill={camberOk ? "var(--success)" : "var(--accent)"}
          >
            {camber > 0 ? "+" : ""}
            {dec(camber, 1)}°
          </text>
        </g>

        {/* ── top view: what toe does ── */}
        <g>
          <g stroke="#4a555e" strokeWidth="1.4" fill="none" strokeLinecap="round">
            <line x1={TOP.cx} y1="54" x2={TOP.cx} y2="34" />
            <path d={`M${TOP.cx - 5} 41 L${TOP.cx} 34 L${TOP.cx + 5} 41`} />
          </g>
          <line x1={TOP.left} y1={TOP.axle} x2={TOP.right} y2={TOP.axle} stroke="#2b333a" strokeWidth="7" strokeLinecap="round" />
          {[
            { x: TOP.left, dir: 1 },
            { x: TOP.right, dir: -1 },
          ].map((wheel) => (
            <g
              key={wheel.x}
              style={{
                transformOrigin: `${wheel.x}px ${TOP.axle}px`,
                transformBox: "view-box",
                transform: `rotate(${toe * EXAGGERATE * 3 * wheel.dir}deg)`,
                transition: "transform 260ms var(--ease-ios)",
              }}
            >
              <rect
                x={wheel.x - 10}
                y={TOP.axle - 34}
                width="20"
                height="68"
                rx="4"
                fill="url(#al-wheel)"
                stroke={toeOk ? "var(--success)" : "var(--accent)"}
                strokeWidth="1.8"
                style={{ transition: "stroke 240ms var(--ease-ios)" }}
              />
              <g stroke="#4a555e" strokeWidth="1" opacity="0.7">
                <line x1={wheel.x - 5} y1={TOP.axle - 28} x2={wheel.x - 5} y2={TOP.axle + 28} />
                <line x1={wheel.x + 5} y1={TOP.axle - 28} x2={wheel.x + 5} y2={TOP.axle + 28} />
              </g>
            </g>
          ))}
          <line x1={TOP.cx} y1="60" x2={TOP.cx} y2="196" stroke="#39434b" strokeWidth="1" strokeDasharray="4 5" />
          <text x={TOP.cx} y="220" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            {w.topView}
          </text>
          <text
            x={TOP.cx}
            y="236"
            textAnchor="middle"
            fontSize="11.5"
            fill={toeOk ? "var(--success)" : "var(--accent)"}
          >
            {toe > 0 ? "+" : ""}
            {dec(toe, 2)}°
          </text>
        </g>

        {/* ── the tread that pays for it ── */}
        <g>
          <rect x={SEC.x} y={SEC.casing} width={SEC.w} height={SEC.road - SEC.casing} rx="6" fill="#10151a" stroke="#39434b" strokeWidth="1" />
          <g stroke="#55616b" strokeWidth="1" opacity="0.45">
            <line x1={SEC.x + 6} y1={SEC.casing + 12} x2={SEC.x + SEC.w - 6} y2={SEC.casing + 12} />
            <line x1={SEC.x + 6} y1={SEC.casing + 19} x2={SEC.x + SEC.w - 6} y2={SEC.casing + 19} />
          </g>
          <path
            d={profile()}
            fill="url(#al-rubber)"
            stroke={allOk ? "var(--success)" : "var(--accent)"}
            strokeWidth="1.6"
            style={{ transition: "d 260ms var(--ease-ios), stroke 240ms var(--ease-ios)" }}
          />
          {/* grooves, as deep as the tread that is left under them */}
          {[0.18, 0.39, 0.61, 0.82].map((u) => {
            const h = Math.max(left(u) - 8, 2);
            return (
              <rect
                key={u}
                x={SEC.x + u * SEC.w - 6}
                y={SEC.road - h}
                width="12"
                height={h}
                rx="2"
                fill="#0b0f12"
                style={{ transition: "y 260ms var(--ease-ios), height 260ms var(--ease-ios)" }}
              />
            );
          })}
          <line x1={SEC.x - 6} y1={SEC.road} x2={SEC.x + SEC.w + 6} y2={SEC.road} stroke="#4a555e" strokeWidth="1.6" />
          <text x={SEC.x} y="190" fontSize="9.5" fill="var(--text-muted)">
            {w.wearInner.replace(/^po /, "")}
          </text>
          <text x={SEC.x + SEC.w} y="190" textAnchor="end" fontSize="9.5" fill="var(--text-muted)">
            {w.wearOuter.replace(/^po /, "")}
          </text>
          <text x={SEC.x + SEC.w / 2} y="220" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            {w.section}
          </text>
          <text
            x={SEC.x + SEC.w / 2}
            y="236"
            textAnchor="middle"
            fontSize="11.5"
            fill={allOk ? "var(--success)" : "var(--accent)"}
          >
            {allOk ? w.ok : wearLabel}
          </text>
        </g>

        <text x="20" y="20" fontSize="9.5" fill="var(--text-muted)" opacity="0.8">
          {w.exaggerated}
        </text>
      </svg>
    </WidgetFrame>
  );
}
