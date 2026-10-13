"use client";

import { useState } from "react";
import { interpolate, tyres } from "@/config/widgets";
import { LiveReadout, Readout, WidgetFrame, WidgetSlider, useCountUp, fmt, num } from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

/** Tread band in section: six blocks with five grooves cut between them. */
const BAND = { x: 190, w: 260, top: 46, road: 122 };
const GROOVES = [0, 1, 2, 3, 4].map((i) => BAND.x + 30 + i * 46);
const GROOVE_W = 16;
/** Depth of a full-depth groove, in drawing units. */
const FULL_DEPTH = 48;

/** Braking comparison along the bottom. */
const AXIS = { x0: 40, x1: 600, y: 228, maxM: 64 };
const scale = (m: number) => AXIS.x0 + (m / AXIS.maxM) * (AXIS.x1 - AXIS.x0);

/**
 * Tyres: what tread depth does to a wet stop.
 *
 * The section is the honest picture of why — the grooves are the only route the
 * water has out from under the tyre, and when they are shallow the water stays
 * and the rubber stops touching the road. The distances come from published wet
 * braking tests and the widget says so beneath itself.
 */
export function TyreWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.tyres;
  const dec = (value: number) => num(value, 1, t.locale);
  const [mm, setMm] = useState<number>(tyres.depth.max);

  const distance = interpolate(tyres.wetBraking, "mm", "m", mm);
  const best = interpolate(tyres.wetBraking, "mm", "m", tyres.depth.max);
  const shown = useCountUp(distance, 0);
  const extra = distance - best;
  const atLegal = mm <= tyres.depth.legalMin + 0.05;

  const share = (mm - tyres.depth.min) / (tyres.depth.max - tyres.depth.min);
  const depth = (mm / tyres.depth.max) * FULL_DEPTH;
  const legalDepth = (tyres.depth.legalMin / tyres.depth.max) * FULL_DEPTH;
  const tone = atLegal ? "var(--danger)" : extra > 6 ? "var(--accent)" : "var(--success)";

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <WidgetSlider
          label={w.depth}
          value={mm}
          min={tyres.depth.min}
          max={tyres.depth.max}
          step={tyres.depth.step}
          display={`${dec(mm)} mm`}
          onChange={setMm}
          marks={[
            { at: tyres.depth.legalMin, label: `${dec(tyres.depth.legalMin)} mm` },
            { at: tyres.depth.max, label: `${dec(tyres.depth.max)} mm` },
          ]}
        />
      }
      readouts={
        <div className="grid grid-cols-2 gap-5">
          <Readout
            label={w.braking}
            value={`${fmt(shown)} m`}
            sub={w.fromSpeed}
            tone={atLegal ? "danger" : extra > 6 ? "accent" : "success"}
          />
          <Readout
            label={w.versusNew}
            value={extra < 0.5 ? "—" : `+${fmt(extra)} m`}
            tone={extra > 6 ? "danger" : "default"}
          />
        </div>
      }
    >
      <LiveReadout text={`${w.depth} ${dec(mm)} mm, ${w.braking} ${fmt(distance)} m`} />

      <svg
        viewBox="0 0 640 258"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 258" }}
      >
        <defs>
          <linearGradient id="ty-rubber" x1="0.15" y1="0" x2="0.7" y2="1">
            <stop offset="0%" stopColor="#39424a" />
            <stop offset="45%" stopColor="#20262b" />
            <stop offset="100%" stopColor="#13181c" />
          </linearGradient>
          <linearGradient id="ty-road" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#262d33" />
            <stop offset="100%" stopColor="#11161a" />
          </linearGradient>
          <linearGradient id="ty-water" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6fb6dd" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#3f7fa3" stopOpacity="0.25" />
          </linearGradient>
        </defs>

        {/* ── road and the water film on it ── */}
        <rect x="120" y={BAND.road} width="400" height="26" fill="url(#ty-road)" />
        <line x1="120" y1={BAND.road} x2="520" y2={BAND.road} stroke="#4a555e" strokeWidth="1.2" />
        <rect x="120" y={BAND.road - 7} width="400" height="7" fill="url(#ty-water)" />

        {/* water that the grooves cannot take stays under the tread */}
        <rect
          x={BAND.x}
          y={BAND.road - 5}
          width={BAND.w}
          height="5"
          fill="#7cc2e6"
          opacity={(1 - share) * 0.75}
          style={{ transition: "opacity 240ms var(--ease-ios)" }}
        />

        {/* ── the tread in section ── */}
        <g>
          <path
            d={`M${BAND.x} ${BAND.road} L${BAND.x} ${BAND.top + 10} Q${BAND.x} ${BAND.top} ${BAND.x + 10} ${BAND.top} L${BAND.x + BAND.w - 10} ${BAND.top} Q${BAND.x + BAND.w} ${BAND.top} ${BAND.x + BAND.w} ${BAND.top + 10} L${BAND.x + BAND.w} ${BAND.road} Z`}
            fill="url(#ty-rubber)"
            stroke="#49545d"
            strokeWidth="1.2"
          />
          {/* belt plies */}
          <g stroke="#55616b" strokeWidth="1" opacity="0.5">
            <line x1={BAND.x + 6} y1={BAND.top + 16} x2={BAND.x + BAND.w - 6} y2={BAND.top + 16} />
            <line x1={BAND.x + 6} y1={BAND.top + 23} x2={BAND.x + BAND.w - 6} y2={BAND.top + 23} />
          </g>

          {/* grooves, cut up from the contact face */}
          {GROOVES.map((x) => (
            <g key={x}>
              <rect
                x={x}
                y={BAND.road - depth}
                width={GROOVE_W}
                height={depth}
                rx="2"
                fill="#0b0f12"
                style={{ transition: "y 240ms var(--ease-ios), height 240ms var(--ease-ios)" }}
              />
              <rect
                x={x + 1}
                y={BAND.road - Math.min(depth, 5)}
                width={GROOVE_W - 2}
                height={Math.min(depth, 5)}
                fill="#7cc2e6"
                opacity={0.5}
                style={{ transition: "y 240ms var(--ease-ios), height 240ms var(--ease-ios)" }}
              />
              <line
                x1={x}
                y1={BAND.road - depth}
                x2={x + GROOVE_W}
                y2={BAND.road - depth}
                stroke="#5a656e"
                strokeWidth="0.8"
                opacity="0.6"
                style={{ transition: "y1 240ms var(--ease-ios), y2 240ms var(--ease-ios)" }}
              />
            </g>
          ))}

          {/* the wear bar sits at the legal minimum */}
          <g opacity="0.75">
            <line
              x1={BAND.x + 4}
              y1={BAND.road - legalDepth}
              x2={BAND.x + BAND.w - 4}
              y2={BAND.road - legalDepth}
              stroke="var(--danger)"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text x={BAND.x + 6} y={BAND.road - legalDepth - 5} fontSize="9.5" fill="var(--danger)">
              {dec(tyres.depth.legalMin)} mm
            </text>
          </g>

          {/* current depth, dimensioned */}
          <g stroke={tone} strokeWidth="1.2" style={{ transition: "stroke 240ms var(--ease-ios)" }}>
            <line x1={BAND.x + BAND.w + 16} y1={BAND.road - depth} x2={BAND.x + BAND.w + 16} y2={BAND.road} />
            <line x1={BAND.x + BAND.w + 12} y1={BAND.road - depth} x2={BAND.x + BAND.w + 20} y2={BAND.road - depth} />
            <line x1={BAND.x + BAND.w + 12} y1={BAND.road} x2={BAND.x + BAND.w + 20} y2={BAND.road} />
          </g>
          <text
            x={BAND.x + BAND.w + 26}
            y={BAND.road - depth / 2 + 4}
            fontSize="11.5"
            fill={tone}
            style={{ transition: "fill 240ms var(--ease-ios)" }}
          >
            {dec(mm)} mm
          </text>
        </g>

        {/* water leaving sideways: only as fast as the grooves allow */}
        <g
          stroke="#7cc2e6"
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          opacity={0.25 + share * 0.6}
          style={{ transition: "opacity 240ms var(--ease-ios)" }}
        >
          <path d="M184 114 L150 114 M160 108 L150 114 L160 120" />
          <path d="M456 114 L490 114 M480 108 L490 114 L480 120" />
        </g>

        {/* ── wet braking from 80 km/h ── */}
        <g>
          <line x1={AXIS.x0} y1={AXIS.y} x2={AXIS.x1} y2={AXIS.y} stroke="#39434b" strokeWidth="1" />
          {[0, 20, 40, 60].map((m) => (
            <g key={m}>
              <line x1={scale(m)} y1={AXIS.y - 4} x2={scale(m)} y2={AXIS.y + 4} stroke="#39434b" strokeWidth="1" />
              <text x={scale(m)} y={AXIS.y + 18} textAnchor="middle" fontSize="10" fill="var(--text-muted)">
                {m} m
              </text>
            </g>
          ))}

          {/* a new tyre, for reference — only once it differs from the current one */}
          {extra >= 0.5 ? (
            <g>
              <line
                x1={AXIS.x0}
                y1={AXIS.y - 36}
                x2={scale(best)}
                y2={AXIS.y - 36}
                stroke="#6b7883"
                strokeWidth="7"
                strokeLinecap="round"
              />
              <text x={scale(best) + 12} y={AXIS.y - 32} fontSize="10.5" fill="var(--text-muted)">
                {dec(tyres.depth.max)} mm · {fmt(best)} m
              </text>
            </g>
          ) : null}

          {/* the current depth */}
          <line
            x1={AXIS.x0}
            y1={AXIS.y - 56}
            x2={scale(distance)}
            y2={AXIS.y - 56}
            stroke={tone}
            strokeWidth="9"
            strokeLinecap="round"
            style={{ transition: "stroke 240ms var(--ease-ios)" }}
          />
          <text
            x={scale(distance) + 14}
            y={AXIS.y - 52}
            fontSize="11"
            fill={tone}
            style={{ transition: "fill 240ms var(--ease-ios)" }}
          >
            {dec(mm)} mm · {fmt(distance)} m
          </text>

          {/* how much further, drawn between the two ends */}
          {extra >= 0.5 ? (
            <g stroke={tone} strokeWidth="1.1" style={{ transition: "stroke 240ms var(--ease-ios)" }}>
              <line x1={scale(best)} y1={AXIS.y - 46} x2={scale(distance)} y2={AXIS.y - 46} strokeDasharray="3 3" />
              <line x1={scale(best)} y1={AXIS.y - 50} x2={scale(best)} y2={AXIS.y - 42} />
              <line x1={scale(distance)} y1={AXIS.y - 50} x2={scale(distance)} y2={AXIS.y - 42} />
            </g>
          ) : null}
        </g>

        {atLegal ? (
          <text x={AXIS.x0} y="178" fontSize="11.5" fill="var(--danger)">
            {w.legalMin} — {dec(tyres.depth.legalMin)} mm
          </text>
        ) : null}
      </svg>
    </WidgetFrame>
  );
}
