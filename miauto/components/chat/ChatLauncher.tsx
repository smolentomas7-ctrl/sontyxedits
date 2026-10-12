"use client";

import { MessageSquare } from "lucide-react";
import dynamic from "next/dynamic";
import { useState } from "react";
import { usePressHandlers } from "@/lib/motion";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * The panel is a separate chunk, pulled in on the first interaction with the
 * launcher. Nothing of the widget beyond this button is in the initial bundle.
 */
const ChatPanel = dynamic(() => import("./ChatPanel").then((m) => m.ChatPanel), {
  ssr: false,
});

export function ChatLauncher({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);
  const press = usePressHandlers();

  return (
    <>
      <button
        type="button"
        aria-label={t.chat.launcherLabel}
        aria-expanded={open}
        onPointerEnter={() => setMounted(true)}
        onFocus={() => setMounted(true)}
        onClick={() => {
          setMounted(true);
          setOpen(true);
        }}
        {...press}
        className="tappable fixed right-4 z-50 grid size-14 place-items-center rounded-full bg-[var(--surface)] text-[color:var(--text)] shadow-[0_6px_24px_rgb(0_0_0/45%)] ring-1 ring-[var(--border)] hover:bg-[var(--surface-hover)] md:right-6 md:bottom-6"
        // Above the mobile call bar, so neither covers the other.
        style={{ bottom: "calc(76px + env(safe-area-inset-bottom))" }}
        data-open={open ? "true" : "false"}
      >
        <MessageSquare size={22} aria-hidden="true" />
      </button>

      {mounted ? (
        <ChatPanel locale={locale} t={t} open={open} onClose={() => setOpen(false)} />
      ) : null}
    </>
  );
}
