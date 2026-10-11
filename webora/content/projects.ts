import { demoPreviews } from "@/config/images";
import type { ImageSlot } from "@/config/images";
import type { Locale } from "./i18n";

/**
 * The seven demo sites, as shown in the portfolio grid and the homepage
 * showcase. Every business here is fictional.
 */

export type ProjectCategory =
  | "hospitality"
  | "ecommerce"
  | "services"
  | "professional"
  | "creative"
  | "realestate";

export type Project = {
  slug: string;
  /** Fictional business name shown on the card. */
  name: string;
  href: string;
  category: ProjectCategory;
  preview: ImageSlot;
  /** Which pricing package the "I want a site like this" CTA preselects. */
  pkg: "starter" | "business" | "eshop";
  industry: Record<Locale, string>;
  description: Record<Locale, string>;
};

export const projects: Project[] = [
  {
    slug: "bistro",
    name: "Bistro Hĺbka",
    href: "/demo/bistro",
    category: "hospitality",
    preview: demoPreviews.bistro,
    pkg: "business",
    industry: { sk: "Kaviareň a bistro", en: "Café and bistro" },
    description: {
      sk: "Menu s kategóriami, galéria a rezervácia stola s overovaním.",
      en: "Tabbed menu, gallery and a table reservation form with validation.",
    },
  },
  {
    slug: "shop",
    name: "Nordik",
    href: "/demo/shop",
    category: "ecommerce",
    preview: demoPreviews.shop,
    pkg: "eshop",
    industry: { sk: "E-shop s bytovými doplnkami", en: "Home goods online shop" },
    description: {
      sk: "Filtrovanie produktov, detail s variantmi a funkčný košík.",
      en: "Product filtering, detail pages with variants and a working cart.",
    },
  },
  {
    slug: "fitness",
    name: "Pulse Studio",
    href: "/demo/fitness",
    category: "services",
    preview: demoPreviews.fitness,
    pkg: "business",
    industry: { sk: "Fitness štúdio", en: "Fitness studio" },
    description: {
      sk: "Rozvrh hodín, členské a štvorkrokový rezervačný proces.",
      en: "Class timetable, memberships and a four-step booking flow.",
    },
  },
  {
    slug: "build",
    name: "Stavmont",
    href: "/demo/build",
    category: "services",
    preview: demoPreviews.build,
    pkg: "business",
    industry: { sk: "Stavebná firma", en: "Construction company" },
    description: {
      sk: "Posuvné porovnanie pred a po, galéria realizácií a dopyt na cenu.",
      en: "Draggable before/after comparison, project gallery and a quote form.",
    },
  },
  {
    slug: "legal",
    name: "Hlavatý & Partners",
    href: "/demo/legal",
    category: "professional",
    preview: demoPreviews.legal,
    pkg: "business",
    industry: { sk: "Advokátska kancelária", en: "Law firm" },
    description: {
      sk: "Oblasti práva, profily advokátov a objednanie konzultácie.",
      en: "Practice areas, attorney profiles and a consultation request.",
    },
  },
  {
    slug: "lens",
    name: "Studio Lens",
    href: "/demo/lens",
    category: "creative",
    preview: demoPreviews.lens,
    pkg: "starter",
    industry: { sk: "Fotograf", en: "Photographer" },
    description: {
      sk: "Masonry galéria s filtrom kategórií a lightboxom na klávesnicu.",
      en: "Masonry gallery with category filters and a keyboard lightbox.",
    },
  },
  {
    slug: "estate",
    name: "Domov Reality",
    href: "/demo/estate",
    category: "realestate",
    preview: demoPreviews.estate,
    pkg: "business",
    industry: { sk: "Realitná kancelária", en: "Estate agency" },
    description: {
      sk: "Filtrovanie nehnuteľností, detaily s galériou a hypotekárna kalkulačka.",
      en: "Property filters, detail pages with galleries and a mortgage calculator.",
    },
  },
];

export function getProject(slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}
