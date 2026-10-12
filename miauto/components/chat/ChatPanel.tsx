"use client";

import clsx from "clsx";
import { ArrowUp, FileText, Phone, Square, ThumbsDown, ThumbsUp, X } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { site } from "@/config/miauto";
import { usePressHandlers } from "@/lib/motion";
import { stripSourceTags, useChat, type Turn } from "./useChat";
import type { Locale, LocaleContent } from "@/content/types";

export function ChatPanel({
  locale,
  t,
  open,
  onClose,
}: {
  locale: Locale;
  t: LocaleContent;
  open: boolean;
  onClose: () => void;
}) {
  const { turns, busy, mode, send, stop } = useChat(locale, t);
  const [draft, setDraft] = useState("");
  const [closing, setClosing] = useState(false);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);
  const press = usePressHandlers();

  const close = useCallback(() => {
    setClosing(true);
    window.setTimeout(() => {
      setClosing(false);
      onClose();
      // Focus returns to the launcher that opened the panel.
      document
        .querySelector<HTMLButtonElement>('button[aria-label][data-open="true"]')
        ?.focus();
    }, 200);
  }, [onClose]);

  // Focus moves into the panel on open; Escape closes; focus is trapped while open.
  useEffect(() => {
    if (!open) return;
    const node = panelRef.current;
    window.setTimeout(() => inputRef.current?.focus(), 60);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
        return;
      }
      if (event.key !== "Tab" || !node) return;
      const focusables = node.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), textarea, [tabindex]:not([tabindex="-1"])',
      );
      if (focusables.length === 0) return;
      const first = focusables[0] as HTMLElement;
      const last = focusables[focusables.length - 1] as HTMLElement;
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, close]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [turns]);

  if (!open && !closing) return null;

  const submit = (text: string) => {
    setDraft("");
    void send(text);
  };

  const lastAssistant = [...turns].reverse().find((turn) => turn.role === "assistant");
  const chips =
    turns.length === 0
      ? t.chat.starterChips
      : (lastAssistant?.chips?.length ?? 0) > 0 && !busy
        ? lastAssistant?.chips ?? []
        : [];

  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-modal="false"
      aria-label={t.chat.panelTitle}
      data-open={closing ? "false" : "true"}
      data-closing={closing ? "true" : "false"}
      className="overlay-enter fixed inset-x-3 bottom-3 z-50 flex max-h-[min(78dvh,620px)] flex-col overflow-hidden rounded-[var(--radius-card)] border border-[var(--border)] bg-[var(--bg)] shadow-[0_18px_60px_rgb(0_0_0/60%)] sm:inset-x-auto sm:right-6 sm:w-[400px] md:bottom-24"
    >
      <header className="flex items-start justify-between gap-3 border-b border-[var(--border)] px-5 py-4">
        <div>
          {/* States what it is. Not a human name, not a photo of a person. */}
          <p className="font-heading text-[1rem] font-semibold">{t.chat.panelTitle}</p>
          <p className="mt-0.5 text-[0.75rem] text-[color:var(--text-muted)]">
            {t.chat.panelSubtitle}
            {mode === "scripted" ? ` · ${t.chat.scriptedNotice}` : ""}
          </p>
        </div>
        <button
          type="button"
          onClick={close}
          aria-label={t.chat.close}
          className="tappable -mr-1.5 -mt-1 grid size-9 shrink-0 place-items-center rounded-[var(--radius-control)] text-[color:var(--text-muted)] hover:text-[color:var(--text)]"
          {...press}
        >
          <X size={18} aria-hidden="true" />
        </button>
      </header>

      {/* Always present, at every point in the conversation. */}
      <a
        href={site.phoneHref}
        aria-label={t.common.callAria}
        className="tappable flex items-center justify-center gap-2 border-b border-[var(--border)] bg-[var(--accent-soft)] px-5 py-2.5 text-[0.875rem] font-semibold text-[color:var(--accent)] no-underline"
        style={{ ["--press-scale" as string]: "0.99" }}
        {...press}
      >
        <Phone size={15} aria-hidden="true" />
        {t.common.callCta} {site.phone}
      </a>

      <div
        ref={listRef}
        className="flex-1 space-y-4 overflow-y-auto px-5 py-5"
        aria-live="polite"
        aria-atomic="false"
      >
        <p className="text-[0.9375rem] leading-relaxed text-[color:var(--text-muted)]">
          {t.chat.greeting}
        </p>

        {turns.map((turn) => (
          <Message key={turn.id} turn={turn} t={t} />
        ))}
      </div>

      {chips.length > 0 ? (
        <div className="border-t border-[var(--border)] px-5 py-3">
          <p className="mb-2 text-[0.6875rem] font-semibold uppercase tracking-[0.12em] text-[color:var(--text-muted)]">
            {t.chat.suggestedLabel}
          </p>
          <ul className="flex flex-wrap gap-2">
            {chips.map((chip) => (
              <li key={chip}>
                <button
                  type="button"
                  onClick={() => submit(chip)}
                  disabled={busy}
                  className="tappable rounded-[var(--radius-pill)] border border-[var(--border)] px-3 py-1.5 text-[0.8125rem] text-[color:var(--text)] hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))] disabled:opacity-50"
                  {...press}
                >
                  {chip}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          submit(draft);
        }}
        className="flex items-end gap-2 border-t border-[var(--border)] p-3"
      >
        <label htmlFor="miauto-chat-input" className="sr-only">
          {t.chat.inputLabel}
        </label>
        <textarea
          ref={inputRef}
          id="miauto-chat-input"
          rows={1}
          value={draft}
          maxLength={2000}
          placeholder={t.chat.inputPlaceholder}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submit(draft);
            }
          }}
          className="max-h-28 min-h-[44px] flex-1 resize-none rounded-[var(--radius-control)] border border-[var(--border)] bg-[var(--surface)] px-3.5 py-3 text-[0.9375rem] placeholder:text-[color:var(--text-muted)] focus:border-[var(--focus)] focus:outline-none focus:ring-[3px] focus:ring-[var(--accent-soft)]"
        />
        {busy ? (
          <button
            type="button"
            onClick={stop}
            aria-label={t.chat.stop}
            className="tappable grid size-11 shrink-0 place-items-center rounded-[var(--radius-control)] border border-[var(--border)] text-[color:var(--text)]"
            {...press}
          >
            <Square size={16} aria-hidden="true" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={draft.trim() === ""}
            aria-label={t.chat.send}
            className="tappable grid size-11 shrink-0 place-items-center rounded-[var(--radius-control)] bg-[var(--accent)] text-[color:var(--accent-ink)] disabled:bg-[var(--surface-hover)] disabled:text-[color:var(--text-muted)]"
            {...press}
          >
            <ArrowUp size={18} aria-hidden="true" />
          </button>
        )}
      </form>

      <p className="border-t border-[var(--border)] px-5 py-2 text-center text-[0.6875rem] text-[color:var(--text-muted)]">
        {t.chat.automatedBadge}
      </p>
    </div>
  );
}

