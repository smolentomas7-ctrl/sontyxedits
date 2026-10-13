import styles from "./SignatureScene.module.css";
import type { LocaleContent } from "@/content/types";

/**
 * The scene, drawn in code — no photograph, no asset.
 *
 * Everything takes its state from --p and data-stage through the stylesheet;
 * nothing here holds state.
 *
 * Shading rules the whole drawing follows:
 *  - One light source, upper left. Every bezel highlight sits top-left and every
 *    contact shadow bottom-right. Nothing is lit from two directions.
 *  - Three stroke weights, used for three jobs: 0.6 for construction lines
 *    (scale ticks, panel seams), 1.2–1.5 for detail, 2.6–3 for foreground
 *    accents only. Uniform outlines are what make a drawing look traced.
 *  - No flat fill anywhere. Every surface is a base plus a gradient overlay plus
 *    a specular, so a dial housing reads as a tube and not as a circle.
 */

// Dials sit far enough apart for the odometer window to live between them
// without overlapping either bezel.
const RPM = { cx: 166, cy: 244, r: 100 };
const SPD = { cx: 450, cy: 244, r: 100 };
const RPM_LABELS = ["0", "1", "2", "3", "4", "5", "6", "7", "8"] as const;
const SPD_LABELS = ["0", "40", "80", "120", "160"] as const;

/**
 * Where a needle points, as a fraction of the dial sweep.
 *
 * The scale runs from 150° to 390°, so a needle drawn pointing up (270°) has to
 * be rotated by `240 * value - 120` to land on the right number. Reading these
 * as "about idle" or "about 2000 rpm" rather than as arbitrary angles is the
 * only way they stay plausible.
 */
const DIAL_START = 150;
const DIAL_SWEEP = 240;

/** Scale ticks for one dial: major, minor and the red sector. */
function Dial({
  cx,
  cy,
  r,
  majors,
  labels,
  redFrom,
  label,
}: {
  cx: number;
  cy: number;
  r: number;
  majors: number;
  labels: readonly string[];
  redFrom: number;
  label: string;
}) {
  const START = 150; // degrees, sweeping clockwise through the bottom
  const SWEEP = 240;
  const ticks = [];
  const total = majors * 2;

  for (let i = 0; i <= total; i += 1) {
    const isMajor = i % 2 === 0;
    const a = ((START + (SWEEP * i) / total) * Math.PI) / 180;
    const outer = r - 14;
    const inner = outer - (isMajor ? 15 : 8);
    const red = i / total >= redFrom;
    ticks.push(
      <line
        key={`t${i}`}
        x1={cx + Math.cos(a) * inner}
        y1={cy + Math.sin(a) * inner}
        x2={cx + Math.cos(a) * outer}
        y2={cy + Math.sin(a) * outer}
        stroke={red ? "var(--danger)" : "var(--text)"}
        strokeOpacity={red ? 0.95 : isMajor ? 0.82 : 0.4}
        strokeWidth={isMajor ? 2.4 : 1}
        strokeLinecap="butt"
      />,
    );
  }

  const last = Math.max(labels.length - 1, 1);
  const numerals = labels.map((text, i) => {
    const a = ((START + (SWEEP * i) / last) * Math.PI) / 180;
    const rr = r - 38;
    return (
      <text
        key={`n${i}`}
        x={cx + Math.cos(a) * rr}
        y={cy + Math.sin(a) * rr + 6}
        textAnchor="middle"
        fontSize={labels.length > 6 ? 14 : 15}
        fontWeight="600"
        fill="var(--text)"
        fillOpacity={i / last >= redFrom ? 0.95 : 0.72}
        fontFamily="var(--font-heading)"
      >
        {text}
      </text>
    );
  });

  // Red sector on the rim. A dial without one — the speedometer — passes
  // redFrom >= 1 and gets no arc at all rather than a wrapped-around sliver.
  const hasRed = redFrom < 1;
  const a0 = ((START + SWEEP * redFrom) * Math.PI) / 180;
  const a1 = ((START + SWEEP) * Math.PI) / 180;
  const rr = r - 7;
  const redArc = hasRed
    ? `M ${cx + Math.cos(a0) * rr} ${cy + Math.sin(a0) * rr} A ${rr} ${rr} 0 0 1 ${
        cx + Math.cos(a1) * rr
      } ${cy + Math.sin(a1) * rr}`
    : "";

  return (
    <g>
      {/* housing: outer tube, inner face, rim highlight, contact shadow */}
      <circle cx={cx} cy={cy + 3} r={r + 3} fill="url(#mi-dial-shadow)" />
      <circle cx={cx} cy={cy} r={r} fill="url(#mi-dial-tube)" />
      <circle cx={cx} cy={cy} r={r - 7} fill="url(#mi-dial-face)" />
      <circle
        cx={cx}
        cy={cy}
        r={r - 7}
        fill="none"
        stroke="url(#mi-dial-rim)"
        strokeWidth="1.4"
      />
      {hasRed ? (
        <path d={redArc} fill="none" stroke="var(--danger)" strokeWidth="4" strokeOpacity="0.85" />
      ) : null}

      {ticks}
      {numerals}

      <text
        x={cx}
        y={cy + r - 46}
        textAnchor="middle"
        fontSize="12"
        letterSpacing="2"
        fill="var(--text-muted)"
        fontFamily="var(--font-body)"
      >
        {label}
      </text>

      {/* glass: one quiet diagonal band, low opacity */}
      <path
        d={`M ${cx - r + 10} ${cy + 26} A ${r} ${r} 0 0 1 ${cx + 10} ${cy - r + 12} L ${
          cx - 34
        } ${cy - r + 20} A ${r} ${r} 0 0 0 ${cx - r + 16} ${cy + 44} Z`}
        fill="url(#mi-glass)"
      />
    </g>
  );
}

