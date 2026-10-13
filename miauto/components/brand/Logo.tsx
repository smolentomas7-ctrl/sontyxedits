import clsx from "clsx";
import { site } from "@/config/miauto";

/**
 * The M.I.Auto mark.
 *
 * Direction: the letter M drawn as a single signal trace. Segments run
 * vertically and at 45°, the way a track is routed on a circuit board, and the
 * run ends in two pads. It reads as diagnostics and electronics rather than as
 * a picture of a car, which is what the rest of the site is about.
 *
 * Geometry notes:
 *  - 32×32 box, 3.6 stroke, miter joins and butt caps — nothing is rounded off,
 *    so the mark stays crisp rather than soft at small sizes.
 *  - The trace is drawn in `currentColor`, so one component serves the
 *    full-colour, light-on-dark and dark-on-light variants with no duplication.
 *  - The two pads carry the accent; set `monochrome` and they inherit the text
 *    colour instead, for a single-colour print or a favicon mask.
 */
export function LogoMark({
  className,
  monochrome = false,
  title,
}: {
  className?: string;
  monochrome?: boolean;
  title?: string;
}) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      fill="none"
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : "true"}
      focusable="false"
    >
      {title ? <title>{title}</title> : null}
      {/* The M, routed like a track: vertical runs, 45° corners, no curves. */}
      <path
        d="M6.6 26V12.4L10.8 8.2L16 13.4L21.2 8.2L25.4 12.4V26"
        stroke="currentColor"
        strokeWidth="3.6"
        strokeLinecap="butt"
        strokeLinejoin="miter"
      />
      {/* Pads where the run terminates. */}
      <circle cx="6.6" cy="27.4" r="2.6" fill={monochrome ? "currentColor" : "var(--accent)"} />
      <circle cx="25.4" cy="27.4" r="2.6" fill={monochrome ? "currentColor" : "var(--accent)"} />
    </svg>
  );
}

/**
 * The wordmark, set in the heading face. "Auto" carries the accent, which is the
 * one place the brand colour appears in the header.
 */
export function LogoWordmark({ className }: { className?: string }) {
  return (
    <span
      className={clsx(
        "font-heading leading-none tracking-[-0.03em] whitespace-nowrap",
        className,
      )}
      style={{ fontWeight: 700 }}
    >
      M.I.<span className="text-[color:var(--accent)]">Auto</span>
      <span className="ml-1 align-baseline text-[0.62em] font-medium tracking-normal text-[color:var(--text-muted)]">
        s.r.o.
      </span>
    </span>
  );
}

/**
 * Horizontal lockup for the header. The mark is optically a touch larger than
 * the cap height of the wordmark and sits on the same baseline, so the pair
 * reads as one object rather than an icon placed next to some text.
 *
 * The accessible name is always the full legal name, whatever the lockup is
 * showing visually.
 */
export function Logo({
  className,
  markClassName,
  wordmarkClassName,
}: {
  className?: string;
  markClassName?: string;
  wordmarkClassName?: string;
}) {
  return (
    <span className={clsx("inline-flex items-center gap-2.5", className)}>
      <LogoMark className={clsx("size-7 shrink-0 text-[color:var(--text)]", markClassName)} />
      <LogoWordmark
        className={clsx("text-[1.0625rem] md:text-[1.1875rem]", wordmarkClassName)}
      />
      <span className="sr-only">{site.legalName}</span>
    </span>
  );
}
