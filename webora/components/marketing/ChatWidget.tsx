"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { MessageCircle, X, Send, Info } from "lucide-react";
import { respond, respondToNodeId } from "@/lib/chat/respond";
import { chatSk } from "@/content/chat/sk";
import { chatEn } from "@/content/chat/en";
import type { ChatScript } from "@/content/chat/types";
import type { Dictionary, Locale } from "@/content/i18n";
import { cn } from "@/lib/utils";

type Message = {
  id: number;
  from: "bot" | "user";
  text: string;
};

export function ChatWidget({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const script: ChatScript = locale === "sk" ? chatSk : chatEn;

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { id: 0, from: "bot", text: dict.chat.greeting },
  ]);
  const [suggestions, setSuggestions] = useState<string[]>(script.initialSuggestions);
  const [showContact, setShowContact] = useState(false);

  const nextId = useRef(1);
  const panelRef = useRef<HTMLDivElement>(null);
  const launcherRef = useRef<HTMLButtonElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const logRef = useRef<HTMLDivElement>(null);

  // Move focus into the panel on open, and back to the launcher on close.
  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
    } else {
      // Avoid stealing focus on first render, before the widget was ever open.
      if (nextId.current > 1) launcherRef.current?.focus();
    }
  }, [open]);

  // Escape closes the panel.
  useEffect(() => {
    if (!open) return;
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        setOpen(false);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  // Keep the newest message in view.
  useEffect(() => {
    const log = logRef.current;
    if (log) log.scrollTop = log.scrollHeight;
  }, [messages]);

  function push(from: "bot" | "user", text: string) {
    setMessages((previous) => [...previous, { id: nextId.current++, from, text }]);
  }

  function handleResponse(userText: string, result: ReturnType<typeof respond>) {
    push("user", userText);
    push("bot", result.node.answer);
    setSuggestions(result.node.followUps);
    setShowContact(result.node.offerContact);
  }

  function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (text.length === 0) return;
    handleResponse(text, respond(text, script));
    setInput("");
  }

  function onSuggestion(id: string) {
    const node = script.nodes[id];
    if (!node) return;
    handleResponse(node.label ?? id, respondToNodeId(id, script));
  }

  return (
    <>
      <button
        ref={launcherRef}
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={open ? dict.chat.close : dict.chat.launcherLabel}
        aria-expanded={open}
        className={cn(
          "fixed bottom-5 right-5 z-[80] inline-flex size-14 items-center justify-center",
          "rounded-full bg-accent text-[#06112E] shadow-lg shadow-black/40",
          "transition-[transform,background-color] duration-150 hover:bg-accent-hover hover:scale-105",
        )}
      >
        {open ? (
          <X aria-hidden="true" strokeWidth={1.5} className="size-6" />
        ) : (
          <MessageCircle aria-hidden="true" strokeWidth={1.5} className="size-6" />
        )}
      </button>

      {open ? (
        <div
          ref={panelRef}
          role="dialog"
          aria-label={dict.chat.title}
          className={cn(
            "fixed bottom-24 right-5 z-[80] flex max-h-[min(560px,calc(100vh-7.5rem))] w-[min(380px,calc(100vw-2.5rem))]",
            "flex-col overflow-hidden rounded-2xl border border-border bg-surface shadow-2xl shadow-black/50",
          )}
        >
          <div className="border-b border-border px-4 py-3">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[15px] font-medium text-text">
              {dict.chat.title}
            </p>
            <p className="t-small text-text-muted">{dict.chat.subtitle}</p>
          </div>

          <p className="flex gap-2 border-b border-border bg-bg/40 px-4 py-2.5 text-[12px] leading-relaxed text-text-muted">
            <Info aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-3.5 shrink-0" />
            {dict.chat.automatedNotice}
          </p>

          <div
            ref={logRef}
            role="log"
            aria-live="polite"
            aria-atomic="false"
            className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4"
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "max-w-[85%] rounded-xl px-3.5 py-2.5 text-[14px] leading-relaxed",
                  message.from === "bot"
                    ? "self-start bg-bg text-text-muted"
                    : "self-end bg-accent-soft text-text",
                )}
              >
                <span className="sr-only">
                  {message.from === "bot" ? dict.chat.botName : dict.chat.youName}:{" "}
                </span>
                {message.text}
              </div>
            ))}

            {showContact ? (
              <Link
                href={`/${locale}/contact`}
                onClick={() => setOpen(false)}
                className="self-start rounded-lg border border-accent/35 px-3 py-1.5 text-[13px] font-medium text-accent transition-colors duration-150 hover:bg-accent-soft"
              >
                {dict.chat.goToContact}
              </Link>
            ) : null}
          </div>

          {suggestions.length > 0 ? (
            <div className="border-t border-border px-4 py-3">
              <p className="sr-only" id="chat-suggestions-label">
                {dict.chat.suggestionsLabel}
              </p>
              <ul aria-labelledby="chat-suggestions-label" className="flex flex-wrap gap-2">
                {suggestions.map((id) => {
                  const node = script.nodes[id];
                  if (!node?.label) return null;
                  return (
                    <li key={id}>
                      <button
                        type="button"
                        onClick={() => onSuggestion(id)}
                        className="rounded-full border border-border px-3 py-1.5 text-[13px] text-text-muted transition-colors duration-150 hover:border-accent/40 hover:text-text"
                      >
                        {node.label}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}

          <form onSubmit={onSubmit} className="flex items-center gap-2 border-t border-border p-3">
            <label htmlFor="chat-input" className="sr-only">
              {dict.chat.inputLabel}
            </label>
            <input
              ref={inputRef}
              id="chat-input"
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={dict.chat.inputPlaceholder}
              autoComplete="off"
              className="h-10 flex-1 rounded-lg border border-border bg-bg px-3 text-[14px] text-text placeholder:text-text-muted/80 focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
            />
            <button
              type="submit"
              aria-label={dict.chat.send}
              disabled={input.trim().length === 0}
              className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg bg-accent text-[#06112E] transition-colors duration-150 hover:bg-accent-hover disabled:opacity-40"
            >
              <Send aria-hidden="true" strokeWidth={1.5} className="size-4" />
            </button>
          </form>
        </div>
      ) : null}
    </>
  );
}
