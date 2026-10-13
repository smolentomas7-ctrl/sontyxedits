"use client";

import clsx from "clsx";
import { RotateCcw, Zap } from "lucide-react";
import { useState } from "react";
import { timing } from "@/config/widgets";
import { usePressHandlers } from "@/lib/motion";
import { LiveReadout, Readout, WidgetFrame, WidgetSlider, fmt } from "./WidgetFrame";
import type { LocaleContent } from "@/content/types";

/**
 * Pulley geometry. The straight runs are the true external tangents of the two
 * circles, so the belt meets each pulley without a kink:
 *   cos α = (r_cam − r_crank) / d, measured from the line joining the centres.
 */
const CAM = { cx: 190, cy: 84, r: 58, teeth: 28 };
const CRANK = { cx: 190, cy: 212, r: 38, teeth: 18 };
const BELT =
  "M132.71 93.06 L152.47 217.94 A38 38 0 0 0 227.53 217.94 L247.29 93.06 A58 58 0 1 0 132.71 93.06 Z";
/** Where the belt lands once it has snapped: slack round the crank, two free ends. */
const BELT_LEFT = "M152.47 217.94 C140 196 132 176 130 152";
const BELT_RIGHT = "M227.53 217.94 C240 196 248 176 250 152";
const BELT_SLACK = "M152.47 217.94 A38 38 0 0 0 227.53 217.94";

/** Points on the two straight runs, where cracks are drawn as wear sets in. */
const CRACKS = [0.3, 0.52, 0.74].flatMap((t) => [
  { x: 132.71 + (152.47 - 132.71) * t, y: 93.06 + (217.94 - 93.06) * t, flip: false },
  { x: 247.29 + (227.53 - 247.29) * t, y: 93.06 + (217.94 - 93.06) * t, flip: true },
]);

/** Sprocket teeth, cut into the rim rather than drawn across the whole face. */
function teeth(p: typeof CAM | typeof CRANK) {
  return Array.from({ length: p.teeth }, (_, i) => {
    const a = (i / p.teeth) * Math.PI * 2;
    return {
      key: i,
      x1: p.cx + Math.cos(a) * (p.r - 6),
      y1: p.cy + Math.sin(a) * (p.r - 6),
      x2: p.cx + Math.cos(a) * (p.r + 0.5),
      y2: p.cy + Math.sin(a) * (p.r + 0.5),
    };
  });
}

/** Lightening holes in the sprocket web, so it reads as a part and not a dial. */
function holes(p: typeof CAM | typeof CRANK, count: number, r: number) {
  return Array.from({ length: count }, (_, i) => {
    const a = (i / count) * Math.PI * 2 + Math.PI / count;
    const ring = (p.r - 9) * 0.56;
    return { key: i, cx: p.cx + Math.cos(a) * ring, cy: p.cy + Math.sin(a) * ring, r };
  });
}

const CAM_TEETH = teeth(CAM);
const CRANK_TEETH = teeth(CRANK);
const CAM_HOLES = holes(CAM, 5, 7.5);
const CRANK_HOLES = holes(CRANK, 4, 5);

/**
 * Timing widget: why the belt is replaced on a schedule rather than on failure.
 *
 * Wear is a drawing — nobody can read a belt's remaining life off a mileage
 * figure, and the copy says so. What is not a drawing is the consequence, and
 * that is the whole point of the widget: the scenario button shows what a snapped
 * belt does to an interference engine, which is the reason the interval exists.
 */
