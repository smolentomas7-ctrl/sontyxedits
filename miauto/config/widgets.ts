/**
 * Every number the service widgets use.
 *
 * Nothing numeric lives in a component. Figures that describe the physical world
 * are sourced and commented; figures that merely shape a drawing are marked as
 * such. Nothing here describes a specific customer's vehicle, and the widgets
 * say so beneath themselves.
 */

/* ────────────────────────────────────────────────────────────────────────────
   ECU — rolling road
   ──────────────────────────────────────────────────────────────────────────── */

/**
 * A representative 2.0 TDI, used as the baseline curve.
 *
 * Power and torque are not two independent curves: P[kW] = M[Nm] × n[rpm] / 9549.
 * Only torque is defined here, and power is derived from it, so the two lines on
 * the chart can never contradict each other.
 */
export const dyno = {
  rpmMin: 1000,
  rpmMax: 4400,
  /** Torque anchor points, in Nm, for the stock engine. */
  torqueCurve: [
    { rpm: 1000, nm: 150 },
    { rpm: 1400, nm: 250 },
    { rpm: 1750, nm: 320 },
    { rpm: 2200, nm: 320 },
    { rpm: 2500, nm: 318 },
    { rpm: 3000, nm: 305 },
    { rpm: 3500, nm: 292 },
    { rpm: 3750, nm: 280 },
    { rpm: 4100, nm: 245 },
    { rpm: 4400, nm: 205 },
  ],
  /**
   * How much of the slider's percentage reaches each part of the rev range.
   * A compression-ignition engine gains most in the mid-range and least at the
   * top, so a flat percentage across the whole curve would be a lie about how
   * these engines behave.
   */
  gainShape: [
    { rpm: 1000, w: 0.35 },
    { rpm: 1400, w: 0.72 },
    { rpm: 1750, w: 1.0 },
    { rpm: 2800, w: 1.0 },
    { rpm: 3500, w: 0.85 },
    { rpm: 4400, w: 0.55 },
  ],
  maxGainPercent: 30,
  /** 1 kW in metric horsepower. */
  kwToHp: 1.35962,
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   Wheel alignment
   ──────────────────────────────────────────────────────────────────────────── */
export const alignment = {
  /** Total toe in degrees; near zero is correct on most passenger cars. */
  toe: { min: -0.6, max: 0.6, step: 0.05, ok: 0.1 },
  /** Camber in degrees; a small negative figure is normal. */
  camber: { min: -3, max: 1.5, step: 0.1, okFrom: -1.2, okTo: 0.2 },
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   Tyres — tread depth and wet braking
   ──────────────────────────────────────────────────────────────────────────── */
export const tyres = {
  /** Tread depth in mm. 1.6 mm is the legal minimum in the EU. */
  depth: { min: 1.6, max: 8, step: 0.1, legalMin: 1.6 },
  /**
   * Wet braking distance from 80 km/h, in metres, by tread depth.
   *
   * Orientation figures only. Independent wet-braking tests (ADAC and TCS have
   * published several) repeatedly show a worn tyre needing roughly half again
   * the distance of a new one from this speed; the exact numbers depend on the
   * tyre, the surface and the water depth, which is why the widget labels them
   * as indicative and the page does not present them as measurements.
   */
  wetBraking: [
    { mm: 8, m: 38 },
    { mm: 6, m: 41 },
    { mm: 4, m: 46 },
    { mm: 3, m: 51 },
    { mm: 1.6, m: 58 },
  ],
  fromSpeed: 80,
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   Timing system
   ──────────────────────────────────────────────────────────────────────────── */
export const timing = {
  /** Mileage slider, in km. */
  km: { min: 0, max: 220_000, step: 5_000 },
  /**
   * Where the belt is treated as past its service life in this illustration.
   * Deliberately NOT presented as a universal interval: the real one is set by
   * the manufacturer for the specific engine, which is what the copy says.
   */
  illustrativeIntervalKm: 120_000,
  /**
   * Where the three described belt states begin, as a fraction of the interval
   * above. Shapes a drawing; it is not a prediction for any particular belt.
   */
  wearStages: [0.45, 0.85],
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   Air conditioning
   ──────────────────────────────────────────────────────────────────────────── */
export const aircon = {
  /** Refrigerant charge as a percentage of the correct fill. */
  charge: { min: 40, max: 100, step: 1, correctFrom: 90 },
  /**
   * Vent temperature in °C by refrigerant charge, with the cabin at `cabinTemp`.
   *
   * Orientation figures, not a measurement. The point the curve makes is that
   * the first part of a leak costs a couple of degrees and the driver does not
   * notice it, while the last part costs the cooling altogether.
   */
  ventTempCurve: [
    { pct: 40, c: 22 },
    { pct: 55, c: 18 },
    { pct: 70, c: 13 },
    { pct: 85, c: 8.5 },
    { pct: 90, c: 7 },
    { pct: 100, c: 6 },
  ],
  /** Below this charge the widget calls the state a heavy undercharge. */
  lowUntil: 65,
  cabinTemp: 30,
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   Electrics — finding a break in a circuit
   ──────────────────────────────────────────────────────────────────────────── */
export const electrics = {
  /** Nominal system voltage with the engine off, in volts. */
  systemVolts: 12.6,
  /**
   * Index of the last measuring point that still has voltage, i.e. the break
   * lies between that point and the next one. The widget walks this list on
   * every reset, so trying again gives a different circuit rather than the same
   * answer twice.
   */
  faultSequence: [1, 2, 0],
} as const;

/* ────────────────────────────────────────────────────────────────────────────
   shared helpers
   ──────────────────────────────────────────────────────────────────────────── */

/**
 * Linear interpolation across a list of anchor points.
 *
 * The list may be written in either direction — wet braking reads naturally from
 * a new tyre downwards, torque from idle upwards — so the points are put in
 * ascending order here rather than relying on every table being written the same
 * way round.
 */
export function interpolate(
  points: readonly { readonly rpm?: number; readonly mm?: number; readonly [k: string]: number | undefined }[],
  xKey: string,
  yKey: string,
  x: number,
): number {
  const ordered =
    (points[0]?.[xKey] ?? 0) > (points[points.length - 1]?.[xKey] ?? 0)
      ? [...points].reverse()
      : points;
  const xs = ordered.map((p) => p[xKey] as number);
  const ys = ordered.map((p) => p[yKey] as number);
  const first = xs[0] ?? 0;
  const lastIndex = xs.length - 1;
  if (x <= first) return ys[0] ?? 0;
  if (x >= (xs[lastIndex] ?? 0)) return ys[lastIndex] ?? 0;
  for (let i = 0; i < lastIndex; i += 1) {
    const x0 = xs[i] ?? 0;
    const x1 = xs[i + 1] ?? 0;
    if (x >= x0 && x <= x1) {
      const t = x1 === x0 ? 0 : (x - x0) / (x1 - x0);
      return (ys[i] ?? 0) + ((ys[i + 1] ?? 0) - (ys[i] ?? 0)) * t;
    }
  }
  return ys[lastIndex] ?? 0;
}

/** Torque in Nm at a given rpm, with an optional percentage gain applied. */
export function torqueAt(rpm: number, gainPercent = 0): number {
  const base = interpolate(dyno.torqueCurve, "rpm", "nm", rpm);
  if (gainPercent === 0) return base;
  const weight = interpolate(dyno.gainShape, "rpm", "w", rpm);
  return base * (1 + (gainPercent / 100) * weight);
}

/** Power in kW, always derived from torque so the two curves stay consistent. */
export function powerAt(rpm: number, gainPercent = 0): number {
  return (torqueAt(rpm, gainPercent) * rpm) / 9549;
}

export function peak(gainPercent: number): {
  powerKw: number;
  powerHp: number;
  torqueNm: number;
} {
  let powerKw = 0;
  let torqueNm = 0;
  for (let rpm = dyno.rpmMin; rpm <= dyno.rpmMax; rpm += 25) {
    powerKw = Math.max(powerKw, powerAt(rpm, gainPercent));
    torqueNm = Math.max(torqueNm, torqueAt(rpm, gainPercent));
  }
  return { powerKw, powerHp: powerKw * dyno.kwToHp, torqueNm };
}
