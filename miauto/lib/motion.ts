"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Reveal-on-first-view. One IntersectionObserver per element, disconnected the
 * moment it fires: the reveal happens once, never repeats, never loops.
 *
 * Under prefers-reduced-motion the element is marked revealed immediately, so
 * nothing ever waits on an observer to become visible.
 */
export function useReveal<T extends HTMLElement>(options?: {
  rootMargin?: string;
  threshold?: number;
}) {
  const ref = useRef<T | null>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node || revealed) return;

    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduced || typeof IntersectionObserver === "undefined") {
      setRevealed(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setRevealed(true);
            observer.disconnect();
          }
        }
      },
      {
        rootMargin: options?.rootMargin ?? "0px 0px -10% 0px",
        threshold: options?.threshold ?? 0.08,
      },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [revealed, options?.rootMargin, options?.threshold]);

  return { ref, revealed };
}

/** Grid stagger: 60ms per child, capped at 6 — the seventh onward reuses the sixth. */
export function staggerDelay(index: number): string {
  return `${Math.min(index, 5) * 60}ms`;
}

/**
 * Pressed state for tappable elements. `:active` is unreliable on touch, so the
 * state is also driven by pointerdown/up/cancel. `will-change` goes on at press
 * and comes straight back off — never left on permanently.
 */
export function usePressHandlers() {
  const set = (element: HTMLElement, pressed: boolean) => {
    element.dataset["pressed"] = pressed ? "true" : "false";
    element.style.willChange = pressed ? "transform" : "";
  };
  return {
    onPointerDown: (e: React.PointerEvent<HTMLElement>) => set(e.currentTarget, true),
    onPointerUp: (e: React.PointerEvent<HTMLElement>) => set(e.currentTarget, false),
    onPointerCancel: (e: React.PointerEvent<HTMLElement>) => set(e.currentTarget, false),
    onPointerLeave: (e: React.PointerEvent<HTMLElement>) => set(e.currentTarget, false),
  };
}

export function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(query.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/**
 * Cursor parallax.
 *
 * The returned ref goes on the element that moves. The element that *listens* is
 * the nearest ancestor marked `data-parallax-area`, or failing that the moving
 * element's parent — which lets a full-bleed hero track the pointer across the
 * whole section while an image tracks only its own box, with no extra wiring.
 *
 * It is never the moving element itself. That element translates and tilts in
 * answer to the pointer, so a cursor near its edge can be stepped out from
 * under: the browser fires `pointerleave`, the layer returns to rest, the
 * cursor is inside again — a flicker that reads as the effect cutting out. The
 * listening box has to be one the effect does not move.
 *
 * Three things keep it cheap:
 *   - the pointer handler stores a target and nothing else; the only writes
 *     happen inside one requestAnimationFrame loop,
 *   - the loop writes two CSS custom properties, never a layout property, and
 *     stops itself the moment the element is back at rest,
 *   - the container's box is measured on entry and re-measured lazily after a
 *     scroll or resize, so a pointermove never forces a layout read.
 *
 * It runs only for a pointer that can actually hover, and not at all under
 * prefers-reduced-motion. Both are watched, so flipping either at runtime takes
 * effect without a reload.
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

/** True once the component has mounted — used to gate anything time-dependent. */
export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted;
}
