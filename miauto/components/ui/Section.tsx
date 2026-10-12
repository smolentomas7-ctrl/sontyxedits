import clsx from "clsx";
import type { ReactNode } from "react";

/**
 * Section padding varies deliberately — a dense section after an airy one — so
 * the page has rhythm instead of one uniform drumbeat.
 */
export function Section({
  id,
  rhythm = "normal",
  className,
  children,
  as: Tag = "section",
}: {
  id?: string;
  rhythm?: "tight" | "normal" | "loose";
  className?: string;
  children: ReactNode;
  as?: "section" | "div";
}) {
  return (
    <Tag
      id={id}
      className={clsx(
        "section",
        rhythm === "tight" && "section--tight",
        rhythm === "loose" && "section--loose",
        className,
      )}
    >
      {children}
    </Tag>
  );
}

export function Container({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return <div className={clsx("container", className)}>{children}</div>;
}
