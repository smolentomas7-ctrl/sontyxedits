"use client";

import { useEffect, useRef } from "react";

/**
 * Cursor parallax for a large image, ported from the M.I.Auto build so the
 * Webora hero moves the same way. Moves only for a pointer that can hover,
 * never under prefers-reduced-motion, and writes two CSS custom properties
 * from a single requestAnimationFrame loop that stops itself at rest.
 */
export function useParallax<T extends HTMLElement>() {
  const ref = useRef<T | null>(null);

  useEffect(() => {
    const layer = ref.current;
    if (!layer) return;
    // `Parallax` wraps the layer in a static element of exactly the same box,
    // which is what makes the parent a safe default here.
    const area = layer.closest<HTMLElement>("[data-parallax-area]") ?? layer.parentElement ?? layer;

    const canHover = window.matchMedia("(hover: hover) and (pointer: fine)");
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");

    let frame = 0;
    let box: DOMRect | null = null;
    // target, then the value easing toward it
    let tx = 0;
    let ty = 0;
    let x = 0;
    let y = 0;

    const clamp = (value: number) => Math.max(-1, Math.min(1, value));

    const write = () => {
      layer.style.setProperty("--parallax-x", x.toFixed(4));
      layer.style.setProperty("--parallax-y", y.toFixed(4));
    };

    const tick = () => {
      x += (tx - x) * 0.12;
      y += (ty - y) * 0.12;
      const atRest = tx === 0 && ty === 0 && Math.abs(x) < 0.002 && Math.abs(y) < 0.002;
      if (atRest) {
        x = 0;
        y = 0;
      }
      write();
      if (atRest) {
        layer.style.willChange = "";
        frame = 0;
        return;
      }
      frame = requestAnimationFrame(tick);
    };

    const run = () => {
      if (frame) return;
      layer.style.willChange = "transform";
      frame = requestAnimationFrame(tick);
    };

    const measure = () => {
      box = area.getBoundingClientRect();
    };
    const invalidate = () => {
      box = null;
    };

    const onMove = (event: PointerEvent) => {
      if (event.pointerType === "touch") return;
      if (!box) measure();
      if (!box || box.width === 0 || box.height === 0) return;
      tx = clamp(((event.clientX - box.left) / box.width) * 2 - 1);
      ty = clamp(((event.clientY - box.top) / box.height) * 2 - 1);
      run();
    };

    const onLeave = () => {
      tx = 0;
      ty = 0;
      run();
    };

    const enable = () => {
      area.addEventListener("pointerenter", measure);
      area.addEventListener("pointermove", onMove);
      area.addEventListener("pointerleave", onLeave);
      window.addEventListener("scroll", invalidate, { passive: true });
      window.addEventListener("resize", invalidate);
    };

    const disable = () => {
      area.removeEventListener("pointerenter", measure);
      area.removeEventListener("pointermove", onMove);
      area.removeEventListener("pointerleave", onLeave);
      window.removeEventListener("scroll", invalidate);
      window.removeEventListener("resize", invalidate);
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      tx = 0;
      ty = 0;
      x = 0;
      y = 0;
      write();
      layer.style.willChange = "";
    };

    const sync = () => {
      disable();
      if (canHover.matches && !reduced.matches) enable();
    };

    sync();
    canHover.addEventListener("change", sync);
    reduced.addEventListener("change", sync);
    return () => {
      canHover.removeEventListener("change", sync);
      reduced.removeEventListener("change", sync);
      disable();
    };
  }, []);

  return ref;
}
