import type { Dictionary, Locale } from "./types";
import { sk } from "./sk";
import { en } from "./en";

export const dictionaries: Record<Locale, Dictionary> = { sk, en };

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale];
}

export * from "./types";
