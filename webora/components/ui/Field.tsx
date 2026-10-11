"use client";

import { useId } from "react";
import { cn } from "@/lib/utils";

const controlBase =
  "w-full rounded-[10px] border bg-surface px-4 text-[15px] text-text " +
  "placeholder:text-text-muted/60 transition-colors duration-150 " +
  "focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/35";

function Shell({
  label,
  htmlFor,
  error,
  errorId,
  hint,
  hintId,
  optionalLabel,
  required,
  children,
}: {
  label: string;
  htmlFor: string;
  error?: string;
  errorId: string;
  hint?: string;
  hintId: string;
  optionalLabel?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={htmlFor} className="t-small font-medium text-text">
        {label}
        {!required && optionalLabel ? (
          <span className="ml-1.5 font-normal text-text-muted">({optionalLabel})</span>
        ) : null}
      </label>
      {children}
      {hint ? (
        <p id={hintId} className="text-[13px] text-text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-[13px] text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}

/** Builds the aria-describedby value from whichever helper nodes exist. */
function describedBy(error: string | undefined, errorId: string, hint: string | undefined, hintId: string) {
  const ids = [error ? errorId : null, hint ? hintId : null].filter(Boolean);
  return ids.length > 0 ? ids.join(" ") : undefined;
}

export function TextField({
  label,
  error,
  hint,
  optionalLabel,
  className,
  ...props
}: {
  label: string;
  error?: string;
  hint?: string;
  optionalLabel?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  const generated = useId();
  const id = props.id ?? generated;
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <Shell
      label={label}
      htmlFor={id}
      error={error}
      errorId={errorId}
      hint={hint}
      hintId={hintId}
      optionalLabel={optionalLabel}
      required={props.required}
    >
      <input
        {...props}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error, errorId, hint, hintId)}
        className={cn(
          controlBase,
          "h-12",
          error ? "border-danger" : "border-border",
          className,
        )}
      />
    </Shell>
  );
}

export function TextArea({
  label,
  error,
  hint,
  optionalLabel,
  className,
  ...props
}: {
  label: string;
  error?: string;
  hint?: string;
  optionalLabel?: string;
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const generated = useId();
  const id = props.id ?? generated;
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <Shell
      label={label}
      htmlFor={id}
      error={error}
      errorId={errorId}
      hint={hint}
      hintId={hintId}
      optionalLabel={optionalLabel}
      required={props.required}
    >
      <textarea
        {...props}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error, errorId, hint, hintId)}
        className={cn(
          controlBase,
          "min-h-[140px] resize-y py-3 leading-relaxed",
          error ? "border-danger" : "border-border",
          className,
        )}
      />
    </Shell>
  );
}

export function SelectField({
  label,
  error,
  hint,
  optionalLabel,
  options,
  placeholder,
  className,
  ...props
}: {
  label: string;
  error?: string;
  hint?: string;
  optionalLabel?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
} & React.SelectHTMLAttributes<HTMLSelectElement>) {
  const generated = useId();
  const id = props.id ?? generated;
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;

  return (
    <Shell
      label={label}
      htmlFor={id}
      error={error}
      errorId={errorId}
      hint={hint}
      hintId={hintId}
      optionalLabel={optionalLabel}
      required={props.required}
    >
      <select
        {...props}
        id={id}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy(error, errorId, hint, hintId)}
        className={cn(
          controlBase,
          "h-12 appearance-none bg-[length:16px] bg-[right_1rem_center] bg-no-repeat pr-10",
          error ? "border-danger" : "border-border",
          className,
        )}
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239A9AA5' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E\")",
        }}
      >
        {placeholder ? <option value="">{placeholder}</option> : null}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Shell>
  );
}

export function CheckboxField({
  label,
  error,
  className,
  ...props
}: {
  label: React.ReactNode;
  error?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  const generated = useId();
  const id = props.id ?? generated;
  const errorId = `${id}-error`;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-start gap-3">
        <input
          {...props}
          type="checkbox"
          id={id}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          className={cn(
            "mt-1 size-[18px] shrink-0 cursor-pointer rounded-[5px] border bg-surface",
            "accent-[#5B8DFF] focus:outline-none focus:ring-2 focus:ring-accent/35",
            error ? "border-danger" : "border-border",
            className,
          )}
        />
        <label htmlFor={id} className="cursor-pointer text-[14px] leading-relaxed text-text-muted">
          {label}
        </label>
      </div>
      {error ? (
        <p id={errorId} className="text-[13px] text-danger">
          {error}
        </p>
      ) : null}
    </div>
  );
}
