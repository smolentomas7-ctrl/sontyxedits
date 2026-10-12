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

/** True once the component has mounted — used to gate anything time-dependent. */
export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted;
}
