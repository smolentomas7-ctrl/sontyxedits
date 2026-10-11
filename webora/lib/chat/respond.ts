/**
 * ============================================================
 * CHAT RESPONSE LOGIC — the one place answers are decided
 * ============================================================
 *
 * Today this matches the visitor's text against keyword sets defined in
 * content/chat/{sk,en}.ts and returns a scripted answer. It is deliberately
 * the only module that decides what the assistant says, so it can be swapped
 * for a real model without touching the UI.
 *
 * TO CALL A REAL LLM INSTEAD:
 *
 * Make respond() async and call your own API route from it — never call a
 * model provider directly from the browser, because that would expose the
 * API key. Create app/api/chat/route.ts that forwards to the provider with
 * the key from the server environment, then:
 *
 *   export async function respond(input: string, script: ChatScript) {
 *     const res = await fetch("/api/chat", {
 *       method: "POST",
 *       headers: { "Content-Type": "application/json" },
 *       body: JSON.stringify({ message: input }),
 *     });
 *     if (!res.ok) return { node: script.fallback, matched: false };
 *     const { answer } = await res.json();
 *     return { node: { ...script.fallback, answer }, matched: true };
 *   }
 *
 * The widget already renders answers as plain text and announces them in a
 * live region, so only this function changes. Keep the header disclosure
 * stating that the assistant is automated.
 */

import type { ChatNode, ChatScript } from "@/content/chat/types";

export type ChatResponse = {
  node: ChatNode;
  /** False when nothing matched and the fallback is being used. */
  matched: boolean;
};

/** Strips diacritics so "cena" matches "cenník" and "koľko" matches "kolko". */
function normalize(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .trim();
}

export function respond(input: string, script: ChatScript): ChatResponse {
  const haystack = normalize(input);

  if (haystack.length === 0) {
    return { node: script.fallback, matched: false };
  }

  let best: { node: ChatNode; score: number } | null = null;

  for (const node of Object.values(script.nodes)) {
    if (!node.keywords) continue;

    let score = 0;
    for (const keyword of node.keywords) {
      const needle = normalize(keyword);
      if (needle.length > 0 && haystack.includes(needle)) {
        // Longer keyword matches are more specific, so weight them higher.
        score += needle.length;
      }
    }

    if (score > 0 && (best === null || score > best.score)) {
      best = { node, score };
    }
  }

  if (best === null) {
    return { node: script.fallback, matched: false };
  }

  return { node: best.node, matched: true };
}

/** Looks up a node by id, used when a suggestion chip is clicked. */
export function respondToNodeId(id: string, script: ChatScript): ChatResponse {
  const node = script.nodes[id];
  if (!node) return { node: script.fallback, matched: false };
  return { node, matched: true };
}
