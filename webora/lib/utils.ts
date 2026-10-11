import clsx, { type ClassValue } from "clsx";

/** Conditional className helper used across the project. */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

/** Formats a number as euros with no decimals, e.g. 1 240 €. */
export function formatEur(value: number, locale: "sk" | "en"): string {
  return new Intl.NumberFormat(locale === "sk" ? "sk-SK" : "en-IE", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

/** Formats an ISO date string for display. */
export function formatDate(iso: string, locale: "sk" | "en"): string {
  return new Intl.DateTimeFormat(locale === "sk" ? "sk-SK" : "en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(iso));
}
