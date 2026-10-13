"use client";

import clsx from "clsx";
import { RotateCcw } from "lucide-react";
import { useState } from "react";
import { electrics } from "@/config/widgets";
import { usePressHandlers } from "@/lib/motion";
import { LiveReadout, Readout, WidgetFrame, num } from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

/** x of each measuring pad on the live wire, left to right. */
const PAD_X = [104, 222, 356, 452] as const;
const WIRE_Y = 74;
/**
 * Where the break is drawn for each fault position. These are the places a
 * circuit actually fails: the fuse itself, then the harness before and after the
 * connector — never halfway through a component, which is why this is a table
 * rather than the midpoint between two pads.
 */
const BREAK_X = [168, 254, 404] as const;

/**
 * Electrics widget: measure, do not guess.
 *
 * The circuit holds a break the visitor cannot see. Measuring a point shows
 * whether voltage still arrives there, and the break is located the way it is
 * located on a car — the last point that has voltage and the first that does
 * not sit either side of it. The break moves on every reset, so the widget
 * teaches the method rather than one answer.
 */
export function ElectricsWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.electrics;
  const press = usePressHandlers();
  const volt = (value: number) => `${num(value, 1, t.locale)} V`;

  const [round, setRound] = useState(0);
  const [measured, setMeasured] = useState<readonly number[]>([]);

  const points = w.points;
  const faultAfter =
    electrics.faultSequence[round % electrics.faultSequence.length] ?? 1;

  const volts = (index: number) => (index <= faultAfter ? electrics.systemVolts : 0);
  const seen = (index: number) => measured.includes(index);
  const found = seen(faultAfter) && seen(faultAfter + 1);

  const before = points[faultAfter];
  const after = points[faultAfter + 1];
  const answer = found && before && after ? `${before.label} → ${after.label}` : "—";

  const liveTo = PAD_X[faultAfter] ?? PAD_X[0];
  const breakX = BREAK_X[faultAfter] ?? 254;

  const last = measured[measured.length - 1];
  const lastPoint = last === undefined ? null : points[last];

  function measure(index: number) {
    setMeasured((current) => (current.includes(index) ? current : [...current, index]));
  }

  function reset() {
    setMeasured([]);
    setRound((r) => r + 1);
  }

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <div>
          <p className="text-[0.875rem] text-[color:var(--text-muted)]">{w.instruction}</p>
          <ul className="mt-4 grid grid-cols-2 gap-3">
            {points.map((point, index) => {
              const done = seen(index);
              const live = volts(index) > 0;
              return (
                <li key={point.id}>
                  <button
                    type="button"
                    onClick={() => measure(index)}
                    aria-label={`${w.measure}: ${point.label}`}
                    className={clsx(
                      "tappable flex h-[58px] w-full flex-col justify-center rounded-[var(--radius-control)] border px-3.5 text-left",
                      done
                        ? live
                          ? "border-[color-mix(in_srgb,var(--success)_55%,var(--border))] bg-[color-mix(in_srgb,var(--success)_10%,transparent)]"
                          : "border-[color-mix(in_srgb,var(--danger)_55%,var(--border))] bg-[color-mix(in_srgb,var(--danger)_10%,transparent)]"
                        : "border-[var(--border)] hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))]",
                    )}
                    {...press}
                  >
                    <span className="text-[0.8125rem] text-[color:var(--text-muted)]">
                      {point.label}
                    </span>
                    <span
                      className={clsx(
                        "font-heading text-[0.9375rem] font-semibold tabular-nums",
                        !done && "text-[color:var(--text-muted)]",
                        done && live && "text-[color:var(--success)]",
                        done && !live && "text-[color:var(--danger)]",
                      )}
                    >
                      {done ? volt(volts(index)) : w.notMeasured}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
          {measured.length > 0 ? (
            <button
              type="button"
              onClick={reset}
              className="tappable mt-4 inline-flex h-11 items-center gap-2 rounded-[var(--radius-control)] border border-[var(--border)] px-4 text-[0.875rem]"
              {...press}
            >
              <RotateCcw size={15} aria-hidden="true" />
              {w.reset}
            </button>
          ) : null}
        </div>
      }
      readouts={
        <Readout
          label={w.found}
          value={answer}
          tone={found ? "success" : "default"}
        />
      }
    >
      <LiveReadout
        text={
          found
            ? `${w.found}: ${answer}`
            : lastPoint
              ? `${lastPoint.label}: ${volt(volts(last ?? 0))}`
              : w.instruction
        }
      />

      <svg
        viewBox="0 0 640 262"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 262" }}
      >
        <defs>
          <linearGradient id="el-batt" x1="0.1" y1="0" x2="0.7" y2="1">
            <stop offset="0%" stopColor="#333d44" />
            <stop offset="60%" stopColor="#1d242a" />
            <stop offset="100%" stopColor="#141a1f" />
          </linearGradient>
          <linearGradient id="el-box" x1="0.1" y1="0" x2="0.6" y2="1">
            <stop offset="0%" stopColor="#3a444c" />
            <stop offset="100%" stopColor="#1b2126" />
          </linearGradient>
          <radialGradient id="el-bulb">
            <stop offset="0%" stopColor="#5b6a74" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#5b6a74" stopOpacity="0.04" />
          </radialGradient>
        </defs>

        {/* ── the live run: grey until the break is located, then split ── */}
        <g fill="none" strokeWidth="3.4" strokeLinecap="round" strokeLinejoin="round">
          <path d={`M58 122 L58 ${WIRE_Y} L470 ${WIRE_Y} L470 126`} stroke="#2b3238" />
          {found ? (
            <path
              d={`M58 122 L58 ${WIRE_Y} L${liveTo} ${WIRE_Y}`}
              stroke="var(--accent)"
              style={{ transition: "stroke 240ms var(--ease-ios)" }}
            />
          ) : (
            <path d={`M58 122 L58 ${WIRE_Y} L470 ${WIRE_Y} L470 126`} stroke="#46525b" />
          )}
          <path d="M58 223 L58 236 L470 236 L470 182" stroke="#46525b" />
        </g>
        <g stroke="#5b6a74" strokeWidth="2.2" strokeLinecap="round">
          <line x1="250" y1="242" x2="274" y2="242" />
          <line x1="254" y1="248" x2="270" y2="248" />
          <line x1="258" y1="254" x2="266" y2="254" />
        </g>

        {/* ── battery ── */}
        <g>
          <rect x="24" y="130" width="68" height="84" rx="7" fill="url(#el-batt)" stroke="#39434b" strokeWidth="1.2" />
          <rect x="30" y="136" width="56" height="18" rx="4" fill="#0f1417" opacity="0.7" />
          <rect x="50" y="122" width="16" height="9" rx="2" fill="#5b6a74" />
          <rect x="50" y="214" width="16" height="9" rx="2" fill="#44505a" />
          <text x="58" y="150" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
            12 V
          </text>
          <text x="58" y="182" textAnchor="middle" fontSize="14" fill="#6e7d87">
            +
          </text>
          <text x="58" y="204" textAnchor="middle" fontSize="14" fill="#6e7d87">
            −
          </text>
        </g>

        {/* ── fuse holder ── */}
        <g>
          <rect x="140" y="60" width="56" height="28" rx="5" fill="url(#el-box)" stroke="#434e57" strokeWidth="1.1" />
          <path d={`M150 ${WIRE_Y} l7 -6 l7 12 l7 -12 l7 12 l7 -6 l6 0`} fill="none" stroke="#8c9aa4" strokeWidth="1.5" />
        </g>

        {/* ── connector ── */}
        <g>
          <rect x="286" y="60" width="20" height="28" rx="4" fill="url(#el-box)" stroke="#434e57" strokeWidth="1.1" />
          <rect x="310" y="60" width="20" height="28" rx="4" fill="url(#el-box)" stroke="#434e57" strokeWidth="1.1" />
          <g stroke="#8c9aa4" strokeWidth="1.2">
            <line x1="306" y1="68" x2="310" y2="68" />
            <line x1="306" y1="74" x2="310" y2="74" />
            <line x1="306" y1="80" x2="310" y2="80" />
          </g>
        </g>

        {/* ── the load ── */}
        <g>
          <circle cx="470" cy="150" r="24" fill="url(#el-bulb)" stroke="#4a555e" strokeWidth="1.5" />
          <path d="M462 158 l3 -11 l3 7 l3 -7 l3 11" fill="none" stroke="#7b8993" strokeWidth="1.5" strokeLinejoin="round" />
          <rect x="460" y="172" width="20" height="10" rx="2" fill="#2c343a" stroke="#434e57" strokeWidth="1" />
        </g>

        {/* ── the break, drawn only once it has been located ── */}
        {found ? (
          <g>
            <rect x={breakX - 11} y={WIRE_Y - 9} width="22" height="18" fill="var(--surface)" />
            <g stroke="var(--danger)" strokeWidth="2.4" strokeLinecap="round">
              <line x1={breakX - 7} y1={WIRE_Y - 7} x2={breakX + 7} y2={WIRE_Y + 7} />
              <line x1={breakX + 7} y1={WIRE_Y - 7} x2={breakX - 7} y2={WIRE_Y + 7} />
            </g>
          </g>
        ) : null}

        {/* ── pads, their labels and their meter readings ── */}
        {points.map((point, index) => {
          const x = PAD_X[index] ?? 0;
          const done = seen(index);
          const live = volts(index) > 0;
          const colour = !done ? "#5b6a74" : live ? "var(--success)" : "var(--danger)";
          return (
            <g key={point.id}>
              <circle cx={x} cy={WIRE_Y} r="5.2" fill={done ? colour : "#1d242a"} stroke={colour} strokeWidth="1.7" />
              {done ? (
                <g>
                  <line x1={x} y1={WIRE_Y - 7} x2={x} y2="44" stroke={colour} strokeWidth="1.1" strokeDasharray="3 3" />
                  <rect x={x - 28} y="16" width="56" height="26" rx="6" fill="var(--bg)" stroke={colour} strokeWidth="1.2" />
                  <text x={x} y="33" textAnchor="middle" fontSize="12" fill={colour}>
                    {volt(volts(index))}
                  </text>
                </g>
              ) : null}
              <text x={x} y="108" textAnchor="middle" fontSize="10" fill="var(--text-muted)">
                {point.label}
              </text>
            </g>
          );
        })}
      </svg>
    </WidgetFrame>
  );
}
