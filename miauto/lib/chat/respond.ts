import Anthropic from "@anthropic-ai/sdk";
import { knowledgeBlock, rulesBlock } from "./prompt";
import { respondScripted, scriptedForIntent } from "./scripted";
import { shouldResummarize, splitHistory, summarize } from "./memory";
import { extractSources, retryInstruction, verify } from "./verify";
import { overBudget, recordTokens } from "./ratelimit";
import type { ChatMessage, FallbackReason, Node } from "./types";
import type { Locale } from "@/content/types";

export const MAX_ASSISTANT_TURNS = 10;
/**
 * Generous for a two-to-five-sentence answer, because on the current models
 * thinking cannot be switched off and it is billed out of the same budget. A
 * tight ceiling would truncate the answer mid-sentence instead of saving money;
 * `effort: "low"` is what keeps the reasoning short.
 */
const MAX_TOKENS = 1200;
const UPSTREAM_TIMEOUT_MS = 20_000;

export type Strategy =
  | { readonly mode: "scripted"; readonly node: Node; readonly reason: FallbackReason }
  | { readonly mode: "model"; readonly run: () => AsyncGenerator<string, ModelResult> };

export type ModelResult = {
  readonly text: string;
  readonly sources: readonly string[];
  readonly inputTokens: number;
  readonly outputTokens: number;
  readonly cacheHit: boolean;
  readonly blocked: boolean;
};

/**
 * Server-side configuration. None of these is a NEXT_PUBLIC_ variable, so none
 * of them can reach the browser bundle.
 *
 * `CHAT_MODEL` is the operator's lever: unset it and the assistant runs on the
 * default below. The deployment notes in README.md list what each model costs.
 */
const MODEL = process.env.CHAT_MODEL ?? "claude-opus-5-5";
const API_KEY = process.env.ANTHROPIC_API_KEY ?? process.env.CHAT_API_KEY ?? "";
/** Optional: point the SDK at a gateway or a local stub instead of the default API. */
const BASE_URL = process.env.CHAT_BASE_URL ?? "";

/**
 * Server-side refusal fallback: if the model declines a request on safety
 * grounds, the API re-runs it on a fallback model inside the same call. Only
 * some models accept the parameter, so it is sent only for those — on anything
 * else a decline still degrades to the scripted tier rather than erroring.
 */
const SUPPORTS_FALLBACK = /^claude-(opus-5|opus-5-5|fable-5|fable-5-1|sonnet-5-5)\b/.test(MODEL);

export function modelConfigured(): boolean {
  return API_KEY !== "" && MODEL !== "";
}

/**
 * The fields this code reads from a streamed event. Both the stable and the beta
 * event unions are supersets of this, which lets one loop consume either.
 */
type StreamEvent = {
  readonly type: string;
  readonly delta?: { readonly type?: string; readonly text?: string; readonly stop_reason?: string | null };
  readonly message?: {
    readonly usage?: { readonly input_tokens?: number; readonly cache_read_input_tokens?: number | null };
  };
  readonly usage?: { readonly output_tokens?: number };
};

/**
 * The single entry point. Tier 1 is built first and is the fallback for every
 * way the model tier can fail, so the widget never shows an error caused by the
 * model being unavailable — the visitor gets a less flexible assistant instead
 * of a blank panel.
 */
export function chooseStrategy(
  locale: Locale,
  message: string,
  history: readonly ChatMessage[],
): Strategy {
  if (!modelConfigured()) {
    return { mode: "scripted", node: respondScripted(locale, message), reason: "no-api-key" };
  }
  if (overBudget()) {
    return { mode: "scripted", node: respondScripted(locale, message), reason: "over-budget" };
  }
  return { mode: "model", run: () => runModel(locale, message, history) };
}

export function scriptedReply(locale: Locale, message: string): Node {
  return respondScripted(locale, message);
}

function buildMessages(
  locale: Locale,
  message: string,
  history: readonly ChatMessage[],
  extraInstruction?: string,
): Anthropic.MessageParam[] {
  const { older, recent } = splitHistory(history);
  const messages: Anthropic.MessageParam[] = [];

  // Volatile context lives here, never in the cached system block.
  const summary =
    older.length > 0 && shouldResummarize(history.length) ? summarize(older, locale) : summarize(older, locale);
  if (summary) {
    messages.push({ role: "user", content: summary });
    messages.push({
      role: "assistant",
      content: locale === "sk" ? "Rozumiem, pokračujme." : "Understood, let's continue.",
    });
  }

  for (const turn of recent) {
    messages.push({ role: turn.role, content: turn.content });
  }

  messages.push({
    role: "user",
    content: extraInstruction ? `${message}\n\n[${extraInstruction}]` : message,
  });

  return messages;
}

