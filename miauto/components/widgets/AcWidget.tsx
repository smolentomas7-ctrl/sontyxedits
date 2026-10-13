"use client";

import { useState } from "react";
import { aircon, interpolate } from "@/config/widgets";
import { LiveReadout, Readout, WidgetFrame, WidgetSlider, num, useCountUp } from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

/** Mixes two hex colours, so the air and the evaporator plate warm up together. */
function mix(a: string, b: string, t: number): string {
  const f = Math.min(Math.max(t, 0), 1);
  const parse = (hex: string) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
  const [ar = 0, ag = 0, ab = 0] = parse(a);
  const [br = 0, bg = 0, bb = 0] = parse(b);
  const ch = (x: number, y: number) => Math.round(x + (y - x) * f);
  return `rgb(${ch(ar, br)} ${ch(ag, bg)} ${ch(ab, bb)})`;
}

const HOT_PIPE = "M92 146 L92 53 L122 53 M282 53 L344 53 L344 96";
const COLD_PIPE = "M344 114 L344 136 L446 136 L446 156 M446 212 L446 248 L92 248 L92 206";

const FINS_V = Array.from({ length: 19 }, (_, i) => 130 + i * 8);
const FINS_H = Array.from({ length: 9 }, (_, i) => 162 + i * 6);
const BLADES = Array.from({ length: 6 }, (_, i) => (i / 6) * Math.PI * 2);

/**
 * Air conditioning widget: charge against vent temperature.
 *
 * The curve is in config/widgets.ts and it is deliberately not a straight line.
 * The first part of a leak costs a couple of degrees and nobody notices; the
 * last part costs the cooling altogether, which is why a system is measured
 * rather than judged by how it feels.
 */
