import { Mail, ArrowUpRight } from "lucide-react";
import { WhatsAppIcon } from "@/components/ui/WhatsAppIcon";
import { siteConfig, mailtoHref } from "@/config/site";
import type { Dictionary } from "@/content/i18n";
import { cn } from "@/lib/utils";

/**
 * The only two ways to reach Webora.
 *
 * There is no contact form anywhere on the site, so these two links are the
 * whole funnel — both are real, working links, never a button that opens
 * nothing. E-mail carries the house accent; WhatsApp uses its own green,
 * which is the point of it being recognisable, but only on the button itself.
 */
export function ContactOptions({
  dict,
  subject,
  className,
}: {
  dict: Dictionary;
  /** Prefills the mail draft's subject line. */
  subject?: string;
  className?: string;
}) {
  const t = dict.contact;

  return (
    <div className={cn("grid gap-4 sm:grid-cols-2", className)}>
      {/* ---------- e-mail ---------- */}
      <a
        href={mailtoHref(subject ?? t.mailSubject)}
        className={cn(
          "group/contact flex flex-col gap-3 rounded-2xl border border-accent/25 bg-accent-soft p-6",
          "transition-[transform,border-color,background-color] duration-200 ease-[cubic-bezier(0.32,0.72,0,1)]",
          "hover:border-accent/50 active:scale-[0.99] active:duration-75",
          "motion-reduce:transition-none motion-reduce:active:scale-100",
        )}
      >
        <span className="flex items-center gap-2.5">
          <Mail aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0 text-accent" />
          <span className="t-small font-medium uppercase tracking-[0.12em] text-text-muted">
            {t.emailLabel}
          </span>
        </span>

        <span className="break-all text-[17px] font-medium text-text">{siteConfig.email}</span>

        <span className="mt-1 inline-flex items-center gap-1.5 text-[15px] font-medium text-accent">
          {t.emailCta}
          <ArrowUpRight
            aria-hidden="true"
            strokeWidth={1.5}
            className="size-4 transition-transform duration-200 group-hover/contact:translate-x-0.5 group-hover/contact:-translate-y-0.5 motion-reduce:transition-none"
          />
        </span>
      </a>

      {/* ---------- WhatsApp ---------- */}
      <a
        href={siteConfig.whatsapp.href}
        target="_blank"
        rel="noopener noreferrer"
        // No aria-label here: the card's own text ("WhatsApp", the number and
        // the call to action) already names it, and an aria-label that did not
        // contain that visible text in order broke WCAG 2.5.3 — a voice-control
        // user saying what they can see would not have matched the link.
        className={cn(
          "group/contact flex flex-col gap-3 rounded-2xl border border-[#25D366]/30 bg-[#25D366]/8 p-6",
          "transition-[transform,border-color,background-color] duration-200 ease-[cubic-bezier(0.32,0.72,0,1)]",
          "hover:border-[#25D366]/60 active:scale-[0.99] active:duration-75",
          "motion-reduce:transition-none motion-reduce:active:scale-100",
        )}
      >
        <span className="flex items-center gap-2.5">
          <WhatsAppIcon className="size-5 shrink-0 text-[#4AE08A]" />
          <span className="t-small font-medium uppercase tracking-[0.12em] text-text-muted">
            {t.whatsappLabel}
          </span>
        </span>

        <span className="text-[17px] font-medium text-text">{siteConfig.whatsapp.display}</span>

        <span className="mt-1 inline-flex items-center gap-1.5 text-[15px] font-medium text-[#4AE08A]">
          {t.whatsappCta}
          <ArrowUpRight
            aria-hidden="true"
            strokeWidth={1.5}
            className="size-4 transition-transform duration-200 group-hover/contact:translate-x-0.5 group-hover/contact:-translate-y-0.5 motion-reduce:transition-none"
          />
        </span>
      </a>
    </div>
  );
}

/**
 * The same two destinations as a pair of buttons, for use inside a CTA band
 * where the card treatment would be too heavy.
 */
export function ContactButtons({
  dict,
  subject,
  className,
}: {
  dict: Dictionary;
  subject?: string;
  className?: string;
}) {
  const t = dict.contact;
  const base =
    "inline-flex h-[52px] select-none items-center justify-center gap-2 rounded-xl px-7 text-[16px] font-medium " +
    "transition-[transform,background-color,border-color,box-shadow] duration-150 ease-[cubic-bezier(0.32,0.72,0,1)] " +
    "active:scale-[0.97] active:duration-75 motion-reduce:transition-none motion-reduce:active:scale-100";

  return (
    <div className={cn("flex flex-col gap-3 sm:flex-row", className)}>
      <a
        href={mailtoHref(subject ?? t.mailSubject)}
        className={cn(
          base,
          "bg-accent text-[#06112E] shadow-[0_1px_0_rgba(255,255,255,0.25)_inset,0_6px_18px_-8px_rgba(91,141,255,0.9)]",
          "hover:bg-accent-hover",
        )}
      >
        <Mail aria-hidden="true" strokeWidth={1.5} className="size-4" />
        {t.emailCta}
      </a>

      <a
        href={siteConfig.whatsapp.href}
        target="_blank"
        rel="noopener noreferrer"
        aria-label={`${t.whatsappCta} — ${siteConfig.whatsapp.display}`}
        className={cn(base, "border border-[#25D366]/40 bg-[#25D366]/10 text-text hover:bg-[#25D366]/18")}
      >
        <WhatsAppIcon className="size-4 text-[#4AE08A]" />
        {t.whatsappCta}
      </a>
    </div>
  );
}
