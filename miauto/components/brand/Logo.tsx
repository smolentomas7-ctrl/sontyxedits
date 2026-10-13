import clsx from "clsx";
import { site } from "@/config/miauto";

/**
 * The M.I.Auto mark, as the owners supplied it.
 *
 * A thin ring holding an "Mi" monogram with a car profile drawn over it. The
 * artwork arrived as a raster file; these are its outlines traced to vector, so
 * the mark stays crisp at any size, takes the surrounding text colour, and costs
 * two paths instead of an image request.
 *
 * Both paths are drawn in `currentColor`, so one component serves the orange
 * header lockup, a dark-on-light print and the knocked-out favicon with no
 * duplication. 64x64 box, mark cropped to its own bounds with one unit of
 * padding, so `size-*` behaves predictably.
 *
 * The ring is kept separate from the monogram because the favicon drops it: at
 * 16px a hairline ring disappears, and a filled disc with the monogram cut out
 * of it is the same mark in a form that still reads.
 */
export const MARK_RING =
  "M3.12 42.29L2.39 41.16L1.33 36.78L0.93 30.27L1.46 26.16L3.32 20.18L7.04 13.81L10.82 9.76L14.81 6.71L20.38 3.92L26.09 2.33L33.39 1.93L38.44 2.59L44.68 4.72L49.46 7.51L54.3 11.82L57.22 15.54L60.41 21.78L60.08 22.11L59.48 21.64L57.49 17.4L54.17 12.75L50.12 8.97L44.55 5.51L40.16 3.79L33.13 2.59L27.42 2.86L22.11 4.05L16.27 6.71L11.49 10.16L7.44 14.61L4.92 18.59L2.53 24.83L1.73 30.01L1.86 35.45L3.46 41.69L3.12 42.29ZM32.07 62.07L26.49 61.67L22.11 60.61L16.4 58.09L12.82 55.7L8.77 51.91L4.39 45.67L5.45 45.81L8.9 50.99L12.68 54.64L16.27 57.16L21.58 59.68L26.76 61.01L33.0 61.41L37.24 60.88L42.55 59.28L47.47 56.76L51.18 53.97L55.1 49.92L57.62 46.21L59.48 42.22L61.07 36.38L61.47 31.07L60.81 26.03L61.41 26.09L62.14 31.87L61.47 38.37L59.22 44.75L56.03 49.92L50.92 55.17L46.01 58.49L40.16 60.88L32.07 62.07Z";
export const MARK_GLYPH =
  "M9.23 40.83L13.94 36.91L17.26 27.35L17.13 25.23L23.3 25.56L24.03 26.29L25.49 30.81L22.11 33.66L21.25 31.47L20.65 31.27L18.79 36.05L14.54 38.7L9.23 40.83ZM26.62 41.36L24.5 41.36L24.17 40.9L23.37 37.97L24.9 36.58L26.89 34.99L27.55 36.05L27.95 35.92L32.46 31.27L36.85 28.48L43.95 26.29L42.42 28.61L36.71 31.67L27.82 40.96L26.62 41.36ZM63.0 25.03L56.76 24.1L54.77 22.77L51.45 21.84L36.98 21.84L41.76 21.31L41.96 20.85L38.57 19.06L35.78 18.39L29.01 18.66L22.37 20.78L22.51 21.58L28.75 24.5L20.52 22.64L17.46 22.77L14.28 24.5L14.21 23.1L13.01 21.25L17.06 21.18L28.75 17.6L34.46 17.33L39.37 18.52L44.81 21.05L50.12 20.91L55.03 21.71L63.0 25.03ZM45.74 43.09L41.29 42.89L45.14 30.27L45.61 29.54L50.12 29.68L45.74 43.09ZM3.66 44.28L2.19 44.15L10.43 42.16L16.13 39.63L19.59 37.51L30.74 28.75L37.64 25.83L41.43 25.36L36.18 27.15L29.54 31.0L18.13 40.03L16.93 43.09L12.68 42.95L3.66 44.28ZM37.91 43.09L33.19 43.02L34.52 38.37L36.25 34.12L38.84 31.93L42.02 30.21L37.91 43.09ZM50.65 28.08L45.94 27.75L46.74 26.03L47.73 25.3L51.45 25.16L50.65 28.08ZM33.93 23.84L28.75 23.04L25.76 21.78L27.29 21.58L33.93 23.84ZM51.32 23.17L48.06 23.1L50.12 22.77L51.32 23.17Z";

export function LogoMark({
  className,
  title,
  /** Drops the ring, for sizes where a hairline cannot survive. */
  glyphOnly = false,
}: {
  className?: string;
  title?: string;
  glyphOnly?: boolean;
}) {
  return (
    <svg
      viewBox="0 0 64 64"
      className={className}
      fill="currentColor"
      role={title ? "img" : undefined}
      aria-hidden={title ? undefined : "true"}
      focusable="false"
    >
      {title ? <title>{title}</title> : null}
      {glyphOnly ? null : <path d={MARK_RING} />}
      <path d={MARK_GLYPH} />
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
 * Horizontal lockup for the header. An emblem inside a ring reads smaller than
 * its box, so the mark is set taller than the wordmark's cap height rather than
 * matched to it, and carries the brand colour the way the supplied artwork does.
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
      <LogoMark className={clsx("size-9 shrink-0 text-[color:var(--accent)]", markClassName)} />
      <LogoWordmark
        className={clsx("text-[1.0625rem] md:text-[1.1875rem]", wordmarkClassName)}
      />
      <span className="sr-only">{site.legalName}</span>
    </span>
  );
}
