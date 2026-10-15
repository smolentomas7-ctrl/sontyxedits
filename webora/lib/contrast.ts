/**
 * Contrast helpers.
 *
 * The demos each carry their own brand colour, and a brand colour alone does
 * not tell you what text can sit on it: #F5C518 and #C4653A both read as
 * "accent", but one needs black text on it and the other white. Picking the
 * text colour by hand per demo is where contrast bugs come from, so it is
 * computed here instead.
 */

type Rgb = [number, number, number];

function parse(color: string): Rgb | null {
  const hex = color.trim().replace("#", "");
  if (/^[0-9a-fA-F]{6}$/.test(hex)) {
    return [
      parseInt(hex.slice(0, 2), 16),
      parseInt(hex.slice(2, 4), 16),
      parseInt(hex.slice(4, 6), 16),
    ];
  }
  if (/^[0-9a-fA-F]{3}$/.test(hex)) {
    return [
      parseInt(hex[0] + hex[0], 16),
      parseInt(hex[1] + hex[1], 16),
      parseInt(hex[2] + hex[2], 16),
    ];
  }
  const rgb = color.match(/-?\d+(\.\d+)?/g);
  if (rgb && rgb.length >= 3) {
    return [Number(rgb[0]), Number(rgb[1]), Number(rgb[2])];
  }
  return null;
}

/** WCAG relative luminance. */
function luminance([r, g, b]: Rgb): number {
  const channel = (value: number) => {
    const s = value / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

/** WCAG contrast ratio, 1 to 21. Symmetric in its arguments. */
export function contrastRatio(a: string, b: string): number {
  const ca = parse(a);
  const cb = parse(b);
  if (!ca || !cb) return 1;
  const la = luminance(ca);
  const lb = luminance(cb);
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

/**
 * The readable text colour for a given background: whichever of the two
 * extremes contrasts more. Not pure #000/#fff — those look harsh next to a
 * saturated brand colour, and the softer pair still clears 4.5:1 on anything
 * a demo uses as an accent.
 */
export function onColor(background: string, dark = "#17171A", light = "#FFFFFF"): string {
  return contrastRatio(background, dark) >= contrastRatio(background, light) ? dark : light;
}

/**
 * Moves a colour toward black (negative amount) or white (positive), keeping
 * hue. Used for hover states on a brand colour that arrives as a prop: the
 * alternative, fading the whole control with `opacity`, drags the label toward
 * the page background and quietly breaks the contrast the resting state had.
 */
export function shade(color: string, amount: number): string {
  const rgb = parse(color);
  if (!rgb) return color;
  const target = amount < 0 ? 0 : 255;
  const t = Math.min(1, Math.abs(amount));
  const mixed = rgb.map((v) => Math.round(v + (target - v) * t)) as Rgb;
  return `#${mixed.map((v) => v.toString(16).padStart(2, "0")).join("")}`;
}
