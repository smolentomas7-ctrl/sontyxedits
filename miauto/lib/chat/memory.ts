import type { ChatMessage } from "./types";
import type { Locale } from "@/content/types";

/**
 * Last 6 turns verbatim; anything older is compressed into one
 * <conversation_so_far> block of at most 150 words, regenerated every 4 turns.
 *
 * The summary is volatile, so it goes in `messages` and NEVER in the cached
 * system block — putting it there would bust the prompt cache on every turn.
 */
export const VERBATIM_TURNS = 6;
const SUMMARY_WORD_LIMIT = 150;

export function splitHistory(history: readonly ChatMessage[]): {
  older: readonly ChatMessage[];
  recent: readonly ChatMessage[];
} {
  if (history.length <= VERBATIM_TURNS) return { older: [], recent: history };
  return {
    older: history.slice(0, history.length - VERBATIM_TURNS),
    recent: history.slice(history.length - VERBATIM_TURNS),
  };
}

/**
 * Extractive summary. Deliberately not a second model call: a summary is not
 * worth the latency or the tokens here, and an extractive one cannot hallucinate.
 */
export function summarize(older: readonly ChatMessage[], locale: Locale): string | null {
  if (older.length === 0) return null;

  const asked = older
    .filter((m) => m.role === "user")
    .map((m) => m.content.replace(/\s+/g, " ").trim())
    .filter(Boolean);
  if (asked.length === 0) return null;

  const lead =
    locale === "sk"
      ? "Návštevník sa doteraz pýtal na:"
      : "So far the visitor has asked about:";

  let out = `${lead} ${asked.map((q) => `„${q}"`).join("; ")}.`;
  const words = out.split(/\s+/);
  if (words.length > SUMMARY_WORD_LIMIT) {
    out = `${words.slice(0, SUMMARY_WORD_LIMIT).join(" ")}…`;
  }
  return `<conversation_so_far>\n${out}\n</conversation_so_far>`;
}

/** Regenerated every 4 turns, not on every single one. */
export function shouldResummarize(turnCount: number): boolean {
  return turnCount % 4 === 0;
}
