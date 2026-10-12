import type { Locale } from "@/content/types";

export type Role = "user" | "assistant";

export type ChatMessage = {
  readonly role: Role;
  readonly content: string;
};

/** A scripted answer. Tier 1 is built first and is the fallback for everything. */
export type Node = {
  readonly id: string;
  readonly answer: string;
  readonly chips?: readonly string[];
  readonly keywords?: readonly string[];
  readonly cta?: "phone" | "form" | "services";
  /**
   * Wins a score tie. Refusals and the authorisation question carry it, so
   * "how much is a timing belt" refuses the price instead of describing timing
   * belts, and "are you an authorised VW centre" answers about independence
   * instead of about electrics.
   */
  readonly priority?: boolean;
};

export type ChatRequest = {
  readonly locale: Locale;
  readonly message: string;
  readonly history: readonly ChatMessage[];
};

/** Why a reply came from the scripted tier instead of the model. */
export type FallbackReason =
  | "no-api-key"
  | "over-budget"
  | "upstream-error"
  | "rate-limited"
  | "timeout"
  | "verifier-blocked"
  | "turn-limit";

export type SseEvent =
  | { readonly type: "token"; readonly value: string }
  /**
   * Discard everything streamed so far and show this text instead. Used when a
   * reply has to be withdrawn mid-stream (the verifier blocked it, or upstream
   * failed). It is a distinct event rather than an in-band sentinel inside a
   * token, because a control character embedded in the text can be stripped in
   * transport and would then render as literal text in the panel.
   */
  | { readonly type: "replace"; readonly value: string }
  | { readonly type: "source"; readonly id: string; readonly href: string }
  | { readonly type: "done"; readonly mode: "model" | "scripted"; readonly chips: readonly string[] }
  | { readonly type: "error"; readonly message: string };
