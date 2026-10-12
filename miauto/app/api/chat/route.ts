import { z } from "zod";
import { SOURCES } from "@/content/knowledge.generated";
import { LOCALES, type Locale } from "@/content/types";
import { getContent } from "@/content";
import { siteUrl } from "@/config/miauto";
import { chooseStrategy, MAX_ASSISTANT_TURNS, scriptedReply } from "@/lib/chat/respond";
import { rateLimit } from "@/lib/chat/ratelimit";
import { intentFrom, logRequest } from "@/lib/chat/log";
import type { FallbackReason } from "@/lib/chat/types";

// Node runtime: the SDK and the key both need it, and the key is read from
// process.env inside the handler. It is never a NEXT_PUBLIC_ variable, never
// touches a client component, and never reaches the shipped bundle.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MESSAGE_MAX = 2000;
const HISTORY_MAX_TURNS = 12;
const HISTORY_MAX_CHARS = 6000;

const RequestSchema = z.object({
  locale: z.enum(LOCALES),
  message: z.string().min(1).max(MESSAGE_MAX),
  /**
   * Total assistant turns in this visitor's session. `history` is capped at 12
   * entries, so counting assistant turns inside it can never reach the limit;
   * the client reports the real total from its own transcript.
   */
  turnCount: z.number().int().min(0).max(1000).default(0),
  history: z
    .array(
      z.object({
        role: z.enum(["user", "assistant"]),
        content: z.string().min(1).max(MESSAGE_MAX),
      }),
    )
    .max(HISTORY_MAX_TURNS)
    .default([]),
});

function sse(data: unknown): string {
  return `data: ${JSON.stringify(data)}\n\n`;
}

function headers(): HeadersInit {
  return {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache, no-transform",
    Connection: "keep-alive",
    // Without this some proxies buffer the whole response and streaming
    // silently stops working in production while it still works locally.
    "X-Accel-Buffering": "no",
  };
}

function sameOrigin(request: Request): boolean {
  const origin = request.headers.get("origin");
  if (!origin) return true; // same-origin fetches may omit it
  try {
    const incoming = new URL(origin);
    const host = request.headers.get("host");
    if (host && incoming.host === host) return true;
    return incoming.host === new URL(siteUrl).host;
  } catch {
    return false;
  }
}

function clientIp(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) return (forwarded.split(",")[0] ?? "").trim() || "unknown";
  return request.headers.get("x-nf-client-connection-ip") ?? "unknown";
}

function sourceHref(locale: Locale, id: string): string {
  return SOURCES[locale][id] ?? `/${locale}`;
}

/** Streams a scripted node. Same wire format as the model path. */
function scriptedStream(
  locale: Locale,
  message: string,
  reason: FallbackReason,
  startedAt: number,
) {
  const node = scriptedReply(locale, message);
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      // Chunked so the widget's caret behaves identically in both tiers.
      for (const chunk of node.answer.match(/\S+\s*/g) ?? [node.answer]) {
        controller.enqueue(encoder.encode(sse({ type: "token", value: chunk })));
      }
      for (const id of (node.answer.match(/\[source:\s*([^\]]+)\]/g) ?? []).map((m) =>
        m.replace(/\[source:\s*|\]/g, "").trim(),
      )) {
        if (SOURCES[locale][id]) {
          controller.enqueue(
            encoder.encode(sse({ type: "source", id, href: sourceHref(locale, id) })),
          );
        }
      }
      controller.enqueue(
        encoder.encode(sse({ type: "done", mode: "scripted", chips: node.chips ?? [] })),
      );
      controller.close();

      logRequest({
        locale,
        latencyMs: Date.now() - startedAt,
        inputTokens: 0,
        outputTokens: 0,
        cacheHit: false,
        fallback: reason,
        intent: intentFrom([], node.id),
      });
    },
  });

  return new Response(stream, { headers: headers() });
}

