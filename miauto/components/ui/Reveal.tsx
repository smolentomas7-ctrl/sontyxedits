"use client";

import clsx from "clsx";
import type { ElementType, ReactNode } from "react";
import { staggerDelay, useReveal } from "@/lib/motion";

/**
 * Fade + 16px rise on first entry into the viewport. Once, never repeated.
 * `index` drives the 60ms grid stagger, capped at six children.
 */
export function Reveal({
  as: Tag = "div",
  index = 0,
  className,
  children,
}: {
  as?: ElementType;
  index?: number;
  className?: string;
  children: ReactNode;
}) {
  const { ref, revealed } = useReveal<HTMLDivElement>();
  return (
    <Tag
      ref={ref}
      className={clsx("reveal", className)}
      data-revealed={revealed ? "true" : "false"}
      style={{ ["--reveal-delay" as string]: staggerDelay(index) }}
    >
      {children}
    </Tag>
  );
}
