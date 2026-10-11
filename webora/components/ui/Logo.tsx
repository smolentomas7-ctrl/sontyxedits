import Image from "next/image";
import { brand } from "@/config/images";
import { cn } from "@/lib/utils";

/**
 * The supplied logo is a raster file, so it is used via next/image rather than
 * inlined as SVG. Two variants exist:
 *   - "light": navy wordmark recolored to near-white, for dark backgrounds
 *   - "dark":  the original navy wordmark, for light backgrounds
 *
 * If a vector original ever arrives, swap the <Image> for the inline SVG and
 * nothing else in the project needs to change.
 */
export function Logo({
  variant = "light",
  className,
  priority = false,
}: {
  variant?: "light" | "dark";
  className?: string;
  priority?: boolean;
}) {
  const asset = variant === "light" ? brand.logoLight : brand.logo;

  return (
    <Image
      src={asset.src}
      width={asset.width}
      height={asset.height}
      alt={asset.alt}
      priority={priority}
      className={cn("h-7 w-auto md:h-8", className)}
    />
  );
}

/**
 * Compact text wordmark, used where the raster logo would be too wide — the
 * demo bar, for instance. Space Grotesk 700 with the accent mark before it.
 */
export function Wordmark({
  className,
  markColor = "var(--accent)",
  textColor = "currentColor",
}: {
  className?: string;
  markColor?: string;
  textColor?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-[family-name:var(--font-space-grotesk)] text-[15px] font-bold tracking-[-0.02em]",
        className,
      )}
    >
      <svg
        viewBox="0 0 16 16"
        aria-hidden="true"
        className="size-[14px] shrink-0"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M8 0.8 14.6 4.6v7.6L8 15.9 1.4 12.2V4.6L8 0.8Z" fill={markColor} />
      </svg>
      <span style={{ color: textColor }}>Webora</span>
    </span>
  );
}
