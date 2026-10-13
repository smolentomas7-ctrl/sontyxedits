import { imageById } from "@/config/images";
import { site } from "@/config/miauto";
import { SlotImage } from "@/components/ui/SlotImage";
import { Reveal } from "@/components/ui/Reveal";
import type { Locale, LocaleContent } from "@/content/types";

/**
 * The owners of the workshop.
 *
 * Driven entirely by `site.owners`, so one person or two lay out correctly with
 * no change here. If the array is empty, or a listed person has no photograph
 * yet, nothing is rendered at all — no outline cards, no initials, no heading
 * left hanging over an empty row.
 *
 * Portraits are 4:5 and share one frame, radius and object-fit, so two photos
 * taken at different distances still read as a pair.
 */
export function Owners({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const owners = site.owners
    .map((owner) => ({ ...owner, slot: imageById(owner.photo) }))
    .filter((owner) => owner.slot !== null);

  if (owners.length === 0) return null;

  return (
    <div>
      <h2 className="text-[1.5rem] md:text-[2rem]">{t.about.ownersHeading}</h2>

      <ul className="mt-8 grid gap-6 sm:grid-cols-2 sm:gap-8 md:max-w-[46rem]">
        {owners.map((owner, index) => {
          const role = t.about.ownerRoles[owner.roleKey];
          return (
            <Reveal as="li" key={owner.name} index={index}>
              <figure className="m-0">
                <SlotImage
                  slot={owner.slot!}
                  // Describes the person, in the page's language. The branding
                  // visible behind them is not part of the description.
                  alt={`${owner.name} — ${role}, ${site.legalName}`}
                  index={index}
                  sizes="(min-width: 640px) 320px, 100vw"
                  className="rounded-[var(--radius-card)] border border-[var(--border)]"
                />
                <figcaption className="mt-4">
                  <p className="font-heading text-[1.1875rem] font-semibold tracking-[-0.02em]">
                    {owner.name}
                  </p>
                  <p className="mt-1 text-[0.9375rem] text-[color:var(--text-muted)]">{role}</p>
                </figcaption>
              </figure>
            </Reveal>
          );
        })}
      </ul>
    </div>
  );
}
