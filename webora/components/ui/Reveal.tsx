"use client";

import { createElement, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

/**
 * Fades and rises its children into view once. Respects prefers-reduced-motion
 * via the .reveal rules in globals.css, which disable the transform entirely.
 */
export function Reveal({
  children,
  delay = 0,
  className,
  as: Tag = "div",
}: {
  children: React.ReactNode;
  /** Stagger in milliseconds, typically index * 60. */
  delay?: number;
  className?: string;
  as?: "div" | "li" | "article" | "section";
}) {
  const ref = useRef<HTMLElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    // If IntersectionObserver is unavailable, show immediately rather than
    // leaving the content invisible.
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
          }
        }
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  // createElement keeps the polymorphic `as` prop without fighting the
  // per-element ref types that JSX would infer.
  return createElement(
    Tag,
    {
      ref,
      className: cn("reveal", visible && "is-visible", className),
      style: { "--reveal-delay": `${delay}ms` } as React.CSSProperties,
    },
    children,
  );
}
