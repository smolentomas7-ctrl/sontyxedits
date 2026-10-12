import Anthropic from "@anthropic-ai/sdk";
import { knowledgeBlock, rulesBlock } from "./prompt";
import { respondScripted, scriptedForIntent } from "./scripted";
import { shouldResummarize, splitHistory, summarize } from "./memory";
import { extractSources, retryInstruction, verify } from "./verify";
import { overBudget, recordTokens } from "./ratelimit";
import type { ChatMessage, FallbackReason, Node } from "./types";
import type { Locale } from "@/content/types";

export const MAX_ASSISTANT_TURNS = 10;
const MAX_TOKENS = 400;
const UPSTREAM_TIMEOUT_MS = 15_000;

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

const MODEL = process.env.CHAT_MODEL ?? "";
const API_KEY = process.env.CHAT_API_KEY ?? "";
/** Optional: point the SDK at a gateway or a local stub instead of the default API. */
const BASE_URL = process.env.CHAT_BASE_URL ?? "";

export function modelConfigured(): boolean {
  return API_KEY !== "" && MODEL !== "";
}

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

    try {
      const stream = await client.messages.create(
        {
          model: MODEL,
          max_tokens: MAX_TOKENS,
          system: [
            { type: "text", text: rulesBlock(locale) },
            {
              type: "text",
              text: knowledgeBlock(locale),
              cache_control: { type: "ephemeral" },
            },
          ],
          messages: buildMessages(locale, message, history, instruction),
          stream: true,
        },
        { signal: controller.signal },
      );

      for await (const event of stream) {
        if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
          text += event.delta.text;
          // Only the first attempt streams to the visitor; a retry is verified
          // in full before anything is shown, so a bad reply is never half-seen.
          if (attempt === 0) yield event.delta.text;
        } else if (event.type === "message_start") {
          const usage = event.message.usage;
          inputTokens = usage.input_tokens ?? 0;
          cacheHit = (usage.cache_read_input_tokens ?? 0) > 0;
        } else if (event.type === "message_delta") {
          outputTokens = event.usage.output_tokens ?? 0;
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
