import Image from "next/image";
import { Info, Star } from "lucide-react";
import { Reveal } from "@/components/ui/Reveal";
import { Flag } from "@/components/ui/Flag";
import { PUBLISHED_REVIEWS, COUNTRY_NAMES, type Review } from "@/content/reviews";
import type { Dictionary } from "@/content/i18n";
import { cn } from "@/lib/utils";

/**
 * Customer reviews.
 *
 * Content lives in content/reviews.ts; this component only lays it out. Each
 * card marked `sample` carries a label, and a short note above the grid shows
 * while any visible card is a sample, so placeholder reviewers are never
 * passed off as real clients. Genuine reviews render with neither.
 *
 * Large screens fill rows of three; when the count leaves a remainder, the
 * last row's cards widen to fill it (five = three + two). Tablets use two
 * columns with an odd last card spanning both; phones use one column.
 */
export function Testimonials({ dict }: { dict: Dictionary }) {
  const t = dict.testimonials;
  const reviews = PUBLISHED_REVIEWS;
  const anySample = reviews.some((review) => review.sample);
  const lastRowStart = reviews.length - (reviews.length % 3 || 3);
  const lastRowSpan = { 1: "lg:col-span-6", 2: "lg:col-span-3", 3: "lg:col-span-2" }[
    reviews.length - lastRowStart
  ];

  return (
    <>
      {anySample ? (
        <Reveal>
          <p
            role="note"
            className="mb-10 flex max-w-[78ch] gap-3 rounded-xl border border-border bg-surface/60 px-5 py-4 text-[14px] leading-relaxed text-text-muted"
          >
            <Info aria-hidden="true" strokeWidth={1.75} className="mt-0.5 size-[18px] shrink-0" />
            {t.disclaimer}
          </p>
        </Reveal>
      ) : null}

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
    </>
  );
}

function ReviewCard({ review, dict }: { review: Review; dict: Dictionary }) {
  const t = dict.testimonials;

  return (
    <figure
      className={cn(
        "flex w-full min-w-0 flex-col gap-5 rounded-2xl border border-border bg-surface p-5 break-normal sm:p-7",
        "shadow-[0_1px_0_rgba(255,255,255,0.04)_inset,0_12px_32px_-24px_rgba(0,0,0,0.9)]",
        "transition-[transform,border-color,box-shadow] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]",
        "hover:-translate-y-1 hover:border-text-muted/30",
        "hover:shadow-[0_1px_0_rgba(255,255,255,0.06)_inset,0_22px_44px_-26px_rgba(0,0,0,1)]",
        "motion-reduce:transition-none motion-reduce:hover:translate-y-0",
      )}
    >
      <figcaption className="flex items-start gap-3.5 sm:gap-4">
        {review.photo ? (
          <Image
            src={review.photo.src}
            width={review.photo.width}
            height={review.photo.height}
            alt={t.photoAlt.replace("{name}", review.name)}
            sizes="56px"
            className="size-12 shrink-0 rounded-full sm:size-14 bg-surface-hover object-cover object-center ring-1 ring-white/10"
          />
        ) : (
          <span
            aria-hidden="true"
            className="flex size-12 shrink-0 items-center justify-center rounded-full bg-accent/15 text-[15px] font-semibold text-accent ring-1 ring-white/10 sm:size-14"
          >
            {initials(review.name)}
          </span>
        )}

        <span className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="text-[16px] font-semibold leading-tight tracking-[-0.01em] text-text">
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

      <div className="flex items-center justify-between gap-3">
        <span
          role="img"
          aria-label={t.ratingLabel.replace("{n}", String(review.rating))}
          className="flex gap-1 text-[#F5B83D]"
        >
          {Array.from({ length: 5 }, (_, i) => (
            <Star
              key={i}
              aria-hidden="true"
              strokeWidth={0}
              className={cn("size-4 fill-current", i >= review.rating && "opacity-25")}
            />
          ))}
        </span>
        {review.sample ? (
          <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.08em] text-text-muted">
            {t.badge}
          </span>
        ) : null}
      </div>

      <blockquote lang={review.lang} className="text-[15.5px] leading-[1.65] text-text/85">
        <p>{review.lang === "en" ? `“${review.text}”` : `„${review.text}“`}</p>
      </blockquote>
    </figure>
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