function Message({ turn, t }: { turn: Turn; t: LocaleContent }) {
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  if (turn.role === "user") {
    return (
      <p className="ml-auto max-w-[85%] rounded-[var(--radius-card)] rounded-br-md bg-[var(--surface-hover)] px-4 py-2.5 text-[0.9375rem]">
        {turn.content}
      </p>
    );
  }

  const text = stripSourceTags(turn.content);

  return (
    <div className="max-w-[92%]">
      <p className="text-[0.9375rem] leading-relaxed">
        {text}
        {turn.streaming ? (
          <span
            aria-hidden="true"
            className="ml-0.5 inline-block h-[1.05em] w-[2px] translate-y-[0.15em] bg-[var(--accent)]"
          />
        ) : null}
      </p>

      {/* The highest-value element here: it makes every answer checkable and
          routes the visitor to the page the answer came from. */}
      {turn.sources && turn.sources.length > 0 ? (
        <ul className="mt-2.5 flex flex-wrap gap-1.5">
          {turn.sources.map((source) => (
            <li key={source.id}>
              <Link
                href={source.href}
                className="inline-flex items-center gap-1.5 rounded-[var(--radius-pill)] border border-[var(--border)] px-2.5 py-1 text-[0.75rem] text-[color:var(--text-muted)] no-underline hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))] hover:text-[color:var(--text)]"
              >
                <FileText size={12} aria-hidden="true" />
                <span className="sr-only">{t.chat.sourceLabel}: </span>
                {source.id}
              </Link>
            </li>
          ))}
        </ul>
      ) : null}

      {!turn.streaming && text !== "" ? (
        <div className="mt-2 flex items-center gap-1">
          {feedback ? (
            <span className="text-[0.75rem] text-[color:var(--text-muted)]">
              {t.chat.feedbackThanks}
            </span>
          ) : (
            <>
              <FeedbackButton
                label={t.chat.feedbackUp}
                onClick={() => {
                  setFeedback("up");
                  // Coarse signal plus the turn id. No message text.
                  console.log(`[chat-feedback] ${JSON.stringify({ id: turn.id, signal: "up" })}`);
                }}
              >
                <ThumbsUp size={13} aria-hidden="true" />
              </FeedbackButton>
              <FeedbackButton
                label={t.chat.feedbackDown}
                onClick={() => {
                  setFeedback("down");
                  console.log(`[chat-feedback] ${JSON.stringify({ id: turn.id, signal: "down" })}`);
                }}
              >
                <ThumbsDown size={13} aria-hidden="true" />
              </FeedbackButton>
            </>
          )}
        </div>
      ) : null}
    </div>
  );
}

function FeedbackButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={clsx(
        "grid size-7 place-items-center rounded-[var(--radius-control)]",
        "text-[color:var(--text-muted)] hover:text-[color:var(--text)]",
      )}
    >
      {children}
    </button>
  );
}
