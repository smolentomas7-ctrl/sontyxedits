"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import type { ImageSlot } from "@/config/images";

/**
 * Draggable before/after comparison.
 *
 * Both images must share identical dimensions or the halves will not line up;
 * the pairs in config/images.ts are cropped to match. The divider is an
 * <input type="range">, which gives keyboard support (arrows, Home, End),
 * a screen-reader-announced value and touch support for free, rather than
 * reimplementing all of that on a div with pointer handlers.
 */
export function BeforeAfter({
  before,
  after,
  label,
  beforeLabel = "Pred",
  afterLabel = "Po",
}: {
  before: ImageSlot;
  after: ImageSlot;
  label: string;
  beforeLabel?: string;
  afterLabel?: string;
}) {
  const [position, setPosition] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  const updateFromClientX = useCallback((clientX: number) => {
    const node = containerRef.current;
    if (!node) return;
    const rect = node.getBoundingClientRect();
    if (rect.width === 0) return;
    const ratio = ((clientX - rect.left) / rect.width) * 100;
    setPosition(Math.min(100, Math.max(0, ratio)));
  }, []);

  // Dragging continues even when the pointer leaves the element.
  useEffect(() => {
    function onPointerMove(event: PointerEvent) {
      if (!draggingRef.current) return;
      event.preventDefault();
      updateFromClientX(event.clientX);
    }
    function onPointerUp() {
      draggingRef.current = false;
    }

    window.addEventListener("pointermove", onPointerMove, { passive: false });
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointercancel", onPointerUp);
    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", onPointerUp);
    };
  }, [updateFromClientX]);

  const aspect = `${before.width} / ${before.height}`;

  return (
    <figure className="m-0">
      <div
        ref={containerRef}
        className="relative select-none overflow-hidden rounded-xl border border-[#D4D4D0] bg-[#2B2B2B]"
        style={{ aspectRatio: aspect, touchAction: "pan-y" }}
        onPointerDown={(event) => {
          draggingRef.current = true;
          updateFromClientX(event.clientX);
        }}
      >
        {/* After image sits underneath and is fully visible. */}
        <Image
          src={after.src}
          alt={after.alt}
          fill
          loading="lazy"
          sizes="(max-width: 1024px) 100vw, 50vw"
          className="object-cover"
        />

        {/* Before image is clipped to the divider position. */}
        <div
          className="absolute inset-0 overflow-hidden"
          style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
        >
          <Image
            src={before.src}
            alt={before.alt}
            fill
            loading="lazy"
            sizes="(max-width: 1024px) 100vw, 50vw"
            className="object-cover"
          />
        </div>

        <span className="pointer-events-none absolute left-3 top-3 rounded bg-black/65 px-2.5 py-1 text-[12px] font-bold uppercase tracking-wide text-white">
          {beforeLabel}
        </span>
        <span className="pointer-events-none absolute right-3 top-3 rounded bg-black/65 px-2.5 py-1 text-[12px] font-bold uppercase tracking-wide text-white">
          {afterLabel}
        </span>

        {/* Divider line and grip, purely visual — the range input below drives it. */}
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-y-0 w-0.5 bg-[#F5C518]"
          style={{ left: `${position}%` }}
        >
          <span className="absolute left-1/2 top-1/2 flex size-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-[#F5C518] bg-[#1C1C1A] text-[#F5C518]">
            <svg viewBox="0 0 24 24" className="size-4" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="m9 7-5 5 5 5M15 7l5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
        </div>
      </div>

      <label className="mt-3 block">
        <span className="sr-only">{label}</span>
        <input
          type="range"
          min={0}
          max={100}
          step={1}
          value={Math.round(position)}
          onChange={(event) => setPosition(Number(event.target.value))}
          aria-label={label}
          aria-valuetext={`${Math.round(position)} % ${beforeLabel.toLowerCase()}`}
          className="w-full accent-[#F5C518]"
        />
      </label>
    </figure>
  );
}
