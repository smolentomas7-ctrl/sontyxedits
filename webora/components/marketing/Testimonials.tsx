import Image from "next/image";
import { Quote, Star } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import { Flag } from "@/components/ui/Flag";
import { PUBLISHED_REVIEWS, COUNTRY_NAMES, type Review } from "@/content/reviews";
import type { Dictionary } from "@/content/i18n";
import { cn } from "@/lib/utils";

/**
 * Customer reviews.
 *
 * Content lives in content/reviews.ts; only genuine reviews reach this
 * component (see PUBLISHED_REVIEWS there), so nothing here needs a sample
 * label. The home page skips the whole section while the list is empty.
 *
 * A single review is shown as one large featured quote. Two or more fall into
 * a grid: rows of three on large screens, with a short last row widening to
 * fill it; two columns on tablets, an odd last card spanning both; one column
 * on phones.
 */
export function Testimonials({ dict }: { dict: Dictionary }) {
  const reviews = PUBLISHED_REVIEWS;

  if (reviews.length === 1) {
    return (
      <Reveal>
        <ReviewCard review={reviews[0]} dict={dict} featured />
      </Reveal>
    );
  }

  const lastRowStart = reviews.length - (reviews.length % 3 || 3);
  const lastRowSpan = { 1: "lg:col-span-6", 2: "lg:col-span-3", 3: "lg:col-span-2" }[
    reviews.length - lastRowStart
  ];

  return (
    <ul className="grid gap-5 md:grid-cols-2 lg:grid-cols-6">
      {reviews.map((review, index) => (
        <Reveal
          as="li"
          key={review.id}
          delay={index * 60}
          className={cn(
            "flex min-w-0",
            index < lastRowStart ? "lg:col-span-2" : lastRowSpan,
            reviews.length % 2 === 1 && index === reviews.length - 1 && "md:col-span-2",
          )}
        >
          <ReviewCard review={review} dict={dict} />
        </Reveal>
      ))}
    </ul>
  );
}

function ReviewCard({
  review,
  dict,
  featured = false,
}: {
  review: Review;
  dict: Dictionary;
  featured?: boolean;
}) {
  const t = dict.testimonials;

  return (
    <figure
      className={cn(
        "relative flex w-full min-w-0 flex-col rounded-2xl border border-border bg-surface break-normal",
        "shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_12px_32px_-24px_rgba(0,0,0,0.9)]",
        featured
          ? "max-w-4xl gap-7 overflow-hidden p-6 sm:gap-9 sm:p-10 lg:p-12"
          : [
              "gap-5 p-5 sm:p-7",
              "transition-[transform,border-color,box-shadow] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]",
              "hover:-translate-y-1 hover:border-text-muted/30",
              "hover:shadow-[0_1px_0_rgba(255,255,255,0.06)_inset,0_22px_44px_-26px_rgba(0,0,0,1)]",
              "motion-reduce:transition-none motion-reduce:hover:translate-y-0",
            ],
      )}
    >
      {featured ? (
        <Quote
          aria-hidden="true"
          strokeWidth={0}
          className="pointer-events-none absolute -top-2 right-4 size-32 fill-accent/10 sm:right-8 sm:size-40"
        />
      ) : null}

      <Stars rating={review.rating} label={t.ratingLabel} large={featured} />

      <blockquote
        lang={review.lang}
        className={cn(
          "relative",
          featured
            ? "text-[1.1875rem] font-medium leading-[1.55] tracking-[-0.01em] text-text sm:text-[1.5rem] sm:leading-[1.5]"
            : "order-last text-[15.5px] leading-[1.65] text-text/85",
        )}
      >
        <p>{review.lang === "en" ? `“${review.text}”` : `„${review.text}“`}</p>
      </blockquote>

      <figcaption
        className={cn(
          "flex items-start",
          featured
            ? "gap-4 border-t border-border pt-6 sm:gap-5 sm:pt-8"
            : "-order-1 gap-3.5 sm:gap-4",
        )}
      >
        {review.photo ? (
          <Image
            src={review.photo.src}
            width={review.photo.width}
            height={review.photo.height}
            alt={review.photo.alt || t.photoAlt.replace("{name}", review.name)}
            sizes={featured ? "72px" : "56px"}
            className={cn(
              "shrink-0 rounded-full bg-surface-hover object-cover object-center ring-1 ring-white/10",
              featured ? "size-14 sm:size-[72px]" : "size-12 sm:size-14",
            )}
          />
        ) : (
          <span
            aria-hidden="true"
            className={cn(
              "flex shrink-0 items-center justify-center rounded-full bg-accent/15 font-semibold text-accent ring-1 ring-white/10",
              featured ? "size-14 text-[17px] sm:size-[72px]" : "size-12 text-[15px] sm:size-14",
            )}
          >
            {initials(review.name)}
          </span>
        )}

        <span className="flex min-w-0 flex-1 flex-col gap-1">
          <span
            className={cn(
              "font-semibold leading-tight tracking-[-0.01em] text-text",
              featured ? "text-[17px] sm:text-[18px]" : "text-[16px]",
            )}
          >
            {review.name}
          </span>

          <span className="flex min-w-0 items-start gap-2 text-[13.5px] leading-snug text-text-muted">
            <Flag country={review.country} className="mt-[2px]" />
            <span className="min-w-0">
              {COUNTRY_NAMES[review.country]}
              <span aria-hidden="true" className="px-1.5 text-text-muted/60">
                ·
              </span>
              <span className="text-text/85">{review.company}</span>
            </span>
          </span>

          <span className="text-[13.5px] text-text-muted">{review.position}</span>
        </span>
      </figcaption>
    </figure>
  );
}

function Stars({ rating, label, large }: { rating: number; label: string; large: boolean }) {
  return (
    <span
      role="img"
      aria-label={label.replace("{n}", String(rating))}
      className="relative flex gap-1 text-[#F5B83D]"
    >
      {Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          aria-hidden="true"
          strokeWidth={0}
          className={cn("fill-current", large ? "size-5" : "size-4", i >= rating && "opacity-25")}
        />
      ))}
    </span>
  );
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}
