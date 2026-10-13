"use client";

import { useState } from "react";
import { dyno, peak, powerAt, torqueAt } from "@/config/widgets";
import {
  LiveReadout,
  Readout,
  WidgetFrame,
  WidgetSlider,
  fmt,
  useCountUp,
} from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

const W = 760;
const H = 300;
const PAD = { l: 52, r: 52, t: 18, b: 34 };

/** Axis maxima, chosen so each quarter gridline is a round figure in both units. */
/**
 * The car on the rollers: a low four-door fastback, front to the right, drawn to
 * the proportions of the brand's own silhouette — roughly three wheel diameters
 * of wheelbase, a roofline that peaks over the cabin and falls away to a short
 * deck, and almost no overhang.
 *
 * Wheels are r=48 at y=116, so their contact line lands at 164 and dips into the
 * cradle between each pair of rollers below.
 */
const WHEELS = [250, 561] as const;
const WHEEL_R = 48;
const SPOKES = [0, 1, 2, 3, 4].map((i) => (i / 5) * Math.PI * 2 - Math.PI / 2);
const BODY =
  "M650 104 C652 90 646 83 632 81 L470 64 C446 60 420 44 392 30 L344 27 " +
  "C300 27 262 36 212 56 L166 76 C154 80 150 88 150 98 L150 140 " +
  "C150 145 153 148 159 148 L207.5 146 " +
  // Each arch is a circle centred on its wheel, four units wider than the tyre,
  // cut off where it crosses the sill. It is the long way round that circle,
  // hence the large-arc flag: the short way bulges the wrong side and swallows
  // the wheel.
  "A52 52 0 1 1 292.5 146 L518.5 146 A52 52 0 1 1 603.5 146 L640 146 " +
  "C646 146 650 142 650 136 Z";
/** The roofline, picked out by the same upper-left light as the rest of the site. */
const ROOFLINE =
  "M650 104 C652 90 646 83 632 81 L470 64 C446 60 420 44 392 30 L344 27 " +
  "C300 27 262 36 212 56 L166 76";
const GLASS = "M455 68 C432 56 414 44 394 32 L348 30 C306 32 268 42 224 62 Z";

const MAX_KW = 160;
const MAX_NM = 480;