export function AcWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.aircon;
  const [pct, setPct] = useState<number>(aircon.charge.max);

  const temp = interpolate(aircon.ventTempCurve, "pct", "c", pct);
  const shown = useCountUp(temp, 1);
  const stage = pct < aircon.lowUntil ? 0 : pct < aircon.charge.correctFrom ? 1 : 2;
  const state = w.states[stage] ?? w.states[0];

  const coldest = aircon.ventTempCurve[aircon.ventTempCurve.length - 1]?.c ?? 6;
  const warmest = aircon.ventTempCurve[0]?.c ?? 22;
  const warmth = (temp - coldest) / (warmest - coldest);

  const air = mix("#8ed0f0", "#ff9a66", warmth);
  const plate = mix("#6ec0e6", "#39424a", warmth);
  // Fewer kilograms of refrigerant, fewer segments moving round the loop.
  const gap = 7 + ((aircon.charge.max - pct) / aircon.charge.max) * 26;

  const deg = (value: number) => `${num(value, 1, t.locale)} °C`;

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <WidgetSlider
          label={w.charge}
          value={pct}
          min={aircon.charge.min}
          max={aircon.charge.max}
          step={aircon.charge.step}
          display={`${pct} %`}
          onChange={setPct}
          marks={[
            { at: aircon.charge.min, label: `${aircon.charge.min} %` },
            { at: aircon.charge.max, label: `${aircon.charge.max} %` },
          ]}
        />
      }
      readouts={
        <div className="grid grid-cols-2 gap-5">
          <Readout
            label={w.ventTemp}
            value={deg(shown)}
            tone={stage === 2 ? "success" : stage === 1 ? "accent" : "danger"}
          />
          <Readout label={w.state} value={state} />
        </div>
      }
    >
      <LiveReadout text={`${w.charge} ${pct} %, ${w.ventTemp} ${deg(temp)}, ${state}`} />

      <svg
        viewBox="0 0 640 266"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 266" }}
      >
        <defs>
          <linearGradient id="ac-block" x1="0.1" y1="0" x2="0.7" y2="1">
            <stop offset="0%" stopColor="#3a444c" />
            <stop offset="55%" stopColor="#222a30" />
            <stop offset="100%" stopColor="#161c21" />
          </linearGradient>
          <linearGradient id="ac-comp" x1="0.15" y1="0" x2="0.8" y2="1">
            <stop offset="0%" stopColor="#4d5862" />
            <stop offset="45%" stopColor="#272f36" />
            <stop offset="100%" stopColor="#161b20" />
          </linearGradient>
        </defs>

        {/* ── pipework: hot side out of the compressor, cold side out of the valve ── */}
        <g fill="none" strokeLinecap="round" strokeLinejoin="round">
          <path d={HOT_PIPE} stroke="#2f3740" strokeWidth="5.5" />
          <path d={COLD_PIPE} stroke="#2f3740" strokeWidth="5.5" />
          <path
            className="ac-flow"
            d={HOT_PIPE}
            stroke="var(--accent)"
            strokeWidth="2.6"
            strokeDasharray={`7 ${gap.toFixed(1)}`}
            style={{ transition: "stroke-dasharray 240ms var(--ease-ios)" }}
          />
          <path
            className="ac-flow"
            d={COLD_PIPE}
            stroke={air}
            strokeWidth="2.6"
            strokeDasharray={`7 ${gap.toFixed(1)}`}
            style={{ transition: "stroke-dasharray 240ms var(--ease-ios)" }}
          />
        </g>

        {/* ── condenser ── */}
        <g>
          <rect x="122" y="30" width="160" height="46" rx="5" fill="url(#ac-block)" stroke="#434e57" strokeWidth="1.2" />
          <g stroke="#55616b" strokeWidth="1.1" opacity="0.8">
            {FINS_V.map((x) => (
              <line key={x} x1={x} y1="34" x2={x} y2="72" />
            ))}
          </g>
          <line x1="124" y1="31.5" x2="280" y2="31.5" stroke="#6c7a85" strokeWidth="1" opacity="0.7" />
          <text x="202" y="22" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            {w.parts[1]}
          </text>
        </g>

        {/* ── expansion valve ── */}
        <g>
          <path d="M334 96 L354 96 L344 106 Z" fill="#6d7b86" />
          <path d="M334 114 L354 114 L344 104 Z" fill="#6d7b86" />
          <text x="328" y="109" textAnchor="end" fontSize="10.5" fill="var(--text-muted)">
            {w.parts[2]}
          </text>
        </g>

        {/* ── compressor ── */}
        <g>
          <circle cx="92" cy="178" r="28" fill="url(#ac-comp)" stroke="#49545d" strokeWidth="1.3" />
          <g className="ac-fan" style={{ transformOrigin: "92px 178px", transformBox: "view-box" }}>
            <circle cx="92" cy="178" r="15" fill="#1b2227" stroke="#3d474f" strokeWidth="1.1" />
            {BLADES.map((a, i) => (
              <line
                key={i}
                x1={92 + Math.cos(a) * 5}
                y1={178 + Math.sin(a) * 5}
                x2={92 + Math.cos(a) * 14}
                y2={178 + Math.sin(a) * 14}
                stroke="#6d7b85"
                strokeWidth="2"
                strokeLinecap="round"
              />
            ))}
          </g>
          <text x="92" y="226" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            {w.parts[0]}
          </text>
        </g>

        {/* ── heater box: blower, evaporator, vent ── */}
        <g>
          <rect x="372" y="146" width="148" height="76" rx="6" fill="#0f1417" stroke="#39434b" strokeWidth="1.2" />

          <g className="ac-fan" style={{ transformOrigin: "398px 184px", transformBox: "view-box" }}>
            <circle cx="398" cy="184" r="18" fill="#171d22" stroke="#3d474f" strokeWidth="1.1" />
            {BLADES.map((a, i) => (
              <line
                key={i}
                x1={398 + Math.cos(a) * 6}
                y1={184 + Math.sin(a) * 6}
                x2={398 + Math.cos(a) * 16}
                y2={184 + Math.sin(a) * 16}
                stroke="#5e6b75"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            ))}
          </g>

          <rect
            x="428"
            y="156"
            width="36"
            height="56"
            rx="3"
            fill={plate}
            fillOpacity="0.22"
            stroke={plate}
            strokeWidth="1.3"
            style={{ transition: "fill 240ms var(--ease-ios), stroke 240ms var(--ease-ios)" }}
          />
          <g stroke={plate} strokeWidth="1.1" opacity="0.55">
            {FINS_H.map((y) => (
              <line key={y} x1="430" y1={y} x2="462" y2={y} />
            ))}
          </g>
          <text x="436" y="238" textAnchor="end" fontSize="10.5" fill="var(--text-muted)">
            {w.parts[3]}
          </text>

          {/* vent louvres */}
          <g stroke="#6d7b86" strokeWidth="3.4" strokeLinecap="round">
            <line x1="506" y1="156" x2="516" y2="162" />
            <line x1="506" y1="179" x2="516" y2="185" />
            <line x1="506" y1="202" x2="516" y2="208" />
          </g>
        </g>

        {/* ── air out of the vent ── */}
        <g fill="none" stroke={air} strokeWidth="3" strokeLinecap="round" style={{ transition: "stroke 240ms var(--ease-ios)" }}>
          {[164, 186, 208].map((y, i) => (
            <g key={y} className="ac-puff" style={{ animationDelay: `${i * 140}ms` }}>
              <path d={`M526 ${y} C556 ${y - 5}, 574 ${y + 5}, 600 ${y}`} />
              <path d={`M592 ${y - 6} L600 ${y} L592 ${y + 6}`} />
            </g>
          ))}
        </g>

        <text
          x="564"
          y="138"
          textAnchor="middle"
          fontSize="19"
          fontWeight="600"
          fill={air}
          style={{ transition: "fill 240ms var(--ease-ios)" }}
        >
          {deg(temp)}
        </text>
        <text x="604" y="250" textAnchor="end" fontSize="10.5" fill="var(--text-muted)">
          {w.cabin} ~{aircon.cabinTemp} °C
        </text>
      </svg>

      <style>{`
        .ac-flow { animation: ac-run 1.4s linear infinite }
        .ac-fan { animation: ac-spin 2.6s linear infinite }
        .ac-puff { animation: ac-puff 2.8s var(--ease-ios) infinite }
        @keyframes ac-run { to { stroke-dashoffset: -34 } }
        @keyframes ac-spin { to { transform: rotate(360deg) } }
        @keyframes ac-puff {
          0%, 100% { opacity: .6; transform: translateX(0) }
          50% { opacity: 1; transform: translateX(5px) }
        }
        @media (prefers-reduced-motion: reduce) {
          .ac-flow, .ac-fan, .ac-puff { animation: none !important }
          .ac-puff { opacity: .85 }
        }
      `}</style>
    </WidgetFrame>
  );
}
