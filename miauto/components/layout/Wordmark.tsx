import clsx from "clsx";
import { site } from "@/config/miauto";

/**
 * Text wordmark. Asset slot 1.1 (a logo file) was never supplied, so the brand
 * is set in type rather than approximated with a drawn mark that is not theirs.
 * Dropping in a real logo means replacing this component only.
 */
export function Wordmark({ className }: { className?: string }) {
  return (
    <span
      className={clsx(
        "font-heading text-[1.0625rem] font-700 tracking-[-0.03em] md:text-[1.125rem]",
        className,
      )}
      style={{ fontWeight: 700 }}
    >
      M.I.<span className="text-[color:var(--accent)]">Auto</span>
      <span className="ml-1 text-[0.6875rem] font-medium tracking-normal text-[color:var(--text-muted)]">
        s.r.o.
      </span>
      <span className="sr-only"> — {site.city}</span>
    </span>
  );
}
