import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  interactive = true,
  as: Tag = "div",
}: {
  className?: string;
  children: React.ReactNode;
  /** Set false for static panels that should not lift on hover. */
  interactive?: boolean;
  as?: "div" | "article" | "li";
}) {
  return (
    <Tag
      className={cn(
        "rounded-2xl border border-border bg-surface",
        interactive &&
          "transition-[transform,border-color,background-color] duration-200 ease-out " +
            "hover:-translate-y-1 hover:border-accent/20 hover:bg-surface-hover",
        className,
      )}
    >
      {children}
    </Tag>
  );
}
