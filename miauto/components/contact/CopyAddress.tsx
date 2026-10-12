"use client";

import { Check, Copy } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { formattedAddress } from "@/config/miauto";
import { usePressHandlers } from "@/lib/motion";
import type { LocaleContent } from "@/content/types";

export function CopyAddress({ t }: { t: LocaleContent }) {
  const [copied, setCopied] = useState(false);
  const timer = useRef<number | null>(null);
  const press = usePressHandlers();

  useEffect(() => () => {
    if (timer.current) window.clearTimeout(timer.current);
  }, []);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(formattedAddress);
      setCopied(true);
      if (timer.current) window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setCopied(false), 2400);
    } catch {
      // Clipboard denied or unavailable: the address is right there as text, so
      // there is nothing to recover from and nothing worth alarming anyone about.
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={copy}
        className="tappable inline-flex h-9 items-center gap-2 rounded-[var(--radius-pill)] border border-[var(--border)] px-3 text-[0.8125rem] font-medium text-[color:var(--text-muted)] hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))] hover:text-[color:var(--text)]"
        {...press}
      >
        {copied ? (
          <Check size={15} aria-hidden="true" className="text-[color:var(--success)]" />
        ) : (
          <Copy size={15} aria-hidden="true" />
        )}
        {copied ? t.common.addressCopied : t.common.copyAddress}
      </button>
      {/* Announced rather than signalled by the icon alone. */}
      <span role="status" aria-live="polite" className="sr-only">
        {copied ? t.common.addressCopied : ""}
      </span>
    </>
  );
}
