"use client";

import { cn } from "@/lib/utils";
import type { CSSProperties, ReactNode } from "react";
import { useParallax } from "@/lib/motion";

/**
 * Wraps a large image so it answers the cursor.
 *
 * The movement is deliberately small — a few pixels and under a degree — because
 * the point is that the picture feels like it sits in the page rather than on
 * it. Anything further and it stops reading as depth and starts reading as an
 * effect.
 *
 * Which element the pointer is tracked against is decided by the markup, not by
 * a prop: the nearest ancestor carrying `data-parallax-area` wins, and failing
 * that it is the static wrapper below — never the layer itself, which moves out
 * from under the cursor. A full-bleed hero marks its section; an image in the
 * page marks nothing and tracks its own box.
 */
export function Parallax({
  className,
  layerClassName,
  shift = 6,
  tilt = 0.9,
  scale = 1.035,
  children,
}: {
  className?: string;
  layerClassName?: string;
  /** Travel at the edge of the area, in px. */
  shift?: number;
  /** Tilt at the edge of the area, in degrees. */
  tilt?: number;
  /** Resting scale, which keeps the edges off screen while it moves. */
  scale?: number;
  children: ReactNode;
}) {
  const ref = useParallax<HTMLDivElement>();

  return (
    <div className={cn("parallax", className)}>
      <div
        ref={ref}
        className={cn("parallax-layer", layerClassName)}
        style={
          {
            "--parallax-shift": `${shift}px`,
            "--parallax-tilt": `${tilt}deg`,
            "--parallax-scale": scale,
          } as CSSProperties
        }
      >
        {children}
      </div>
    </div>
  );
}
