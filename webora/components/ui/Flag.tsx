import type { CountryCode } from "@/content/reviews";
import { cn } from "@/lib/utils";

/**
 * Small inline flags.
 *
 * Drawn as SVG rather than emoji: Windows has no flag emoji and renders
 * "🇸🇰" as the letters "SK", which would look broken next to a name. Shapes are
 * simplified for a 20x14 slot; the country name is always printed beside the
 * flag, so the flag itself is decorative and hidden from assistive tech.
 */
export function Flag({ country, className }: { country: CountryCode; className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "inline-block h-[14px] w-5 shrink-0 overflow-hidden rounded-[3px] ring-1 ring-white/15",
        className,
      )}
    >
      {FLAGS[country]}
    </span>
  );
}

const svgProps = {
  width: "100%",
  height: "100%",
  preserveAspectRatio: "xMidYMid slice",
  focusable: "false" as const,
};

const FLAGS: Record<CountryCode, React.ReactNode> = {
  SK: (
    <svg viewBox="0 0 9 6" {...svgProps}>
      <rect width="9" height="6" fill="#fff" />
      <rect y="2" width="9" height="4" fill="#0b4ea2" />
      <rect y="4" width="9" height="2" fill="#ee1c25" />
      <path
        d="M1.95 1.2h2.3v2c0 .95-.6 1.5-1.15 1.85C2.55 4.7 1.95 4.15 1.95 3.2z"
        fill="#ee1c25"
        stroke="#fff"
        strokeWidth=".2"
      />
      <path d="M3.1 1.55v2.4M2.6 2.05h1M2.45 2.6h1.3" stroke="#fff" strokeWidth=".24" />
      <path
        d="M2.1 3.75c.25-.25.55-.25.75 0 .2-.3.5-.3.7 0 .2-.2.4-.2.55 0-.2.55-.55.9-1 1.15-.45-.25-.8-.6-1-1.15z"
        fill="#0b4ea2"
      />
    </svg>
  ),
  CZ: (
    <svg viewBox="0 0 9 6" {...svgProps}>
      <rect width="9" height="6" fill="#d7141a" />
      <rect width="9" height="3" fill="#fff" />
      <path d="M0 0 4.5 3 0 6z" fill="#11457e" />
    </svg>
  ),
  GB: (
    <svg viewBox="0 0 60 30" {...svgProps}>
      <clipPath id="flag-gb-diagonals">
        <path d="M30 15h30v15zv15H0zH0V0zV0h30z" />
      </clipPath>
      <path d="M0 0v30h60V0z" fill="#012169" />
      <path d="M0 0l60 30m0-30L0 30" stroke="#fff" strokeWidth="6" />
      <path
        d="M0 0l60 30m0-30L0 30"
        clipPath="url(#flag-gb-diagonals)"
        stroke="#c8102e"
        strokeWidth="4"
      />
      <path d="M30 0v30M0 15h60" stroke="#fff" strokeWidth="10" />
      <path d="M30 0v30M0 15h60" stroke="#c8102e" strokeWidth="6" />
    </svg>
  ),
  US: (
    <svg viewBox="0 0 19 10" {...svgProps}>
      <rect width="19" height="10" fill="#b22234" />
      {[1, 3, 5, 7, 9, 11].map((row) => (
        <rect key={row} y={(row * 10) / 13} width="19" height={10 / 13} fill="#fff" />
      ))}
      <rect width="7.6" height={70 / 13} fill="#3c3b6e" />
      {[0, 1, 2, 3].flatMap((r) =>
        [0, 1, 2, 3, 4].map((c) => (
          <circle key={`${r}-${c}`} cx={0.85 + c * 1.48} cy={0.75 + r * 1.3} r=".28" fill="#fff" />
        )),
      )}
    </svg>
  ),
};