export async function POST(request: Request): Promise<Response> {
  const startedAt = Date.now();

  // Origin check first, before a single token is spent.
  if (!sameOrigin(request)) {
    return new Response(JSON.stringify({ error: "forbidden" }), {
      status: 403,
      headers: { "Content-Type": "application/json" },
    });
  }

  let parsed: z.infer<typeof RequestSchema>;
  try {
    parsed = RequestSchema.parse(await request.json());
  } catch {
    return new Response(JSON.stringify({ error: "bad request" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const { locale, message } = parsed;
  let history = parsed.history;

  let total = 0;
  const trimmed: typeof history = [];
  for (let i = history.length - 1; i >= 0; i -= 1) {
    const turn = history[i];
    if (!turn) continue;
    total += turn.content.length;
    if (total > HISTORY_MAX_CHARS) break;
    trimmed.unshift(turn);
  }
  history = trimmed;

  // After 10 assistant turns, point at the phone and stop taking more.
  const assistantTurns = Math.max(
    parsed.turnCount,
    history.filter((turn) => turn.role === "assistant").length,
  );
  if (assistantTurns >= MAX_ASSISTANT_TURNS) {
    const t = getContent(locale);
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(sse({ type: "token", value: t.chat.turnLimit })));
        controller.enqueue(
          encoder.encode(sse({ type: "done", mode: "scripted", chips: [] })),
        );
        controller.close();
        logRequest({
          locale,
          latencyMs: Date.now() - startedAt,
          inputTokens: 0,
          outputTokens: 0,
          cacheHit: false,
          fallback: "turn-limit",
          intent: "turn-limit",
        });
      },
    });
    return new Response(stream, { headers: headers() });
  }

  const limit = rateLimit(clientIp(request));
  if (!limit.allowed) {
    return scriptedStream(locale, message, "rate-limited", startedAt);
  }

  const strategy = chooseStrategy(locale, message, history);
  if (strategy.mode === "scripted") {
    return scriptedStream(locale, message, strategy.reason, startedAt);
  }

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const generator = strategy.run();
      let streamed = "";

      try {
        let step = await generator.next();
        while (!step.done) {
          streamed += step.value;
          controller.enqueue(encoder.encode(sse({ type: "token", value: step.value })));
          step = await generator.next();
        }

        const result = step.value;

        if (result.blocked) {
          // Verifier blocked twice. Replace what was streamed with the scripted
          // answer for this intent rather than let an invented figure stand.
          const node = scriptedReply(locale, message);
          controller.enqueue(encoder.encode(sse({ type: "replace", value: node.answer })));
          controller.enqueue(
            encoder.encode(sse({ type: "done", mode: "scripted", chips: node.chips ?? [] })),
          );
          controller.close();
          logRequest({
            locale,
            latencyMs: Date.now() - startedAt,
            inputTokens: result.inputTokens,
            outputTokens: result.outputTokens,
            cacheHit: result.cacheHit,
            fallback: "verifier-blocked",
            intent: intentFrom([], node.id),
          });
          return;
        }

        // The verified text may differ from what streamed (a dead source tag
        // stripped), so the final text is sent and the widget replaces with it.
        if (result.text !== streamed) {
          controller.enqueue(encoder.encode(sse({ type: "replace", value: result.text })));
        }

        for (const id of result.sources) {
          controller.enqueue(
            encoder.encode(sse({ type: "source", id, href: sourceHref(locale, id) })),
          );
        }
        controller.enqueue(encoder.encode(sse({ type: "done", mode: "model", chips: [] })));
        controller.close();

        logRequest({
          locale,
          latencyMs: Date.now() - startedAt,
          inputTokens: result.inputTokens,
          outputTokens: result.outputTokens,
          cacheHit: result.cacheHit,
          fallback: null,
          intent: intentFrom(result.sources),
        });
      } catch (error) {
        // Upstream failed, timed out or 429'd. The visitor still gets an answer.
        const reason = ((error as { reason?: FallbackReason }).reason ??
          "upstream-error") satisfies FallbackReason;
        const node = scriptedReply(locale, message);
        controller.enqueue(encoder.encode(sse({ type: "replace", value: node.answer })));
        controller.enqueue(
          encoder.encode(sse({ type: "done", mode: "scripted", chips: node.chips ?? [] })),
        );
        controller.close();
        logRequest({
          locale,
          latencyMs: Date.now() - startedAt,
          inputTokens: 0,
          outputTokens: 0,
          cacheHit: false,
          fallback: reason,
          intent: intentFrom([], node.id),
        });
      }
    },
  });

  return new Response(stream, { headers: headers() });
}
