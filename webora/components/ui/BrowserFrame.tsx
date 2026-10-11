import { cn } from "@/lib/utils";

/**
 * Chrome around a demo preview image. Decorative — the dots and the address
 * bar are hidden from assistive technology, and the label is rendered as
 * plain text rather than a fake input so it is never mistaken for one.
 */
export function BrowserFrame({
  url,
  children,
  className,
}: {
  url: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-border bg-[#0F0F12]",
        className,
      )}
    >
      <div
        aria-hidden="true"
        className="flex items-center gap-2 border-b border-border bg-[#17171B] px-3 py-2"
      >
        <span className="flex gap-1.5">
          <span className="size-2.5 rounded-full bg-[#2E2E36]" />
          <span className="size-2.5 rounded-full bg-[#2E2E36]" />
          <span className="size-2.5 rounded-full bg-[#2E2E36]" />
        </span>
        <span className="ml-1 flex-1 truncate rounded-md bg-[#0F0F12] px-2.5 py-1 text-[11px] text-text-muted">
          {url}
        </span>
      </div>
      {children}
    </div>
  );
}
