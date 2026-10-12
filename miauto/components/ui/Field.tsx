import clsx from "clsx";
import type { ReactNode } from "react";

/**
 * Label above the input, error below it and tied with aria-describedby, border
 * in --danger when invalid. The error is never signalled by colour alone — it is
 * a sentence of text.
 */
export function Field({
  id,
  label,
  hint,
  error,
  optional,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  optional?: string;
  children: (props: {
    id: string;
    "aria-describedby": string | undefined;
    "aria-invalid": boolean | undefined;
    className: string;
  }) => ReactNode;
}) {
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const describedBy =
    [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(" ") || undefined;

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-[0.875rem] text-[color:var(--text-muted)]">
        {label}
        {optional ? (
          <span className="ml-2 text-[color:var(--text-muted)] opacity-80">({optional})</span>
        ) : null}
      </label>

      {children({
        id,
        "aria-describedby": describedBy,
        "aria-invalid": error ? true : undefined,
        className: clsx(inputClasses, error && "border-[var(--danger)]"),
      })}

      {hint && !error ? (
        <p id={hintId} className="text-[0.8125rem] text-[color:var(--text-muted)]">
          {hint}
        </p>
      ) : null}

      {error ? (
        <p id={errorId} className="text-[0.8125rem] font-medium text-[color:var(--danger)]">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export const inputClasses = clsx(
  "h-[52px] w-full rounded-[var(--radius-control)] border border-[var(--border)]",
  "bg-[var(--surface)] px-4 text-[color:var(--text)]",
  "placeholder:text-[color:color-mix(in_srgb,var(--text-muted)_80%,transparent)]",
  "transition-[border-color,box-shadow] duration-[var(--dur-state)] ease-[var(--ease-ios-in)]",
  "focus:border-[var(--focus)] focus:outline-none focus:ring-[3px] focus:ring-[var(--accent-soft)]",
  "read-only:opacity-60",
);

export const textareaClasses = clsx(
  "min-h-[160px] w-full resize-y rounded-[var(--radius-control)] border border-[var(--border)]",
  "bg-[var(--surface)] p-4 text-[color:var(--text)]",
  "placeholder:text-[color:color-mix(in_srgb,var(--text-muted)_80%,transparent)]",
  "transition-[border-color,box-shadow] duration-[var(--dur-state)] ease-[var(--ease-ios-in)]",
  "focus:border-[var(--focus)] focus:outline-none focus:ring-[3px] focus:ring-[var(--accent-soft)]",
  "read-only:opacity-60",
);
