import { DAY_ORDER, formattedAddress, isPlaceholder, site, siteUrl } from "@/config/miauto";
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
 * ratings, no reviews and no prices, so emitting any of them would be inventing
 * them. Any property whose value is still a placeholder is omitted entirely
 * rather than published as the literal "[EMAIL]".
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
    name: site.legalName,
    url: `${siteUrl}/${locale}`,
    telephone: site.phone,
    address: {
      "@type": "PostalAddress",
      streetAddress: site.street,
      postalCode: site.postalCode,
      addressLocality: site.city,
      addressRegion: site.region,
      addressCountry: site.country,
    },
    areaServed: { "@type": "City", name: site.city },
    openingHoursSpecification,
  };

  if (!isPlaceholder(site.email)) data["email"] = site.email;

  const sameAs = [site.social.facebook, site.social.instagram].filter(
    (value) => !isPlaceholder(value),
  );
  if (sameAs.length > 0) data["sameAs"] = sameAs;

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
