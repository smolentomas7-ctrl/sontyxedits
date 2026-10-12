"use client";

import clsx from "clsx";
import Image from "next/image";
import { staggerDelay, useReveal } from "@/lib/motion";
import type { ImageSlot } from "@/config/images";

/**
 * Every content image on the site goes through here.
 *
 * The box is reserved with `aspect-ratio` from the slot's intrinsic dimensions
 * before anything loads, and a dominant-colour placeholder sits underneath, so
 * the reveal can never shift layout and nothing flashes white.
 */
export function SlotImage({
  slot,
  alt,
  priority = false,
  index = 0,
  sizes = "(min-width: 1024px) 50vw, 100vw",
  variant = "src",
  className,
  imgClassName,
}: {
  slot: ImageSlot;
  /** Meaningful alt in the page's language, or "" when purely decorative. */
  alt: string;
  priority?: boolean;
  index?: number;
  sizes?: string;
  variant?: "src" | "card" | "thumb";
  className?: string;
  imgClassName?: string;
}) {
  const { ref, revealed } = useReveal<HTMLDivElement>();
  const src = slot[variant];

  return (
    <div
      ref={ref}
      className={clsx("relative overflow-hidden", className)}
      style={{
        aspectRatio: `${slot.width} / ${slot.height}`,
        backgroundColor: slot.placeholder,
      }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        sizes={sizes}
        priority={priority}
        loading={priority ? undefined : "lazy"}
        className={clsx("reveal-image object-cover", imgClassName)}
        data-revealed={priority || revealed ? "true" : "false"}
        style={{ ["--reveal-delay" as string]: staggerDelay(index) }}
      />
    </div>
  );
}
