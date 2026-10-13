"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * A static export has no server, so there is no /api/chat to call. In that build
 * the scripted tier runs here in the browser instead — it is pure functions over
 * the same content the pages render, with no key and nothing to hide. The
 * grounded tier is genuinely unavailable in that mode, and the panel header says
 * the answers are prepared in advance.
 *
 * This is lazily imported so it only reaches the bundle of the build that needs
 * it, and only once the visitor opens the panel.
 */
const STATIC_CHAT = process.env.NEXT_PUBLIC_STATIC_CHAT === "1";

async function answerLocally(locale: Locale, message: string) {
  const [{ respondScripted }, { SOURCES }] = await Promise.all([
    import("@/lib/chat/scripted"),
    import("@/content/knowledge.generated"),
  ]);
  const node = respondScripted(locale, message);
  const sources: Source[] = [];
  for (const match of node.answer.matchAll(/\[source:\s*([^\]]+)\]/gi)) {
    const id = (match[1] ?? "").trim();
    const href = SOURCES[locale][id];
    if (href && !sources.some((s) => s.id === id)) sources.push({ id, href });
  }
  return { content: node.answer, sources, chips: [...(node.chips ?? [])] };
}

export type Source = { id: string; href: string };

export type Turn = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  chips?: string[];
  streaming?: boolean;
  /**
   * Which tier answered. A scripted answer says so under itself: the widget
   * never lets a fallback pass for the grounded assistant.
   */
  scripted?: boolean;
};

const STORAGE_KEY = "miauto-chat";

/**
 * The transcript lives in sessionStorage only: it is gone when the tab closes,
 * it is never written to localStorage, never persisted server-side, and never
 * sent to analytics. Every access is wrapped — storage can throw in private mode.
 */
function load(): Turn[] {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Turn[]) : [];
  } catch {
    return [];
  }
}

function save(turns: Turn[]): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(turns.slice(-20)));
  } catch {
    // Private mode or blocked storage: the conversation just will not survive
    // a reload, which is not worth surfacing to the visitor.
  }
}

export function clearStored(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* nothing to clean up */
  }
}

export function useChat(locale: Locale, t: LocaleContent) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState<"model" | "scripted" | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => setTurns(load()), []);
  useEffect(() => {
    if (turns.length > 0) save(turns);
  }, [turns]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setBusy(false);
    setTurns((previous) =>
      previous.map((turn) => (turn.streaming ? { ...turn, streaming: false } : turn)),
    );
  }, []);

  const send = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (message === "" || busy) return;

      const userTurn: Turn = { id: `u${Date.now()}`, role: "user", content: message };
      const assistantId = `a${Date.now()}`;
      const history = turns.map(({ role, content }) => ({ role, content }));

      setTurns((previous) => [
        ...previous,
        userTurn,
        { id: assistantId, role: "assistant", content: "", streaming: true },
      ]);
      setBusy(true);

      const controller = new AbortController();
      abortRef.current = controller;

      const patch = (fn: (turn: Turn) => Turn) =>
        setTurns((previous) =>
          previous.map((turn) => (turn.id === assistantId ? fn(turn) : turn)),
        );

      try {
        if (STATIC_CHAT) {
          const reply = await answerLocally(locale, message);
          setMode("scripted");
          patch((turn) => ({ ...turn, ...reply, streaming: false }));
          return;
        }

        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            locale,
            message,
            history: history.slice(-12),
            turnCount: turns.filter((turn) => turn.role === "assistant").length,
          }),
          signal: controller.signal,
        });

        if (!response.ok || !response.body) throw new Error("request failed");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const frames = buffer.split("\n\n");
          buffer = frames.pop() ?? "";

          for (const frame of frames) {
            const line = frame.trim();
            if (!line.startsWith("data:")) continue;
            const event = JSON.parse(line.slice(5).trim()) as
              | { type: "token"; value: string }
              | { type: "replace"; value: string }
              | { type: "source"; id: string; href: string }
              | { type: "done"; mode: "model" | "scripted"; chips: string[] }
              | { type: "error"; message: string };

            if (event.type === "token") {
              patch((turn) => ({ ...turn, content: turn.content + event.value }));
            } else if (event.type === "replace") {
              // The reply was withdrawn mid-stream: discard what streamed and
              // show this instead, rather than leaving an invented figure on screen.
              patch((turn) => ({ ...turn, content: event.value, sources: [] }));
            } else if (event.type === "source") {
              patch((turn) => ({
                ...turn,
                sources: [...(turn.sources ?? []), { id: event.id, href: event.href }],
              }));
            } else if (event.type === "done") {
              setMode(event.mode);
              patch((turn) => ({
                ...turn,
                streaming: false,
                chips: event.chips,
                scripted: event.mode === "scripted",
              }));
            } else {
              patch((turn) => ({ ...turn, content: t.chat.errorMessage, streaming: false }));
            }
          }
        }

        patch((turn) => ({ ...turn, streaming: false }));
      } catch (error) {
        if ((error as Error).name === "AbortError") {
          patch((turn) => ({ ...turn, streaming: false }));
        } else {
          // One sentence and the phone number. Never a code, never a raw message.
          patch((turn) => ({ ...turn, content: t.chat.errorMessage, streaming: false }));
        }
      } finally {
        setBusy(false);
        abortRef.current = null;
      }
    },
    [busy, locale, t.chat.errorMessage, turns],
  );

  return { turns, busy, mode, send, stop };
}

/** Source tags are rendered as chips, so they come out of the prose. */
export function stripSourceTags(text: string): string {
  return text.replace(/\s*\[source:\s*[^\]]+\]/gi, "").trim();
}
