"use client";

import { useCallback, useEffect, useRef } from "react";
import Image from "next/image";
import { X, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export type LightboxItem = {
  src: string;
  width: number;
  height: number;
  alt: string;
  /** Caption heading, e.g. the project name. */
  title?: string;
  /** Optional link rendered under the caption. */
  href?: string;
  hrefLabel?: string;
};

const FOCUSABLE =
  'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

/**
 * Reusable modal image viewer, built from scratch rather than pulled from a
 * library. Handles:
 *   - Escape to close, click on the backdrop to close
 *   - ArrowLeft / ArrowRight to move between items
 *   - a focus trap cycling within the dialog
 *   - body scroll lock while open
 *   - returning focus to the element that opened it
 */
export function Lightbox({
  items,
  index,
  onClose,
  onIndexChange,
  label,
  counterWord,
  closeLabel,
  prevLabel,
  nextLabel,
}: {
  items: LightboxItem[];
  /** Null means closed. */
  index: number | null;
  onClose: () => void;
  onIndexChange: (next: number) => void;
  label: string;
  counterWord: string;
  closeLabel: string;
  prevLabel: string;
  nextLabel: string;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previouslyFocused = useRef<HTMLElement | null>(null);

  const isOpen = index !== null;
  const hasMultiple = items.length > 1;

  const goPrev = useCallback(() => {
    if (index === null) return;
    onIndexChange((index - 1 + items.length) % items.length);
  }, [index, items.length, onIndexChange]);

  const goNext = useCallback(() => {
    if (index === null) return;
    onIndexChange((index + 1) % items.length);
  }, [index, items.length, onIndexChange]);

  // Remember the trigger, move focus in, and restore focus on close.
  useEffect(() => {
    if (!isOpen) return;
    previouslyFocused.current = document.activeElement as HTMLElement | null;
    closeButtonRef.current?.focus();

    return () => {
      previouslyFocused.current?.focus?.();
    };
  }, [isOpen]);

  // Lock body scroll while the dialog is open.
  useEffect(() => {
    if (!isOpen) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, [isOpen]);

  // Keyboard handling, including the focus trap.
  useEffect(() => {
    if (!isOpen) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key === "ArrowLeft" && hasMultiple) {
        event.preventDefault();
        goPrev();
        return;
      }

      if (event.key === "ArrowRight" && hasMultiple) {
        event.preventDefault();
        goNext();
        return;
      }

      if (event.key !== "Tab") return;

      const root = dialogRef.current;
      if (!root) return;

      const focusable = Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
        (el) => el.offsetParent !== null || el === document.activeElement,
      );
      if (focusable.length === 0) {
        event.preventDefault();
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [isOpen, hasMultiple, goPrev, goNext, onClose]);

  if (index === null) return null;
  const item = items[index];
  if (!item) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/88 p-4 backdrop-blur-sm md:p-8"
      onClick={(event) => {
        // Only close when the backdrop itself was clicked.
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className="relative flex max-h-full w-full max-w-5xl flex-col gap-4"
      >
        <div className="flex items-center justify-between gap-4">
          <p className="t-small text-text-muted" aria-live="polite">
            {index + 1} {counterWord} {items.length}
          </p>
          <button
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            aria-label={closeLabel}
            className="inline-flex size-10 items-center justify-center rounded-full border border-white/15 bg-white/5 text-text transition-colors duration-150 hover:bg-white/15"
          >
            <X aria-hidden="true" strokeWidth={1.5} className="size-5" />
          </button>
        </div>

        <div className="relative flex min-h-0 flex-1 items-center justify-center">
          {hasMultiple ? (
            <button
              type="button"
              onClick={goPrev}
              aria-label={prevLabel}
              className={cn(
                "absolute left-0 z-10 inline-flex size-11 items-center justify-center rounded-full",
                "border border-white/15 bg-black/60 text-text backdrop-blur",
                "transition-colors duration-150 hover:bg-black/80 md:-left-4",
              )}
            >
              <ChevronLeft aria-hidden="true" strokeWidth={1.5} className="size-6" />
            </button>
          ) : null}

          <Image
            key={item.src}
            src={item.src}
            width={item.width}
            height={item.height}
            alt={item.alt}
            sizes="(max-width: 1024px) 100vw, 1024px"
            className="max-h-[70vh] w-auto rounded-xl border border-white/10 object-contain"
          />

          {hasMultiple ? (
            <button
              type="button"
              onClick={goNext}
              aria-label={nextLabel}
              className={cn(
                "absolute right-0 z-10 inline-flex size-11 items-center justify-center rounded-full",
                "border border-white/15 bg-black/60 text-text backdrop-blur",
                "transition-colors duration-150 hover:bg-black/80 md:-right-4",
              )}
            >
              <ChevronRight aria-hidden="true" strokeWidth={1.5} className="size-6" />
            </button>
          ) : null}
        </div>

        {item.title ? (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="font-[family-name:var(--font-space-grotesk)] text-lg text-text">
              {item.title}
            </p>
            {item.href && item.hrefLabel ? (
              <a
                href={item.href}
                className="t-small font-medium text-accent underline underline-offset-4 hover:text-accent-hover"
              >
                {item.hrefLabel}
              </a>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
