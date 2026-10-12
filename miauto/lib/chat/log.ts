import { HASH } from "@/content/knowledge.generated";
import type { FallbackReason } from "./types";
import type { Locale } from "@/content/types";

/**
 * One structured line per request. Deliberately absent: message text. Nothing a
 * visitor types is logged, here or anywhere else.
 */
export type RequestLog = {
  readonly ts: string;
  readonly locale: Locale;
  readonly latencyMs: number;
  readonly inputTokens: number;
  readonly outputTokens: number;
  readonly cacheHit: boolean;
  readonly fallback: FallbackReason | null;
  readonly intent: string;
  readonly knowledgeHash: string;
};

export function logRequest(entry: Omit<RequestLog, "ts" | "knowledgeHash">): void {
  const line: RequestLog = { ts: new Date().toISOString(), knowledgeHash: HASH, ...entry };
  console.log(`[chat] ${JSON.stringify(line)}`);
}

/** Coarse intent label, derived from the source tag or the scripted node id. */
export function intentFrom(sourceIds: readonly string[], scriptedId?: string): string {
  if (scriptedId) return scriptedId;
  return sourceIds[0] ?? "unknown";
}

export function logFeedback(requestId: string, signal: "up" | "down"): void {
  console.log(`[chat-feedback] ${JSON.stringify({ requestId, signal, ts: new Date().toISOString() })}`);
}
