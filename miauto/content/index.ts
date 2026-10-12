import { sk } from "./sk";
import { en } from "./en";
import { DEFAULT_LOCALE, LOCALES, type Locale, type LocaleContent } from "./types";

export const content: Record<Locale, LocaleContent> = { sk, en };

export function getContent(locale: Locale): LocaleContent {
  return content[locale];
}

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

export { DEFAULT_LOCALE, LOCALES };
export type { Locale, LocaleContent };
export * from "./types";
