import {
  DAY_ORDER,
  formattedAddress,
  has,
  site,
  siteUrl,
  siteUrlIsPlaceholder,
} from "@/config/miauto";

/**
 * Prefix for every URL in the structured data.
 *
 * Empty until the real domain is set, which leaves relative references — and a
 * relative reference in JSON-LD resolves against the page it was found on,
 * which is exactly right. An absolute `http://localhost:3000/...` would instead
 * claim the business lives at an address no crawler can reach.
 */
const base = siteUrlIsPlaceholder ? "" : siteUrl;
import { images } from "@/config/images";
import type { Locale } from "@/content/types";

const SCHEMA_DAY: Record<string, string> = {
  mon: "Monday",
  tue: "Tuesday",
  wed: "Wednesday",
  thu: "Thursday",
  fri: "Friday",
  sat: "Saturday",
  sun: "Sunday",
};

/**
 * AutoRepair structured data, built ONLY from config/miauto.ts.
 *
 * Deliberately absent: aggregateRating, review, priceRange. There are no
 * ratings, no reviews and no published prices, so emitting any of them would be
 * inventing them. Properties whose value is not known yet — company number,
 * coordinates, social profiles — are omitted entirely rather than guessed.
 */
export function autoRepairJsonLd(locale: Locale) {
  // A midday break is expressed as two spans for the day, not as one span with a
  // hole in it: schema.org has no way to say "closed between".
  const openingHoursSpecification = DAY_ORDER.flatMap((day) => {
    const hours = site.hours[day];
    if (!hours) return [];
    const [breakStart, breakEnd] = site.lunchBreak;
    const spans: [string, string][] = [
      [hours[0], breakStart],
      [breakEnd, hours[1]],
    ];
    return spans.map(([opens, closes]) => ({
      "@type": "OpeningHoursSpecification",
      dayOfWeek: `https://schema.org/${SCHEMA_DAY[day]}`,
      opens,
      closes,
    }));
  });

  const data: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    "@id": `${base}/#autorepair`,
    name: site.legalName,
    url: `${base}/${locale}`,
    telephone: site.phone,
    email: site.email,
    image: `${base}${images.hero.src}`,
    address: {
      "@type": "PostalAddress",
      streetAddress: site.street,
      postalCode: site.postalCode,
      addressLocality: site.city,
      addressRegion: site.region,
      addressCountry: site.country,
    },
    areaServed: { "@type": "City", name: site.city },
    hasMap: site.mapUrl,
    openingHoursSpecification,
  };

  // Coordinates were never supplied. An estimate here would put a pin on the
  // wrong building, which is worse than having no pin at all.
  if (has(site.geo.lat) && has(site.geo.lng)) {
    data["geo"] = {
      "@type": "GeoCoordinates",
      latitude: site.geo.lat,
      longitude: site.geo.lng,
    };
  }

  if (has(site.ico)) data["identifier"] = { "@type": "PropertyValue", name: "IČO", value: site.ico };
  if (has(site.icDph)) data["vatID"] = site.icDph;
  if (has(site.dic)) data["taxID"] = site.dic;

  const sameAs = [site.social.facebook, site.social.instagram].filter(has);
  if (sameAs.length > 0) data["sameAs"] = sameAs;

  const founders = site.owners.map((owner) => ({ "@type": "Person", name: owner.name }));
  if (founders.length > 0) data["founder"] = founders;

  return data;
}

export function breadcrumbJsonLd(
  items: readonly { readonly name: string; readonly url: string }[],
) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: `${base}${item.url}`,
    })),
  };
}

export { formattedAddress };
