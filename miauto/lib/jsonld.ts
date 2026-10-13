import { DAY_ORDER, formattedAddress, has, site, siteUrl } from "@/config/miauto";
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
  const openingHoursSpecification = DAY_ORDER.flatMap((day) => {
    const hours = site.hours[day];
    if (!hours) return [];
    return [
      {
        "@type": "OpeningHoursSpecification",
        dayOfWeek: `https://schema.org/${SCHEMA_DAY[day]}`,
        opens: hours[0],
        closes: hours[1],
      },
    ];
  });

  const data: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "AutoRepair",
    "@id": `${siteUrl}/#autorepair`,
    name: site.legalName,
    url: `${siteUrl}/${locale}`,
    telephone: site.phone,
    email: site.email,
    image: `${siteUrl}${images.hero.src}`,
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
      item: `${siteUrl}${item.url}`,
    })),
  };
}

export { formattedAddress };
