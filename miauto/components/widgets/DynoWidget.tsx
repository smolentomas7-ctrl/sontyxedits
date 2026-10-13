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
        viewBox="0 0 760 180"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "760 / 180" }}
      >
        <defs>
          <linearGradient id="dy-body" x1="0.1" y1="0" x2="0.6" y2="1">
            <stop offset="0%" stopColor="#39424a" />
            <stop offset="55%" stopColor="#222a31" />
            <stop offset="100%" stopColor="#141a1f" />
          </linearGradient>
          <linearGradient id="dy-glass" x1="0" y1="0" x2="0.4" y2="1">
            <stop offset="0%" stopColor="#8fa3b0" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#8fa3b0" stopOpacity="0.12" />
          </linearGradient>
          <radialGradient id="dy-smoke">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.16" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* floor and rollers */}
        <rect x="0" y="150" width="760" height="2" fill="var(--border)" />
        {[266, 338].map((cx) => (
          <g key={cx}>
            <circle cx={cx} cy="132" r="26" fill="#1b2227" stroke="var(--border)" strokeWidth="1.2" />
            <g style={{ transformOrigin: `${cx}px 132px`, animation: `dy-spin ${spin}s linear infinite` }}>
              <path d={`M${cx - 18} 132 h36 M${cx} 114 v36`} stroke="var(--text-muted)" strokeOpacity="0.4" strokeWidth="1.4" />
            </g>
          </g>
        ))}

        {/* body, tilting back a little under load */}
        <g
          style={{
            transformOrigin: "300px 130px",
            transform: `rotate(${(-gain / dyno.maxGainPercent) * 1.1}deg)`,
            transition: "transform 420ms var(--ease-ios)",
          }}
        >
          <path
            d="M150 128 L168 92 Q176 78 196 76 L300 70 Q330 69 356 82 L418 110 L470 118 Q486 121 486 132 L486 140 L150 140 Z"
            fill="url(#dy-body)"
          />
          <path d="M206 84 L296 79 Q320 78 340 88 L382 108 L212 112 Z" fill="url(#dy-glass)" />
          <path
            d="M150 128 L168 92 Q176 78 196 76 L300 70"
            fill="none"
            stroke="#ffffff"
            strokeOpacity="0.16"
            strokeWidth="1.2"
          />
          {/* wheels */}
          {[218, 420].map((cx) => (
            <g key={cx}>
              <circle cx={cx} cy="140" r="30" fill="#0e1316" stroke="#2b3339" strokeWidth="2" />
              <g style={{ transformOrigin: `${cx}px 140px`, animation: `dy-spin ${spin}s linear infinite` }}>
                <path
                  d={`M${cx - 15} 140 h30 M${cx} 125 v30 M${cx - 11} 129 l22 22 M${cx + 11} 129 l-22 22`}
                  stroke="#4a545b"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                />
              </g>
              <circle cx={cx} cy="140" r="6" fill="#39434a" />
            </g>
          ))}
        </g>

        {/* exhaust haze, stronger with load */}
        <circle
          cx="128"
          cy="126"
          r="34"
          fill="url(#dy-smoke)"
          style={{ opacity: 0.25 + (gain / dyno.maxGainPercent) * 0.75 }}
        />

        <style>{`@keyframes dy-spin { to { transform: rotate(360deg) } }
          @media (prefers-reduced-motion: reduce) { [style*="dy-spin"] { animation: none !important } }`}</style>
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
