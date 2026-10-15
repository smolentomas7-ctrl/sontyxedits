import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Conditional className helper used across the project.
 *
 * twMerge, not clsx alone: a component's base classes and the `className` a
 * caller passes often target the same property, and with plain concatenation
 * the winner is decided by the order Tailwind happens to emit the utilities
 * in, not by the caller's intent. That is how the header's CTA, marked
 * `hidden sm:inline-flex`, still rendered at 320px and pushed the menu button
 * off screen. Merging resolves the conflict in favour of the caller.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Formats an ISO date string for display. */
export function formatDate(iso: string, locale: "sk" | "en"): string {
  return new Intl.DateTimeFormat(locale === "sk" ? "sk-SK" : "en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(iso));
}