async function* runModel(
  locale: Locale,
  message: string,
  history: readonly ChatMessage[],
): AsyncGenerator<string, ModelResult> {
  const client = new Anthropic({
    apiKey: API_KEY,
    ...(BASE_URL ? { baseURL: BASE_URL } : {}),
  });
  const ecuContext = /cipovanie|ecu|chiptuning|tuning|softver|remap|chip/i.test(
    message.normalize("NFD").replace(/[̀-ͯ]/g, ""),
  );

  let attempt = 0;
  let instruction: string | undefined;
  let lastResult: ModelResult | null = null;

  // One retry on a verifier block; a second failure falls through to scripted.
  while (attempt < 2) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), UPSTREAM_TIMEOUT_MS);
    let text = "";
    let inputTokens = 0;
    let outputTokens = 0;
    let cacheHit = false;

    let refused = false;

    try {
      const params = {
        model: MODEL,
        max_tokens: MAX_TOKENS,
        // Short answers from a fixed knowledge block need no deep reasoning, and
        // thinking cannot be disabled on the current models — low effort is the
        // control that keeps both latency and the bill down.
        output_config: { effort: "low" as const },
        system: [
          { type: "text" as const, text: rulesBlock(locale) },
          {
            type: "text" as const,
            text: knowledgeBlock(locale),
            cache_control: { type: "ephemeral" as const },
          },
        ],
        messages: buildMessages(locale, message, history, instruction),
        stream: true as const,
      };

      const raw = SUPPORTS_FALLBACK
        ? await client.beta.messages.create(
            { ...params, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default" },
            { signal: controller.signal },
          )
        : await client.messages.create(params, { signal: controller.signal });

      const stream = raw as unknown as AsyncIterable<StreamEvent>;

      for await (const event of stream) {
        if (event.type === "content_block_delta" && event.delta?.type === "text_delta") {
          const chunk = event.delta.text ?? "";
          text += chunk;
          // Only the first attempt streams to the visitor; a retry is verified
          // in full before anything is shown, so a bad reply is never half-seen.
          if (attempt === 0) yield chunk;
        } else if (event.type === "message_start") {
          const usage = event.message?.usage;
          inputTokens = usage?.input_tokens ?? 0;
          cacheHit = (usage?.cache_read_input_tokens ?? 0) > 0;
        } else if (event.type === "message_delta") {
          outputTokens = event.usage?.output_tokens ?? 0;
          if (event.delta?.stop_reason === "refusal") refused = true;
        }
      }
    } catch (error) {
      clearTimeout(timeout);
      const aborted = error instanceof Error && error.name === "AbortError";
      throw Object.assign(new Error("upstream"), {
        reason: (aborted ? "timeout" : "upstream-error") satisfies FallbackReason,
      });
    }
    clearTimeout(timeout);
    recordTokens(inputTokens + outputTokens);

    // A safety decline arrives as a normal 200 with little or no text. Treat it
    // like any other upstream failure: the visitor gets the scripted answer, not
    // a half sentence that stops.
    if (refused || text.trim() === "") {
      throw Object.assign(new Error("upstream"), {
        reason: "upstream-error" satisfies FallbackReason,
      });
    }

    const verdict = verify(text, { locale, ecuContext });
    if (verdict.ok) {
      return {
        text: verdict.text,
        sources: extractSources(verdict.text, locale),
        inputTokens,
        outputTokens,
        cacheHit,
        blocked: false,
      };
    }

    console.warn(`[chat] verifier blocked: ${verdict.code} (${verdict.detail})`);
    instruction = retryInstruction(verdict.code, locale);
    lastResult = {
      text: "",
      sources: [],
      inputTokens,
      outputTokens,
      cacheHit,
      blocked: true,
    };
    attempt += 1;
  }

  return lastResult ?? {
    text: "",
    sources: [],
    inputTokens: 0,
    outputTokens: 0,
    cacheHit: false,
    blocked: true,
  };
}

export { scriptedForIntent };