function path(gain: number, kind: "power" | "torque"): string {
  const pts: string[] = [];
  for (let rpm = dyno.rpmMin; rpm <= dyno.rpmMax; rpm += 50) {
    const x =
      PAD.l + ((rpm - dyno.rpmMin) / (dyno.rpmMax - dyno.rpmMin)) * (W - PAD.l - PAD.r);
    const value = kind === "power" ? powerAt(rpm, gain) : torqueAt(rpm, gain);
    const max = kind === "power" ? MAX_KW : MAX_NM;
    const y = H - PAD.b - (value / max) * (H - PAD.t - PAD.b);
    pts.push(`${pts.length === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return pts.join(" ");
}

/**
 * ECU widget: a rolling road and the two curves that come off it.
 *
 * The curves are not drawn by hand. Torque comes from the anchor points in
 * config/widgets.ts and power is computed from it as P = M × n / 9549, so the
 * two lines agree with each other at every point and at every slider position.
 *
 * The figures are a representative 2.0 TDI, not anyone's car, and they are not a
 * promise — which the disclaimer under the widget says in as many words.
 */
export function DynoWidget({ t }: { t: LocaleContent }) {
  const [gain, setGain] = useState(0);
  const w = t.widgets.dyno;

  const base = peak(0);
  const now = peak(gain);
  const kw = useCountUp(now.powerKw, 0);
  const hp = useCountUp(now.powerHp, 0);
  const nm = useCountUp(now.torqueNm, 0);

  const dKw = now.powerKw - base.powerKw;
  const dNm = now.torqueNm - base.torqueNm;
  // Wheel speed rises with load; purely a drawing rate, not a measured figure.
  const spin = 1.6 - (gain / dyno.maxGainPercent) * 1.05;

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <WidgetSlider
          label={w.sliderLabel}
          value={gain}
          min={0}
          max={dyno.maxGainPercent}
          step={1}
          display={`+${gain} %`}
          onChange={setGain}
          marks={[
            { at: 0, label: "0 %" },
            { at: dyno.maxGainPercent, label: `+${dyno.maxGainPercent} %` },
          ]}
        />
      }
      readouts={
        <div className="grid grid-cols-2 gap-5">
          <Readout
            label={w.power}
            value={`${fmt(kw)} kW`}
            sub={`${fmt(hp)} k · ${dKw >= 0.5 ? `+${fmt(dKw)} kW` : w.stock}`}
            tone={gain > 0 ? "accent" : "default"}
          />
          <Readout
            label={w.torque}
            value={`${fmt(nm)} Nm`}
            sub={dNm >= 0.5 ? `+${fmt(dNm)} Nm` : w.stock}
            tone={gain > 0 ? "accent" : "default"}
          />
        </div>
      }
    >
      <LiveReadout
        text={`${w.power} ${fmt(now.powerKw)} kW, ${w.torque} ${fmt(now.torqueNm)} Nm, +${gain} %`}
      />

      {/* ── the car on the rollers ── */}
      <svg
        viewBox="0 0 760 212"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "760 / 212" }}
      >
        <defs>
          <linearGradient id="dy-body" x1="0.1" y1="0" x2="0.45" y2="1">
            <stop offset="0%" stopColor="#424c55" />
            <stop offset="42%" stopColor="#262f36" />
            <stop offset="100%" stopColor="#11161a" />
          </linearGradient>
          <linearGradient id="dy-glass" x1="0.1" y1="0" x2="0.5" y2="1">
            <stop offset="0%" stopColor="#a6bac8" stopOpacity="0.42" />
            <stop offset="100%" stopColor="#748794" stopOpacity="0.08" />
          </linearGradient>
          <linearGradient id="dy-tyre" x1="0.25" y1="0" x2="0.75" y2="1">
            <stop offset="0%" stopColor="#222a30" />
            <stop offset="100%" stopColor="#0a0e11" />
          </linearGradient>
          <radialGradient id="dy-smoke">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.16" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* floor, and a pair of rollers under each wheel */}
        <rect x="0" y="200" width="760" height="2" fill="var(--border)" />
        {WHEELS.flatMap((wheel) => [wheel - 32, wheel + 32]).map((cx) => (
          <g key={cx}>
            <circle cx={cx} cy="180" r="20" fill="#171d22" stroke="var(--border)" strokeWidth="1.2" />
            <g
              className="dy-roll"
              style={{ transformOrigin: `${cx}px 180px`, transformBox: "view-box", animationDuration: `${spin}s` }}
            >
              <path
                d={`M${cx - 13} 180 h26 M${cx} 167 v26 M${cx - 9} 171 l18 18 M${cx + 9} 171 l-18 18`}
                stroke="#49545c"
                strokeWidth="1.2"
                strokeLinecap="round"
              />
            </g>
          </g>
        ))}

        {/* body, settling back a little under load */}
        <g
          style={{
            transformOrigin: "405px 140px",
            transformBox: "view-box",
            transform: `rotate(${(-gain / dyno.maxGainPercent) * 1.2}deg)`,
            transition: "transform 420ms var(--ease-ios)",
          }}
        >
          {/* Wheels first: the body is drawn over them, so each arch reads as an
              opening with the tyre behind it rather than a tyre stuck on top. */}
          {WHEELS.map((cx) => (
            <g key={cx}>
              <circle cx={cx} cy="116" r={WHEEL_R} fill="url(#dy-tyre)" stroke="#333c43" strokeWidth="2" />
              <circle cx={cx} cy="116" r="33" fill="#161c21" stroke="#404a52" strokeWidth="1.2" />
              <g
                className="dy-roll"
                style={{ transformOrigin: `${cx}px 116px`, transformBox: "view-box", animationDuration: `${spin}s` }}
              >
                {SPOKES.map((a, i) => (
                  <path
                    key={i}
                    d={`M${(cx + Math.cos(a) * 9).toFixed(1)} ${(116 + Math.sin(a) * 9).toFixed(1)} L${(cx + Math.cos(a) * 30).toFixed(1)} ${(116 + Math.sin(a) * 30).toFixed(1)}`}
                    stroke="#5d6871"
                    strokeWidth="5"
                    strokeLinecap="round"
                  />
                ))}
              </g>
              <circle cx={cx} cy="116" r="8" fill="#434d55" stroke="#616d76" strokeWidth="1" />
            </g>
          ))}

          <path d={BODY} fill="url(#dy-body)" stroke="#39434b" strokeWidth="1" strokeLinejoin="round" />
          <path d={ROOFLINE} fill="none" stroke="#ffffff" strokeOpacity="0.2" strokeWidth="1.3" strokeLinejoin="round" />

          {/* glasshouse and its pillars */}
          <path d={GLASS} fill="url(#dy-glass)" />
          <g stroke="#0d1216" strokeOpacity="0.6" strokeWidth="2.2">
            <path d="M348 30 L344 64" />
            <path d="M394 33 L398 66" />
          </g>

          {/* shut lines, handles and the crease down the flank */}
          <g stroke="#0d1216" strokeOpacity="0.5" strokeWidth="1.3" fill="none">
            <path d="M300 60 L300 140" />
            <path d="M420 64 L422 140" />
          </g>
          <g fill="#6c7984" opacity="0.75">
            <rect x="326" y="78" width="17" height="3.2" rx="1.6" />
            <rect x="440" y="80" width="17" height="3.2" rx="1.6" />
          </g>
          <path
            d="M306 92 C360 89 440 89 512 92"
            fill="none"
            stroke="#ffffff"
            strokeOpacity="0.1"
            strokeWidth="1.6"
          />
          {/* sill shadow, so the car sits in its own light rather than floating */}
          <path d="M296 142 C360 147 460 147 523 142" fill="none" stroke="#070a0c" strokeOpacity="0.5" strokeWidth="4" />
          {/* mirror */}
          <path d="M452 64 l17 -2 q6 0 5 5 l-1 3 l-21 1 z" fill="#2d353c" stroke="#49545c" strokeWidth="0.9" />

          {/* light signatures, the one place the car carries the brand colour */}
          <path d="M602 78 L636 81 q7 1 7 6 l-38 1 z" fill="var(--accent)" opacity="0.92" />
          <path d="M154 86 L190 82 l1 7 l-37 3 z" fill="var(--accent)" opacity="0.7" />
          {/* lower intake and diffuser */}
          <path d="M604 128 L644 127 l-3 10 l-38 1 z" fill="#0b0f12" opacity="0.85" />
          <path d="M154 126 L190 125 l0 10 l-35 1 z" fill="#0b0f12" opacity="0.85" />

        </g>

        {/* exhaust haze, stronger with load */}
        <circle
          cx="124"
          cy="112"
          r="38"
          fill="url(#dy-smoke)"
          style={{ opacity: 0.2 + (gain / dyno.maxGainPercent) * 0.8 }}
        />

        <style>{`
          .dy-roll { animation-name: dy-spin; animation-timing-function: linear; animation-iteration-count: infinite }
          @keyframes dy-spin { to { transform: rotate(360deg) } }
          @media (prefers-reduced-motion: reduce) { .dy-roll { animation: none !important } }
        `}</style>
      </svg>

      {/* ── the curves ── */}
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="mt-4 w-full"
        role="img"
        aria-label={w.chartAlt}
        style={{ aspectRatio: `${W} / ${H}` }}
      >
        {/* grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((f) => {
          const y = H - PAD.b - f * (H - PAD.t - PAD.b);
          return (
            <g key={f}>
              <line x1={PAD.l} y1={y} x2={W - PAD.r} y2={y} stroke="var(--border)" strokeWidth="0.6" />
              <text x={PAD.l - 8} y={y + 4} textAnchor="end" fontSize="10" fill="var(--text-muted)">
                {Math.round(f * MAX_KW)}
              </text>
              <text x={W - PAD.r + 8} y={y + 4} fontSize="10" fill="var(--text-muted)">
                {Math.round(f * MAX_NM)}
              </text>
            </g>
          );
        })}
        {[1000, 2000, 3000, 4000].map((rpm) => {
          const x = PAD.l + ((rpm - dyno.rpmMin) / (dyno.rpmMax - dyno.rpmMin)) * (W - PAD.l - PAD.r);
          return (
            <text key={rpm} x={x} y={H - 12} textAnchor="middle" fontSize="10" fill="var(--text-muted)">
              {rpm}
            </text>
          );
        })}
        <text x={PAD.l - 8} y={PAD.t - 4} textAnchor="end" fontSize="10" fill="var(--text-muted)">kW</text>
        <text x={W - PAD.r + 8} y={PAD.t - 4} fontSize="10" fill="var(--text-muted)">Nm</text>

        {/* stock curves stay visible underneath, so the difference is the point */}
        {gain > 0 ? (
          <g>
            <path d={path(0, "torque")} fill="none" stroke="var(--text-muted)" strokeOpacity="0.45" strokeWidth="1.4" strokeDasharray="4 4" />
            <path d={path(0, "power")} fill="none" stroke="var(--text-muted)" strokeOpacity="0.55" strokeWidth="1.6" />
          </g>
        ) : null}

        <path
          d={path(gain, "torque")}
          fill="none"
          stroke="var(--accent)"
          strokeOpacity="0.55"
          strokeWidth="2"
          strokeDasharray="5 4"
          style={{ transition: "d 300ms var(--ease-ios)" }}
        />
        <path
          d={path(gain, "power")}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="2.8"
          strokeLinecap="round"
          style={{ transition: "d 300ms var(--ease-ios)" }}
        />

        <g transform={`translate(${PAD.l + 10} ${PAD.t + 14})`} fontSize="11">
          <line x1="0" y1="-4" x2="22" y2="-4" stroke="var(--accent)" strokeWidth="2.8" />
          <text x="28" y="0" fill="var(--text)">{w.legendPower}</text>
          <line x1="0" y1="14" x2="22" y2="14" stroke="var(--accent)" strokeOpacity="0.55" strokeWidth="2" strokeDasharray="5 4" />
          <text x="28" y="18" fill="var(--text)">{w.legendTorque}</text>
          {gain > 0 ? (
            <g>
              <line x1="0" y1="32" x2="22" y2="32" stroke="var(--text-muted)" strokeOpacity="0.55" strokeWidth="1.6" />
              <text x="28" y="36" fill="var(--text-muted)">{w.legendStock}</text>
            </g>
          ) : null}
        </g>
      </svg>
    </WidgetFrame>
  );
}
