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
 * The supplied portraits are square, shot in the same place in the same light,
 * and each carries its own name label. So they share one frame, one radius and
 * one object-fit — and no caption is printed under them, because that would
 * print each name twice.
 */
export function Owners({ locale, t }: { locale: Locale; t: LocaleContent }) {
  const owners = site.owners
    .map((owner) => ({ ...owner, slot: imageById(owner.photo) }))
    .filter((owner) => owner.slot !== null);

  if (owners.length === 0) return null;

  return (
    <div>
      <h2 className="text-[1.5rem] md:text-[2rem]">{t.about.ownersHeading}</h2>

      {/* Held to a column width rather than run full-bleed: two square portraits
          at full container width would be the loudest thing on the page. */}
      <ul className="mt-8 grid gap-5 sm:grid-cols-2 sm:gap-6 md:max-w-[52rem]">
        {owners.map((owner, index) => {
          const role = t.about.ownerRoles[owner.roleKey];
          return (
            <Reveal as="li" key={owner.name} index={index}>
              <SlotImage
                slot={owner.slot!}
                // The name is in the photograph, where a screen reader cannot
                // reach it, so it is spelled out here instead. The branding
                // visible behind them is not part of the description.
                alt={`${owner.name} — ${role}, ${site.legalName}`}
                index={index}
                sizes="(min-width: 640px) 400px, 100vw"
                className="rounded-[var(--radius-card)] border border-[var(--border)]"
              />
            </Reveal>
          );
        })}
      </ul>
    </div>
  );
}
