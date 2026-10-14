"use client";

import clsx from "clsx";
import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import { usePressHandlers } from "@/lib/motion";

type Variant = "primary" | "secondary" | "ghost";
type Size = "md" | "lg";

const base =
  "tappable tappable--lift inline-flex items-center justify-center gap-2 " +
  "rounded-[var(--radius-control)] font-semibold leading-none no-underline select-none";

const sizes: Record<Size, string> = {
  // 52px desktop / 48px mobile
  md: "h-12 md:h-[52px] px-5 md:px-6 text-[0.9375rem] md:text-base",
  lg: "h-[52px] md:h-[60px] px-6 md:px-8 text-base md:text-lg",
};

const variants: Record<Variant, string> = {
  primary:
    "bg-[var(--accent)] text-[color:var(--accent-ink)] hover:bg-[var(--accent-hover)] " +
    "disabled:bg-[var(--surface-hover)] disabled:text-[color:var(--text-muted)] disabled:cursor-not-allowed",
  secondary:
    "bg-transparent text-[color:var(--text)] border border-[var(--border)] " +
    "hover:border-[color-mix(in_srgb,var(--accent)_55%,var(--border))] hover:bg-[var(--surface)]",
  ghost:
    "bg-transparent text-[color:var(--text-muted)] hover:text-[color:var(--text)]",
};

type CommonProps = {
  variant?: Variant;
  size?: Size;
  className?: string;
  children: ReactNode;
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...rest
}: CommonProps & ComponentPropsWithoutRef<"button">) {
  const press = usePressHandlers();
  return (
    <button
      className={clsx(base, sizes[size], variants[variant], className)}
      {...press}
      {...rest}
    >
      {children}
    </button>
  );
}

export function ButtonLink({
  variant = "primary",
  size = "md",
  className,
  children,
  href,
  external,
  ...rest
}: CommonProps & { href: string; external?: boolean } & Omit<
    ComponentPropsWithoutRef<"a">,
    "href"
  >) {
  const press = usePressHandlers();
  const classes = clsx(base, sizes[size], variants[variant], className);

  // tel: and external destinations are plain anchors; Link is for in-app routes.
  if (external || href.startsWith("tel:") || href.startsWith("mailto:") || href.startsWith("http")) {
    return (
      <a
        href={href}
        className={classes}
        {...(href.startsWith("http") ? { target: "_blank", rel: "noopener noreferrer" } : {})}
        {...press}
        {...rest}
      >
        {children}
      </a>
    );
  }

  return (
    <Link href={href} className={classes} {...press} {...rest}>
      {children}
    </Link>
  );
}
