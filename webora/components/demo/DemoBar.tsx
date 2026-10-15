import Link from "next/link";
import { ArrowLeft, ArrowUpRight } from "lucide-react";
import { Wordmark } from "@/components/ui/Logo";

/**
 * Fixed frame above every demo site's own header, so a visitor always knows
 * they are looking at a Webora demo and can get back. Deliberately styled
 * apart from the demo beneath it: near-black bar, thin bottom border, small
 * type — it should read as chrome, not as part of the site.
 *
 * Demo layouts add padding-top equal to DEMO_BAR_HEIGHT so the bar never
 * covers the demo's own fixed header.
 */

export const DEMO_BAR_HEIGHT = 44;

/** What the demo demonstrates. Drives the prefilled project type on contact. */
export type DemoKind = "info" | "eshop" | "gallery";

/**
 * Must match an entry in `contact.projectTypes` in content/i18n/sk.ts —
 * the contact form only accepts a prefill it recognises, so a typo here
 * silently falls back to an empty select rather than breaking.
 */
const PROJECT_TYPE: Record<DemoKind, string> = {
  info: "Informačný web pre firmu",
  eshop: "E-shop",
  gallery: "Galerijný web alebo portfólio",
};

export function DemoBar({ kind }: { kind: DemoKind }) {
  return (
    <div
      className="fixed inset-x-0 top-0 z-[90] border-b border-white/10 bg-[#0A0A0B] text-[#F4F4F5]"
      style={{ height: DEMO_BAR_HEIGHT }}
    >
      <div className="mx-auto flex h-full max-w-[1400px] items-center justify-between gap-4 px-4">
        <div className="flex min-w-0 items-center gap-3">
          <Wordmark markColor="#5B8DFF" textColor="#F4F4F5" />
          <span className="hidden truncate text-[12px] text-[#9A9AA5] sm:inline">
            Demo website by Webora
          </span>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/sk/portfolio"
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/15 px-2.5 py-1.5 text-[12px] text-[#F4F4F5] transition-colors duration-150 hover:bg-white/10"
          >
            <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
            <span className="hidden sm:inline">Späť na portfólio</span>
            <span className="sm:hidden">Späť</span>
          </Link>
          <Link
            href={`/sk/contact?type=${encodeURIComponent(PROJECT_TYPE[kind])}`}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#5B8DFF] px-2.5 py-1.5 text-[12px] font-medium text-[#06112E] transition-colors duration-150 hover:bg-[#3B74FF]"
          >
            <span className="hidden sm:inline">Chcem takýto web</span>
            <span className="sm:hidden">Mám záujem</span>
            <ArrowUpRight aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