function Needle({
  cx,
  cy,
  r,
  className,
}: {
  cx: number;
  cy: number;
  r: number;
  // CSS-module lookups are typed as possibly undefined under noUncheckedIndexedAccess.
  className: string | undefined;
}) {
  return (
    <g
      className={`${styles.needle} ${className}`}
      style={{ transformBox: "view-box", transformOrigin: `${cx}px ${cy}px` }}
    >
      {/* counterweight behind the hub, thin taper in front */}
      <path
        d={`M ${cx - 4.2} ${cy + 18} L ${cx - 1.3} ${cy - r + 30} L ${cx + 1.3} ${cy - r + 30} L ${
          cx + 4.2
        } ${cy + 18} Z`}
        fill="url(#mi-needle)"
      />
      <circle cx={cx} cy={cy} r="13" fill="url(#mi-hub)" />
      <circle cx={cx} cy={cy} r="13" fill="none" stroke="var(--border)" strokeWidth="0.8" />
      <circle cx={cx - 3.5} cy={cy - 4.5} r="4" fill="#ffffff" fillOpacity="0.1" />
    </g>
  );
}

export function SignatureSvg({ t }: { t: LocaleContent }) {
  const codes = t.signature.codes;

  return (
    <svg
      className={styles.svg}
      viewBox="0 0 960 540"
      role="img"
      preserveAspectRatio="xMidYMid meet"
    >
      <title>{t.signature.svgTitle}</title>

      <defs>
        {/* ---- material gradients, all lit from the upper left ---- */}
        <linearGradient id="mi-dial-tube" x1="0.18" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#3a4246" />
          <stop offset="38%" stopColor="#222a2e" />
          <stop offset="100%" stopColor="#11161a" />
        </linearGradient>
        <radialGradient id="mi-dial-face" cx="0.3" cy="0.22" r="0.95">
          <stop offset="0%" stopColor="#1d2429" />
          <stop offset="62%" stopColor="#12171b" />
          <stop offset="100%" stopColor="#0a0e11" />
        </radialGradient>
        <linearGradient id="mi-dial-rim" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.22" />
          <stop offset="45%" stopColor="#ffffff" stopOpacity="0.04" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.5" />
        </linearGradient>
        <radialGradient id="mi-dial-shadow" cx="0.5" cy="0.6" r="0.5">
          <stop offset="70%" stopColor="#000000" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="mi-glass" x1="0" y1="0" x2="0.6" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.1" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
        <linearGradient id="mi-needle" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#8d9398" />
          <stop offset="45%" stopColor="#eef1f3" />
          <stop offset="100%" stopColor="#70777c" />
        </linearGradient>
        <radialGradient id="mi-hub" cx="0.34" cy="0.28" r="0.8">
          <stop offset="0%" stopColor="#4a5257" />
          <stop offset="100%" stopColor="#171c20" />
        </radialGradient>

        <linearGradient id="mi-panel" x1="0.1" y1="0" x2="0.7" y2="1">
          <stop offset="0%" stopColor="#222a2f" />
          <stop offset="55%" stopColor="#161c21" />
          <stop offset="100%" stopColor="#0d1114" />
        </linearGradient>
        <linearGradient id="mi-panel-edge" x1="0" y1="0" x2="0.4" y2="1">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.16" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>

        <linearGradient id="mi-tool" x1="0.15" y1="0" x2="0.85" y2="1">
          <stop offset="0%" stopColor="#2b3338" />
          <stop offset="50%" stopColor="#1a2024" />
          <stop offset="100%" stopColor="#0e1215" />
        </linearGradient>
        <linearGradient id="mi-display" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor="#0d1518" />
          <stop offset="100%" stopColor="#060a0c" />
        </linearGradient>
        <linearGradient id="mi-cable" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#2a3136" />
          <stop offset="50%" stopColor="#384046" />
          <stop offset="100%" stopColor="#242a2e" />
        </linearGradient>

        {/* ---- light ---- */}
        <radialGradient id="mi-bloom-inner">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.95" />
          <stop offset="45%" stopColor="var(--accent)" stopOpacity="0.35" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="mi-bloom-outer">
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.3" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="mi-bloom-green">
          <stop offset="0%" stopColor="var(--success)" stopOpacity="0.45" />
          <stop offset="100%" stopColor="var(--success)" stopOpacity="0" />
        </radialGradient>
        <filter id="mi-soft" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="6" />
        </filter>

        {/* ---- depth: vignette and a static film grain ---- */}
        <radialGradient id="mi-vignette" cx="0.5" cy="0.45" r="0.78">
          <stop offset="55%" stopColor="#000000" stopOpacity="0" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.55" />
        </radialGradient>
        {/* Static on purpose: an animated turbulence would repaint every frame. */}
        <filter id="mi-grain" x="0" y="0" width="100%" height="100%">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>

        <clipPath id="mi-display-clip">
          <rect x="646" y="192" width="274" height="194" rx="8" />
        </clipPath>
      </defs>

      {/* ══════════════ instrument cluster ══════════════ */}
      <g>
        {/* binnacle: body, top edge catching the light, seam below */}
        <rect x="40" y="110" width="556" height="304" rx="28" fill="url(#mi-panel)" />
        <rect
          x="40"
          y="110"
          width="556"
          height="304"
          rx="28"
          fill="none"
          stroke="url(#mi-panel-edge)"
          strokeWidth="1.5"
        />
        <path
          d="M62 410 H574"
          stroke="#000000"
          strokeOpacity="0.5"
          strokeWidth="0.6"
        />

        <Dial
          cx={RPM.cx}
          cy={RPM.cy}
          r={RPM.r}
          majors={8}
          labels={RPM_LABELS}
          redFrom={0.75}
          label={t.signature.dialRpm}
        />
        <Dial
          cx={SPD.cx}
          cy={SPD.cy}
          r={SPD.r}
          majors={8}
          labels={SPD_LABELS}
          redFrom={1.1}
          label={t.signature.dialSpeed}
        />

        {/* digital window between the dials */}
        <rect x="276" y="224" width="64" height="38" rx="6" fill="url(#mi-display)" />
        <rect
          x="276"
          y="224"
          width="64"
          height="38"
          rx="6"
          fill="none"
          stroke="#000000"
          strokeOpacity="0.6"
          strokeWidth="1.2"
        />
        <text
          x="308"
          y="249"
          textAnchor="middle"
          fontSize="14"
          fontFamily="ui-monospace, monospace"
          fill="var(--text-muted)"
          fillOpacity="0.85"
          letterSpacing="0.5"
        >
          {t.signature.odo}
        </text>

        <Needle cx={RPM.cx} cy={RPM.cy} r={RPM.r} className={styles.needleRpm} />
        <Needle cx={SPD.cx} cy={SPD.cy} r={SPD.r} className={styles.needleSpeed} />

        {/* ---- warning lamps ---- */}
        <g>
          {/* multi-layer bloom: wide falloff, tight core, then the glyph */}
          <circle className={styles.warnBloom} cx={308} cy={378} r="62" fill="url(#mi-bloom-outer)" />
          <circle className={styles.warnBloom} cx={308} cy={378} r="32" fill="url(#mi-bloom-inner)" />
          <g transform="translate(288 364)">
            <path
              className={styles.warnLit}
              d="M3 12 h6 V6 h11 v6 h8 l6-6 v6 h5 v11 h-5 v6 h-8 v4 H9 v-4 H3 z"
              fill="var(--accent)"
            />
            <path
              className={styles.warnLit}
              d="M3 12 h6 V6 h11 v6 h8 l6-6 v6 h5 v11 h-5 v6 h-8 v4 H9 v-4 H3 z"
              fill="#fff"
              fillOpacity="0.28"
              filter="url(#mi-soft)"
            />
            <path
              className={styles.warnOff}
              d="M3 12 h6 V6 h11 v6 h8 l6-6 v6 h5 v11 h-5 v6 h-8 v4 H9 v-4 H3 z"
              fill="none"
              stroke="var(--text-muted)"
              strokeOpacity="0.32"
              strokeWidth="1.4"
            />
          </g>

          {/* secondary telltales */}
          {[
            { x: 196, d: "M0 7 a7 7 0 1 1 14 0 a7 7 0 1 1 -14 0 M3 7 h8" },
            { x: 404, d: "M0 10 l7-10 l7 10 z M6 4 h2 v4 h-2 z" },
          ].map((item) => (
            <g key={item.x} transform={`translate(${item.x} 372)`}>
              <circle className={styles.telltaleLit} cx="7" cy="7" r="22" fill="url(#mi-bloom-outer)" />
              <path className={styles.telltaleLit} d={item.d} fill="var(--accent)" fillOpacity="0.9" />
              <path
                className={styles.telltaleOff}
                d={item.d}
                fill="none"
                stroke="var(--text-muted)"
                strokeOpacity="0.28"
                strokeWidth="1.2"
              />
            </g>
          ))}

          {/* cleared: drawn as a stroke, with its own soft halo */}
          <circle className={styles.clearedGlow} cx={308} cy={378} r="40" fill="url(#mi-bloom-green)" />
          <path
            className={styles.cleared}
            d="M292 378 l11 11 l22 -25"
            pathLength="1"
            fill="none"
            stroke="var(--success)"
            strokeWidth="5.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>

        {/* OBD port under the binnacle */}
        <g>
          <rect x="96" y="430" width="62" height="24" rx="5" fill="url(#mi-tool)" />
          <rect
            x="96"
            y="430"
            width="62"
            height="24"
            rx="5"
            fill="none"
            stroke="#ffffff"
            strokeOpacity="0.1"
            strokeWidth="0.8"
          />
          <rect className={styles.portGlow} x="103" y="436" width="48" height="12" rx="3" fill="var(--accent)" fillOpacity="0.75" />
        </g>
      </g>

      {/* ══════════════ cable: a filled path with a real taper and sag ══════════════ */}
      <g>
        <path
          className={styles.cable}
          d="M158 442 C 236 442, 266 486, 356 486 C 478 486, 540 352, 644 336"
          pathLength="1"
          fill="none"
          stroke="url(#mi-cable)"
          strokeWidth="9"
          strokeLinecap="round"
        />
        <path
          className={styles.cable}
          d="M158 439 C 236 439, 266 482, 356 482 C 478 482, 540 348, 644 332"
          pathLength="1"
          fill="none"
          stroke="#ffffff"
          strokeOpacity="0.12"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          className={styles.dataFlow}
          d="M158 442 C 236 442, 266 486, 356 486 C 478 486, 540 352, 644 336"
          pathLength="1"
          fill="none"
          stroke="var(--accent)"
          strokeWidth="3.4"
          strokeLinecap="round"
        />
      </g>

      {/* ══════════════ diagnostic tool ══════════════ */}
      <g>
        <g className={styles.tool}>
          <rect x="632" y="146" width="302" height="290" rx="22" fill="url(#mi-tool)" />
          <rect
            x="592"
            y="150"
            width="328"
            height="286"
            rx="22"
            fill="none"
            stroke="url(#mi-panel-edge)"
            strokeWidth="1.5"
          />
          <rect x="644" y="158" width="278" height="10" rx="5" fill="#ffffff" fillOpacity="0.05" />

          {/* display */}
          <rect x="646" y="192" width="274" height="194" rx="8" fill="url(#mi-display)" />
          <rect
            x="646"
            y="192"
            width="274"
            height="194"
            rx="8"
            fill="none"
            stroke="#000"
            strokeOpacity="0.7"
            strokeWidth="1.4"
          />

          <g className={styles.toolScreen} clipPath="url(#mi-display-clip)">
            <g className={styles.codeListOut}>
              <text
                x="660"
                y="216"
                fontSize="10.5"
                letterSpacing="1.4"
                fill="var(--text-muted)"
                fontFamily="ui-monospace, monospace"
              >
                {t.signature.displayTitle}
              </text>
              <line x1="660" y1="226" x2="906" y2="226" stroke="var(--border)" strokeWidth="0.6" />
              <g className={styles.codeList}>
                {codes.map((code, i) => {
                  const y = 256 + i * 36;
                  const cls = [styles.codeRow1, styles.codeRow2, styles.codeRow3][i];
                  const first = i === 0;
                  return (
                    <g key={code.id} className={cls}>
                      <text
                        x="660"
                        y={y}
                        fontSize="14"
                        fontFamily="ui-monospace, monospace"
                        fill={first ? "var(--accent)" : "var(--text)"}
                        fillOpacity={first ? 1 : 0.78}
                      >
                        {code.id}
                      </text>
                      <text
                        x="724"
                        y={y}
                        fontSize="11"
                        fontFamily="ui-monospace, monospace"
                        fill="var(--text-muted)"
                      >
                        {code.label}
                      </text>
                    </g>
                  );
                })}
              </g>
            </g>

            {/* scanline, very low intensity */}
            <rect className={styles.scanline} x="646" y="232" width="274" height="2" fill="var(--accent)" fillOpacity="0.35" />
          </g>

          {/* buttons and status LED give the body edges and controls */}
          <g>
            <rect x="660" y="402" width="60" height="22" rx="7" fill="#20272b" />
            <rect x="660" y="402" width="60" height="22" rx="7" fill="none" stroke="#ffffff" strokeOpacity="0.09" strokeWidth="0.8" />
            <rect x="732" y="402" width="60" height="22" rx="7" fill="#20272b" />
            <rect x="732" y="402" width="60" height="22" rx="7" fill="none" stroke="#ffffff" strokeOpacity="0.09" strokeWidth="0.8" />
            <circle className={styles.toolLed} cx="900" cy="413" r="6" fill="var(--success)" />
            <circle className={styles.toolLed} cx="900" cy="413" r="13" fill="url(#mi-bloom-green)" />
          </g>
        </g>
      </g>

      {/* ══════════════ stage 4: the isolated circuit and the probe ══════════════ */}
      <g className={styles.circuit}>
        <text
          x="660"
          y="216"
          fontSize="10.5"
          letterSpacing="1.4"
          fill="var(--text-muted)"
          fontFamily="ui-monospace, monospace"
        >
          {t.signature.circuitTitle}
        </text>
        <line x1="660" y1="226" x2="906" y2="226" stroke="var(--border)" strokeWidth="0.6" />

        {/* supply → fuse → connector → component → ground */}
        <path
          d="M678 300 H726 M762 300 H800 M838 300 H876"
          stroke="var(--text-muted)"
          strokeOpacity="0.55"
          strokeWidth="1.4"
        />
        <circle cx="668" cy="300" r="9" fill="none" stroke="var(--text-muted)" strokeOpacity="0.6" strokeWidth="1.4" />
        <path d="M664 300 h8 M668 296 v8" stroke="var(--text-muted)" strokeOpacity="0.6" strokeWidth="1.2" />
        <rect x="726" y="288" width="36" height="24" rx="4" fill="#1b2226" stroke="var(--border)" strokeWidth="1.2" />
        <rect x="800" y="288" width="38" height="24" rx="4" fill="#1b2226" stroke="var(--border)" strokeWidth="1.2" />
        <path d="M876 292 v16 M882 295 v10 M888 298 v4" stroke="var(--text-muted)" strokeOpacity="0.6" strokeWidth="1.4" />

        {t.signature.circuitPoints.map((point, i) => (
          <text
            key={point}
            x={[668, 744, 819, 882][i]}
            y="336"
            textAnchor="middle"
            fontSize="9.5"
            fill="var(--text-muted)"
            fillOpacity="0.8"
            fontFamily="ui-monospace, monospace"
          >
            {point}
          </text>
        ))}

        {/* the open circuit, then the same run repaired */}
        <g className={styles.circuitFaultDim}>
          <circle cx="781" cy="300" r="26" fill="url(#mi-bloom-outer)" />
          <path d="M770 292 l22 16 M770 308 l22 -16" stroke="var(--danger)" strokeWidth="2.4" strokeLinecap="round" />
        </g>
        <g className={styles.circuitFaultFixed}>
          <circle cx="781" cy="300" r="22" fill="url(#mi-bloom-green)" />
          <path d="M762 300 H800" stroke="var(--success)" strokeWidth="2.6" />
        </g>

        {/* probe tip resting on the faulty section */}
        <g className={styles.probe}>
          <path d="M788 282 l44 -36 l11 12 l-44 36 z" fill="url(#mi-needle)" />
          <path d="M832 246 l11 12 l16 -13 l-10 -11 z" fill="#2b3338" />
        </g>
      </g>

      {/* ══════════════ depth over everything ══════════════ */}
      <rect className={styles.vignette} x="0" y="0" width="960" height="540" fill="url(#mi-vignette)" />
      <rect className={styles.grain} x="0" y="0" width="960" height="540" filter="url(#mi-grain)" />
    </svg>
  );
}
