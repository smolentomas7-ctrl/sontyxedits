import clsx from "clsx";

/**
 * A value the client still has to supply, rendered VISIBLY with its square
 * brackets intact so it cannot ship unnoticed. Two flavours: `token` for a short
 * inline value like [EMAIL], `block` for a paragraph of copy that does not exist yet.
 */
export function PlaceholderToken({
  children,
  className,
}: {
  children: string;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-[var(--radius-pill)] border border-dashed",
        "border-[var(--border)] bg-[var(--surface)] px-2 py-0.5",
        "font-mono text-[0.8125rem] text-[color:var(--text-muted)]",
        className,
      )}
    >
      {children}
    </span>
  );
}

export function PlaceholderBlock({
  children,
  label,
  className,
}: {
  children: string;
  label: string;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "rounded-[var(--radius-card)] border border-dashed border-[var(--border)]",
        "bg-[var(--surface)] p-5 md:p-6",
        className,
      )}
    >
      <p className="mb-2 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--text-muted)]">
        {label}
      </p>
      <p className="font-mono text-[0.9375rem] text-[color:var(--text-muted)]">{children}</p>
    </div>
  );
}

/** A `[TO CONFIRM: …]` marker for a service scope the client has not confirmed. */
export function ToConfirm({
  items,
  label,
}: {
  items: readonly string[];
  label: string;
}) {
  if (items.length === 0) return null;
  return (
    <div className="rounded-[var(--radius-card)] border border-dashed border-[color-mix(in_srgb,var(--accent)_40%,var(--border))] bg-[var(--accent-soft)] p-5 md:p-6">
      <p className="mb-3 flex items-center gap-2 text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-[color:var(--accent)]">
        {label}
      </p>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="font-mono text-[0.875rem] leading-relaxed text-[color:var(--text)]">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
