"use client";

import { createElement, useCallback, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

/**
 * Cursor-responsive 3D tilt.
 *
 * Design notes, because the naive version of this is a performance trap:
 *
 * - Pointer moves never touch React state. They write to a ref and schedule a
 *   single rAF, so a fast pointer produces one style write per frame instead
 *   of one render per event.
 * - The element rect is measured on enter and on resize, not per move, so we
 *   never force layout inside the pointer handler.
 * - Motion is critically damped toward the target rather than snapped, which
 *   is what makes it read as "spring" rather than "jitter".
 * - Only `transform` is animated, so it stays on the compositor.
 * - Touch devices and prefers-reduced-motion get no tilt at all. The hover
 *   scale is dropped too, since on touch there is no hover to leave.
 */

export type TiltProps = {
  children: React.ReactNode;
  className?: string;
  /** Peak rotation in degrees at the edge of the element. */
  max?: number;
  /** Scale applied while the pointer is inside. */
  scale?: number;
  /** Pixels the inner layer shifts, for parallax between card and image. */
  depth?: number;
  /** 0–1. Higher follows the cursor faster. */
  stiffness?: number;
  /** Adds a specular highlight that tracks the cursor. */
  glare?: boolean;
  as?: "div" | "article" | "li";
};

export function Tilt({
  children,
  className,
  max = 7,
  scale = 1.015,
  depth = 0,
  stiffness = 0.12,
  glare = false,
  as: Tag = "div",
}: TiltProps) {
  const rootRef = useRef<HTMLElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  const glareRef = useRef<HTMLDivElement>(null);

  // Target and current values, kept outside React entirely.
  const target = useRef({ rx: 0, ry: 0, s: 1, gx: 50, gy: 50, go: 0 });
  const current = useRef({ rx: 0, ry: 0, s: 1, gx: 50, gy: 50, go: 0 });
  const rect = useRef<DOMRect | null>(null);
  const frame = useRef<number | null>(null);
  const enabled = useRef(false);

  const tick = useCallback(() => {
    const c = current.current;
    const t = target.current;
    const k = stiffness;

    c.rx += (t.rx - c.rx) * k;
    c.ry += (t.ry - c.ry) * k;
    c.s += (t.s - c.s) * k;
    c.gx += (t.gx - c.gx) * k;
    c.gy += (t.gy - c.gy) * k;
    c.go += (t.go - c.go) * k;

    const root = rootRef.current;
    if (root) {
      root.style.transform =
        `perspective(1000px) rotateX(${c.rx.toFixed(3)}deg) ` +
        `rotateY(${c.ry.toFixed(3)}deg) scale(${c.s.toFixed(4)})`;
    }
    if (innerRef.current && depth !== 0) {
      // Inner layer moves opposite the tilt, which reads as parallax depth.
      const px = (-c.ry / Math.max(max, 0.001)) * depth;
      const py = (c.rx / Math.max(max, 0.001)) * depth;
      innerRef.current.style.transform = `translate3d(${px.toFixed(2)}px, ${py.toFixed(2)}px, 0)`;
    }
    if (glareRef.current && glare) {
      glareRef.current.style.opacity = c.go.toFixed(3);
      glareRef.current.style.background =
        `radial-gradient(circle at ${c.gx.toFixed(1)}% ${c.gy.toFixed(1)}%, ` +
        `rgba(255,255,255,0.16), rgba(255,255,255,0) 55%)`;
    }

    const settled =
      Math.abs(t.rx - c.rx) < 0.01 &&
      Math.abs(t.ry - c.ry) < 0.01 &&
      Math.abs(t.s - c.s) < 0.0005 &&
      Math.abs(t.go - c.go) < 0.01;

    frame.current = settled ? null : requestAnimationFrame(tick);
  }, [depth, glare, max, stiffness]);

  const schedule = useCallback(() => {
    if (frame.current === null) frame.current = requestAnimationFrame(tick);
  }, [tick]);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    // `hover: hover` is the reliable signal for a real pointer; touch screens
    // report `hover: none` and would otherwise latch a tilt on first tap.
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)");

    function evaluate() {
      enabled.current = fine.matches && !reduced.matches;
      if (!enabled.current) {
        target.current = { rx: 0, ry: 0, s: 1, gx: 50, gy: 50, go: 0 };
        schedule();
      }
    }
    evaluate();
    reduced.addEventListener("change", evaluate);
    fine.addEventListener("change", evaluate);

    function onEnter() {
      if (!enabled.current) return;
      rect.current = root!.getBoundingClientRect();
      target.current.s = scale;
      target.current.go = glare ? 1 : 0;
      schedule();
    }

    function onMove(event: PointerEvent) {
      if (!enabled.current) return;
      const r = rect.current;
      if (!r || r.width === 0 || r.height === 0) return;
      // -0.5 .. 0.5 from the element centre.
      const px = (event.clientX - r.left) / r.width - 0.5;
      const py = (event.clientY - r.top) / r.height - 0.5;
      target.current.ry = px * max * 2;
      target.current.rx = -py * max * 2;
      target.current.gx = (px + 0.5) * 100;
      target.current.gy = (py + 0.5) * 100;
      schedule();
    }

    function onLeave() {
      target.current = { rx: 0, ry: 0, s: 1, gx: 50, gy: 50, go: 0 };
      schedule();
    }

    function onResize() {
      if (rect.current) rect.current = root!.getBoundingClientRect();
    }

    root.addEventListener("pointerenter", onEnter);
    root.addEventListener("pointermove", onMove);
    root.addEventListener("pointerleave", onLeave);
    window.addEventListener("resize", onResize, { passive: true });
    window.addEventListener("scroll", onResize, { passive: true });

    return () => {
      root.removeEventListener("pointerenter", onEnter);
      root.removeEventListener("pointermove", onMove);
      root.removeEventListener("pointerleave", onLeave);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onResize);
      reduced.removeEventListener("change", evaluate);
      fine.removeEventListener("change", evaluate);
      if (frame.current !== null) {
        cancelAnimationFrame(frame.current);
        frame.current = null;
      }
    };
  }, [glare, max, scale, schedule]);

  const body = (
    <>
      {depth !== 0 ? (
        <div ref={innerRef} className="h-full will-change-transform">
          {children}
        </div>
      ) : (
        children
      )}

      {glare ? (
        <div
          ref={glareRef}
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 rounded-[inherit] opacity-0 mix-blend-overlay"
        />
      ) : null}
    </>
  );

  // createElement keeps the polymorphic `as` prop without fighting the
  // per-element ref types that JSX would infer.
  return createElement(
    Tag,
    {
      ref: rootRef,
      // Marks the element for the validation suite, which asserts that the
      // transform tracks the cursor and stays flat on touch and under
      // prefers-reduced-motion.
      "data-tilt": "",
      className: cn("relative [transform-style:preserve-3d] will-change-transform", className),
    },
    body,
  );
}
