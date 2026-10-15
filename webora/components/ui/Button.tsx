"use client";

import Link from "next/link";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * iOS-inspired controls.
 *
 * The feel comes from three things, not from decoration:
 *  - press scales down slightly and lifts back on release (`active:scale-...`),
 *    which gives immediate feedback on the same frame as the tap;
 *  - a tuned ease that decelerates rather than bouncing, so repeat clicks
 *    never feel laggy;
 *  - hover and focus states that change surface, not layout, so nothing
 *    around the button shifts.
 *
 * Durations stay short (120–180ms). Anything slower reads as lag on a control.
 */

type Variant = "primary" | "secondary" | "ghost" | "glass";
type Size = "lg" | "md" | "sm";

const base =
  "group/btn relative inline-flex select-none items-center justify-center gap-2 " +
  "rounded-xl font-medium tracking-[-0.01em] whitespace-nowrap " +
  "transition-[transform,background-color,border-color,color,box-shadow] " +
  "duration-150 ease-[cubic-bezier(0.32,0.72,0,1)] " +
  "active:scale-[0.97] active:duration-75 " +
  "disabled:pointer-events-none disabled:opacity-50 " +
  "motion-reduce:transition-none motion-reduce:active:scale-100";

const variants: Record<Variant, string> = {
  primary:
    "bg-accent text-[#06112E] shadow-[0_1px_0_rgba(255,255,255,0.25)_inset,0_6px_18px_-8px_rgba(91,141,255,0.9)] " +
    "hover:bg-accent-hover hover:shadow-[0_1px_0_rgba(255,255,255,0.3)_inset,0_10px_26px_-10px_rgba(91,141,255,1)]",
  secondary:
    "border border-border bg-surface/60 text-text backdrop-blur-sm " +
    "hover:border-text-muted/60 hover:bg-surface-hover",
  ghost: "text-text-muted hover:bg-surface/70 hover:text-text",
  glass:
    "border border-white/15 bg-white/8 text-white backdrop-blur-md " +
    "hover:border-white/25 hover:bg-white/14",
};

const sizes: Record<Size, string> = {
  lg: "h-[52px] px-7 text-[16px]",
  md: "h-11 px-5 text-[15px]",
  sm: "h-9 px-3.5 text-[14px]",
};

type Common = {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: React.ReactNode;
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  loading = false,
  loadingLabel,
  disabled,
  ...props
}: Common & { loading?: boolean; loadingLabel?: string } &
  React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(base, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      {...props}
    >
      {loading ? (
        <Loader2 aria-hidden="true" strokeWidth={2} className="size-4 animate-spin" />
      ) : null}
      {loading && loadingLabel ? loadingLabel : children}
    </button>
  );
}

export function ButtonLink({
  href,
  variant = "primary",
  size = "md",
  className,
  children,
  external,
  ...props
}: Common & { href: string; external?: boolean } & Omit<
    React.AnchorHTMLAttributes<HTMLAnchorElement>,
    "href"
  >) {
  const classes = cn(base, variants[variant], sizes[size], className);

  if (external) {
    return (
      <a href={href} className={classes} rel="noopener noreferrer" {...props}>
        {children}
      </a>
    );
  }
  return (
    <Link href={href} className={classes} {...props}>
      {children}
    </Link>
  );
}
