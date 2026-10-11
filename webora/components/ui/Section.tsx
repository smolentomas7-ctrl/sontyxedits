import { cn } from "@/lib/utils";
import { Container } from "./Container";

export function Section({
  id,
  className,
  containerClassName,
  children,
  as: Tag = "section",
  ariaLabelledBy,
}: {
  id?: string;
  className?: string;
  containerClassName?: string;
  children: React.ReactNode;
  as?: "section" | "div";
  ariaLabelledBy?: string;
}) {
  return (
    <Tag id={id} aria-labelledby={ariaLabelledBy} className={cn("py-[72px] md:py-32", className)}>
      <Container className={containerClassName}>{children}</Container>
    </Tag>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  subtitle,
  id,
  align = "left",
  className,
}: {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  id?: string;
  align?: "left" | "center";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4",
        align === "center" && "items-center text-center",
        className,
      )}
    >
      {eyebrow ? (
        <span className="t-small font-medium uppercase tracking-[0.18em] text-accent">
          {eyebrow}
        </span>
      ) : null}
      <h2 id={id} className="t-h2 max-w-[22ch] text-text">
        {title}
      </h2>
      {subtitle ? (
        <p className={cn("t-prose text-text-muted", align === "center" && "mx-auto")}>{subtitle}</p>
      ) : null}
    </div>
  );
}
