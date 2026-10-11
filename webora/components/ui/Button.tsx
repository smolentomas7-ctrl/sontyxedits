import Link from "next/link";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost";
type Size = "md" | "sm";

const base =
  "inline-flex items-center justify-center gap-2 rounded-[10px] font-medium " +
  "transition-[transform,background-color,border-color,color] duration-150 ease-out " +
  "disabled:cursor-not-allowed disabled:opacity-55 disabled:hover:translate-y-0";

const variants: Record<Variant, string> = {
  primary:
    "bg-accent text-[#06120D] hover:bg-accent-hover hover:-translate-y-0.5 " +
    "active:translate-y-0",
  secondary:
    "border border-border bg-transparent text-text hover:border-text-muted " +
    "hover:bg-surface hover:-translate-y-0.5 active:translate-y-0",
  ghost: "bg-transparent text-text-muted hover:text-text",
};

const sizes: Record<Size, string> = {
  md: "h-12 px-6 text-[15px]",
  sm: "h-10 px-4 text-sm",
};

type CommonProps = {
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
  ...props
}: CommonProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
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
}: CommonProps & {
  href: string;
  external?: boolean;
} & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, "href">) {
  const classes = cn(base, variants[variant], sizes[size], className);

  if (external) {
    return (
      <a href={href} className={classes} {...props}>
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