export function TimingWidget({ t }: { t: LocaleContent }) {
  const w = t.widgets.timing;
  const press = usePressHandlers();

  const [km, setKm] = useState<number>(60_000);
  const [failed, setFailed] = useState(false);

  const share = km / timing.illustrativeIntervalKm;
  const [early, late] = timing.wearStages;
  const stage = share < (early ?? 0.45) ? 0 : share < (late ?? 0.85) ? 1 : 2;
  const condition = w.states[stage] ?? w.states[0];

  // Drawing figures: teeth round off and cracks show as the belt ages.
  const wear = Math.min(Math.max(share, 0), 1.6) / 1.6;
  const tooth = 4.6 - wear * 2;
  const crackOpacity = Math.max(0, (share - (early ?? 0.45)) / 0.8);

  const pistonY = failed ? 110 : 168;

  return (
    <WidgetFrame
      heading={w.heading}
      lead={w.lead}
      disclaimer={w.disclaimer}
      controls={
        <div>
          <WidgetSlider
            label={w.mileage}
            value={km}
            min={timing.km.min}
            max={timing.km.max}
            step={timing.km.step}
            display={`${fmt(km)} km`}
            onChange={(value) => {
              setKm(value);
              setFailed(false);
            }}
            marks={[
              { at: timing.km.min, label: "0" },
              { at: timing.illustrativeIntervalKm, label: `${fmt(timing.illustrativeIntervalKm)} km` },
            ]}
          />
          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => setFailed(true)}
              disabled={failed}
              className="tappable inline-flex h-11 items-center gap-2 rounded-[var(--radius-control)] bg-[var(--accent)] px-5 text-[0.9375rem] font-semibold text-[color:var(--accent-ink)] disabled:bg-[var(--surface-hover)] disabled:text-[color:var(--text-muted)]"
              {...press}
            >
              <Zap size={16} aria-hidden="true" />
              {w.run}
            </button>
            {failed ? (
              <button
                type="button"
                onClick={() => setFailed(false)}
                className="tappable inline-flex h-11 items-center gap-2 rounded-[var(--radius-control)] border border-[var(--border)] px-4 text-[0.875rem]"
                {...press}
              >
                <RotateCcw size={15} aria-hidden="true" />
                {w.reset}
              </button>
            ) : null}
          </div>
        </div>
      }
      readouts={
        <div className="grid grid-cols-2 gap-5">
          <Readout
            label={w.condition}
            value={failed ? w.failure : condition}
            tone={failed ? "danger" : stage === 2 ? "accent" : stage === 1 ? "default" : "success"}
          />
          <Readout label={w.interval} value={`${fmt(timing.illustrativeIntervalKm)} km`} />
        </div>
      }
    >
      <LiveReadout
        text={failed ? `${w.failure}. ${w.failureBody}` : `${fmt(km)} km, ${condition}`}
      />

      <svg
        viewBox="0 0 640 282"
        className="w-full"
        role="img"
        aria-label={w.sceneAlt}
        style={{ aspectRatio: "640 / 282" }}
      >
        <defs>
          <linearGradient id="tm-pulley" x1="0.15" y1="0" x2="0.75" y2="1">
            <stop offset="0%" stopColor="#56626c" />
            <stop offset="45%" stopColor="#2a333a" />
            <stop offset="100%" stopColor="#161c21" />
          </linearGradient>
          <linearGradient id="tm-belt" x1="0.1" y1="0" x2="0.8" y2="1">
            <stop offset="0%" stopColor="#2b3238" />
            <stop offset="45%" stopColor="#1b2126" />
            <stop offset="100%" stopColor="#10151a" />
          </linearGradient>
          <linearGradient id="tm-block" x1="0.1" y1="0" x2="0.7" y2="1">
            <stop offset="0%" stopColor="#2a333a" />
            <stop offset="50%" stopColor="#191f24" />
            <stop offset="100%" stopColor="#10151a" />
          </linearGradient>
          <linearGradient id="tm-bore" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#0a0e11" />
            <stop offset="30%" stopColor="#1b242b" />
            <stop offset="100%" stopColor="#0b0f13" />
          </linearGradient>
          <linearGradient id="tm-piston" x1="0" y1="0" x2="0.35" y2="1">
            <stop offset="0%" stopColor="#76848f" />
            <stop offset="50%" stopColor="#3c454d" />
            <stop offset="100%" stopColor="#222931" />
          </linearGradient>
          <radialGradient id="tm-bang">
            <stop offset="0%" stopColor="var(--danger)" stopOpacity="0.6" />
            <stop offset="100%" stopColor="var(--danger)" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* ── sprockets and belt ── */}
        <g>
          {!failed ? (
            <path d={BELT} fill="none" stroke="#080b0d" strokeOpacity="0.6" strokeWidth="15" />
          ) : null}

          <g
            className={failed ? undefined : "tm-cam"}
            style={{ transformOrigin: `${CAM.cx}px ${CAM.cy}px`, transformBox: "view-box" }}
          >
            <circle cx={CAM.cx} cy={CAM.cy} r={CAM.r} fill="url(#tm-pulley)" stroke="#4e5962" strokeWidth="1.3" />
            <g stroke="#0d1216" strokeWidth="2.8" strokeLinecap="butt">
              {CAM_TEETH.map((tk) => (
                <line key={tk.key} x1={tk.x1} y1={tk.y1} x2={tk.x2} y2={tk.y2} />
              ))}
            </g>
            <circle cx={CAM.cx} cy={CAM.cy} r={CAM.r - 7} fill="none" stroke="#39434b" strokeWidth="1.1" />
            {CAM_HOLES.map((h) => (
              <circle key={h.key} cx={h.cx} cy={h.cy} r={h.r} fill="#10161a" stroke="#39434b" strokeWidth="1" />
            ))}
            <circle cx={CAM.cx} cy={CAM.cy} r="17" fill="#1d242a" stroke="#454f58" strokeWidth="1.2" />
            <circle cx={CAM.cx} cy={CAM.cy} r="5" fill="#59646e" />
            <line x1={CAM.cx} y1={CAM.cy - 17} x2={CAM.cx} y2={CAM.cy - 30} stroke="#7b8993" strokeWidth="2.6" />
          </g>

          <g
            className="tm-crank"
            style={{ transformOrigin: `${CRANK.cx}px ${CRANK.cy}px`, transformBox: "view-box" }}
          >
            <circle cx={CRANK.cx} cy={CRANK.cy} r={CRANK.r} fill="url(#tm-pulley)" stroke="#4e5962" strokeWidth="1.3" />
            <g stroke="#0d1216" strokeWidth="2.6" strokeLinecap="butt">
              {CRANK_TEETH.map((tk) => (
                <line key={tk.key} x1={tk.x1} y1={tk.y1} x2={tk.x2} y2={tk.y2} />
              ))}
            </g>
            <circle cx={CRANK.cx} cy={CRANK.cy} r={CRANK.r - 7} fill="none" stroke="#39434b" strokeWidth="1.1" />
            {CRANK_HOLES.map((h) => (
              <circle key={h.key} cx={h.cx} cy={h.cy} r={h.r} fill="#10161a" stroke="#39434b" strokeWidth="1" />
            ))}
            <circle cx={CRANK.cx} cy={CRANK.cy} r="12" fill="#1d242a" stroke="#454f58" strokeWidth="1.2" />
            <circle cx={CRANK.cx} cy={CRANK.cy} r="4" fill="#59646e" />
          </g>

          {failed ? (
            <g fill="none" strokeLinecap="round">
              <path d={BELT_SLACK} stroke="#080b0d" strokeOpacity="0.6" strokeWidth="15" />
              <path d={BELT_SLACK} stroke="url(#tm-belt)" strokeWidth="9" />
              <path d={BELT_LEFT} stroke="url(#tm-belt)" strokeWidth="9" />
              <path d={BELT_RIGHT} stroke="url(#tm-belt)" strokeWidth="9" />
            </g>
          ) : (
            <g fill="none">
              <path d={BELT} stroke="url(#tm-belt)" strokeWidth="9" />
              <path
                className="tm-teeth"
                d={BELT}
                stroke="#0c1216"
                strokeWidth="4.6"
                strokeDasharray={`${tooth.toFixed(2)} 5.4`}
                style={{ transition: "stroke-dasharray 240ms var(--ease-ios)" }}
              />
              <path d={BELT} stroke="#9aa7b1" strokeOpacity="0.13" strokeWidth="1.1" />
              {/* cracks, as the belt ages */}
              <g stroke="var(--danger)" strokeWidth="1.6" strokeLinecap="round" opacity={Math.min(crackOpacity, 0.85)}>
                {CRACKS.map((c, i) => (
                  <line
                    key={i}
                    x1={c.x - (c.flip ? -5 : 5)}
                    y1={c.y - 3}
                    x2={c.x + (c.flip ? -5 : 5)}
                    y2={c.y + 3}
                  />
                ))}
              </g>
            </g>
          )}
        </g>

        {/* ── one cylinder, in section ── */}
        <g>
          <rect x="356" y="30" width="252" height="222" rx="10" fill="url(#tm-block)" stroke="#39434b" strokeWidth="1.2" />
          <line x1="358" y1="31.5" x2="606" y2="31.5" stroke="#6c7a85" strokeWidth="1" opacity="0.5" />
          {/* head-to-block joint and its bolts */}
          <line x1="364" y1="116" x2="440" y2="116" stroke="#434e57" strokeWidth="1.4" />
          <line x1="524" y1="116" x2="600" y2="116" stroke="#434e57" strokeWidth="1.4" />
          <g fill="#2b343b" stroke="#454f58" strokeWidth="1">
            <circle cx="386" cy="116" r="5" />
            <circle cx="578" cy="116" r="5" />
          </g>
          {/* coolant jacket, as a hatch either side of the bore */}
          <g stroke="#39434b" strokeWidth="1" opacity="0.7">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <line key={`l${i}`} x1="372" y1={142 + i * 16} x2="430" y2={142 + i * 16} />
            ))}
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <line key={`r${i}`} x1="534" y1={142 + i * 16} x2="592" y2={142 + i * 16} />
            ))}
          </g>

          {/* combustion chamber and bore */}
          <path d="M442 116 C442 84 464 68 482 68 C500 68 522 84 522 116 Z" fill="url(#tm-bore)" stroke="#404a53" strokeWidth="1.2" />
          <rect x="442" y="116" width="80" height="124" fill="url(#tm-bore)" stroke="#404a53" strokeWidth="1.2" />
          <line x1="443.5" y1="116" x2="443.5" y2="240" stroke="#5e6a74" strokeWidth="1.6" />
          <line x1="520.5" y1="116" x2="520.5" y2="240" stroke="#46525b" strokeWidth="1.6" />

          {/* valve guides */}
          <rect x="450" y="44" width="14" height="30" rx="3" fill="#232b31" stroke="#3f4952" strokeWidth="1" />
          <rect x="500" y="44" width="14" height="30" rx="3" fill="#232b31" stroke="#3f4952" strokeWidth="1" />

          {/* valves: the right one keeps its seat, the left one is in the way */}
          <g strokeLinecap="round">
            <line x1="507" y1="42" x2="507" y2="96" stroke="#7a8893" strokeWidth="4.2" />
            <path d="M494 96 L520 96 L515 104 L499 104 Z" fill="#78868f" stroke="#49545d" strokeWidth="0.9" />
            {failed ? (
              <>
                <path d="M457 42 L459 74 L447 96" fill="none" stroke="var(--danger)" strokeWidth="4.2" />
                <path d="M432 100 L458 106 L452 114 L434 108 Z" fill="var(--danger)" fillOpacity="0.9" />
              </>
            ) : (
              <>
                <line x1="457" y1="42" x2="457" y2="96" stroke="#7a8893" strokeWidth="4.2" />
                <path d="M444 96 L470 96 L465 104 L449 104 Z" fill="#78868f" stroke="#49545d" strokeWidth="0.9" />
              </>
            )}
          </g>

          {/* piston */}
          <g style={{ transition: "transform 460ms var(--ease-ios)", transform: `translateY(${pistonY - 168}px)` }}>
            <rect x="444" y="168" width="76" height="44" rx="3" fill="url(#tm-piston)" stroke="#626d77" strokeWidth="1.1" />
            <g stroke="#131a1f" strokeWidth="1.6">
              <line x1="444" y1="177" x2="520" y2="177" />
              <line x1="444" y1="184" x2="520" y2="184" />
            </g>
            <line x1="482" y1="212" x2="482" y2="248" stroke="#4d5861" strokeWidth="8" strokeLinecap="round" />
          </g>

          {failed ? (
            <g>
              <circle cx="452" cy="106" r="38" fill="url(#tm-bang)" />
              <g stroke="var(--danger)" strokeWidth="2.2" strokeLinecap="round">
                <line x1="452" y1="76" x2="452" y2="64" />
                <line x1="430" y1="86" x2="421" y2="79" />
                <line x1="474" y1="86" x2="483" y2="79" />
              </g>
            </g>
          ) : null}
        </g>

        <text x="190" y="272" textAnchor="middle" fontSize="10.5" fill="var(--text-muted)">
          {failed ? w.failure : condition}
        </text>
      </svg>

      {/* Why the interval exists, shown only once the scenario has been run. */}
      <div aria-live="polite">
        {failed ? (
          <div
            className={clsx(
              "mt-5 rounded-[var(--radius-card)] border p-4 md:p-5",
              "border-[color-mix(in_srgb,var(--danger)_45%,var(--border))] bg-[color-mix(in_srgb,var(--danger)_8%,transparent)]",
            )}
          >
            <p className="font-heading text-[1rem] font-semibold text-[color:var(--danger)]">
              {w.failure}
            </p>
            <p className="prose-width mt-2 text-[0.9375rem] text-[color:var(--text)]">
              {w.failureBody}
            </p>
          </div>
        ) : null}
      </div>

      <style>{`
        .tm-cam { animation: tm-spin 7.4s linear infinite }
        .tm-crank { animation: tm-spin 4.8s linear infinite }
        .tm-teeth { animation: tm-run 1.1s linear infinite }
        @keyframes tm-spin { to { transform: rotate(360deg) } }
        @keyframes tm-run { to { stroke-dashoffset: -12 } }
        @media (prefers-reduced-motion: reduce) {
          .tm-cam, .tm-crank, .tm-teeth { animation: none !important }
        }
      `}</style>
    </WidgetFrame>
  );
}
