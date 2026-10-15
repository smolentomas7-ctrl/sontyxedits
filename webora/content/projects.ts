import { miauto, shop, lens } from "@/config/images";
import type { ImageSlot } from "@/config/images";
import type { Locale } from "./i18n";

/**
 * Exactly three portfolio examples, one per website type.
 *
 * `kind` separates real delivered work from demonstrations built to show
 * capability. The UI renders a different badge for each and never implies a
 * demonstration belongs to a client.
 *
 * The other mini-sites under /demo (bistro, fitness, build, legal, estate)
 * still exist and still work, but are deliberately not listed here — the
 * portfolio is limited to three primary examples.
 */

export type ProjectCategory = "informacny" | "eshop" | "galeria";
export type ProjectKind = "client" | "demo";

export type Project = {
  slug: string;
  name: string;
  /** Where "Pozrieť ukážku" goes. */
  href: string;
  /** External link opens in a new tab; demos are internal routes. */
  external?: boolean;
  kind: ProjectKind;
  category: ProjectCategory;
  /** Card preview, shown inside a browser frame. */
  preview: ImageSlot;
  /** Extra captures for the case study page. */
  gallery: ImageSlot[];
  /** Mobile capture, shown beside the desktop one where available. */
  mobile?: ImageSlot;
  year: string;
  categoryLabel: Record<Locale, string>;
  kindLabel: Record<Locale, string>;
  summary: Record<Locale, string>;
  /** Longer narrative for the case study page. */
  intro: Record<Locale, string>;
  /** What the project actually involved. */
  highlights: Record<Locale, string[]>;
  /** Capabilities demonstrated, rendered as chips. */
  capabilities: Record<Locale, string[]>;
};

export const projects: Project[] = [
  {
    slug: "miauto",
    name: "M.I.Auto s.r.o.",
    href: "/sk/portfolio/miauto",
    kind: "client",
    category: "informacny",
    preview: miauto.shotHome,
    gallery: [miauto.shotHome, miauto.shotServices, miauto.shotDetail, miauto.shotContact],
    mobile: miauto.shotMobile,
    year: "2025",
    categoryLabel: { sk: "Informačný web", en: "Informational website" },
    kindLabel: { sk: "Klientský projekt", en: "Client project" },
    summary: {
      sk: "Dvojjazyčný web pre autoservis v Ružomberku. Sedem samostatných stránok služieb, dôraz na telefonát ako hlavnú konverziu.",
      en: "A bilingual site for a car service in Ružomberok. Seven standalone service pages, built around the phone call as the primary conversion.",
    },
    intro: {
      sk: "M.I.Auto je autoservis v Ružomberku, ktorý sa venuje diagnostike, elektronike a mechanickým opravám. Zákazník k nim najčastejšie prichádza s konkrétnym problémom — svieti kontrolka, auto ťahá do strany, klimatizácia nechladí. Web je postavený tak, aby na takúto otázku odpovedal a doviedol človeka k telefonátu.",
      en: "M.I.Auto is a car service in Ružomberok working on diagnostics, electronics and mechanical repairs. Customers usually arrive with one specific problem — a warning light, a car pulling to one side, an air conditioner that stopped cooling. The site is built to answer that question and get the person to the phone.",
    },
    highlights: {
      sk: [
        "Samostatná stránka pre každú zo siedmich služieb, aby mala vlastný popis a vlastnú pozíciu vo vyhľadávaní",
        "Telefónne číslo ako hlavná výzva — v hlavičke, v hero sekcii aj na konci každej stránky",
        "Otváracie hodiny, ktoré na stránke ukazujú aktuálny stav namiesto statickej tabuľky",
        "Slovenská a anglická verzia s rovnakou štruktúrou adries",
        "Fotografie z vlastnej dielne namiesto stockových záberov",
      ],
      en: [
        "A standalone page per service, so each has its own copy and its own search presence",
        "The phone number as the primary call to action — in the header, the hero and at the end of every page",
        "Opening hours that show the current state rather than a static table",
        "Slovak and English versions sharing one URL structure",
        "Photography from the client's own workshop instead of stock imagery",
      ],
    },
    capabilities: {
      sk: ["Dvojjazyčný web", "7 stránok služieb", "Lokálne SEO", "Klik na telefón", "Mapa a lokalita", "Responzívny dizajn"],
      en: ["Bilingual site", "7 service pages", "Local SEO", "Click-to-call", "Map and location", "Responsive design"],
    },
  },

  {
    slug: "shop",
    name: "Nordik",
    href: "/demo/shop",
    kind: "demo",
    category: "eshop",
    preview: shop.hero,
    gallery: [shop.hero, shop.category1, shop.product1, shop.product3],
    year: "2026",
    categoryLabel: { sk: "E-shop", en: "E-commerce" },
    kindLabel: { sk: "Ukážka možností", en: "Capability demo" },
    summary: {
      sk: "Ukážkový e-shop s bytovými doplnkami. Filtrovanie, detail produktu s variantmi a funkčný košík vrátane pokladne.",
      en: "A demo home-goods shop. Filtering, product detail with variants, and a working cart through to checkout.",
    },
    intro: {
      sk: "Nordik je vymyslený obchod, ktorý sme postavili preto, aby sme na niečom ukázali, ako vieme riešiť predaj online. Nie je to screenshot ani maketa — produkty sa dajú filtrovať, pridať do košíka a prejsť pokladňou.",
      en: "Nordik is a fictional shop we built to demonstrate how we approach selling online. It is not a screenshot or a mockup — products filter, go into a cart, and pass through a checkout.",
    },
    highlights: {
      sk: [
        "Deväť produktov s kategóriami, cenovým filtrom a zoraďovaním priamo v prehliadači",
        "Detail produktu s galériou a výberom variantu",
        "Košík, ktorý si pamätá obsah aj po obnovení stránky",
        "Pokladňa s výberom dopravy a platby a s overovaním polí",
      ],
      en: [
        "Nine products with categories, a price filter and sorting, all in the browser",
        "Product detail with a gallery and variant selection",
        "A cart that survives a page reload",
        "A checkout with shipping and payment selection and field validation",
      ],
    },
    capabilities: {
      sk: ["Katalóg produktov", "Filtrovanie a zoraďovanie", "Varianty produktov", "Košík", "Rozhranie pokladne", "Responzívna mriežka"],
      en: ["Product catalogue", "Filtering and sorting", "Product variants", "Cart", "Checkout interface", "Responsive grid"],
    },
  },

  {
    slug: "lens",
    name: "Studio Lens",
    href: "/demo/lens",
    kind: "demo",
    category: "galeria",
    preview: lens.hero,
    gallery: [lens.hero, lens.portrait1, lens.wedding1, lens.landscape1],
    year: "2026",
    categoryLabel: { sk: "Galéria", en: "Gallery" },
    kindLabel: { sk: "Ukážka možností", en: "Capability demo" },
    summary: {
      sk: "Ukážka galerijného webu pre fotografa. Masonry mriežka, filter kategórií a lightbox ovládateľný klávesnicou.",
      en: "A gallery site demo for a photographer. Masonry grid, category filter and a keyboard-operated lightbox.",
    },
    intro: {
      sk: "Studio Lens je vymyslený ateliér. Galerijný web má inú úlohu než informačný — text má ustúpiť a fotografie majú dostať priestor. Rozhranie je preto zámerne tiché a takmer celé tmavé.",
      en: "Studio Lens is a fictional studio. A gallery site has a different job from an informational one — the text should step back and the photographs should take the space. The interface is deliberately quiet and almost entirely dark.",
    },
    highlights: {
      sk: [
        "Masonry mriežka, ktorá zvláda na výšku aj na šírku bez orezania",
        "Filter podľa kategórie s okamžitou odozvou",
        "Lightbox so šípkami, klávesou Escape a zachytením fokusu",
        "Rozhranie potlačené tak, aby neprekrývalo fotografie",
      ],
      en: [
        "A masonry grid that handles portrait and landscape without cropping",
        "Category filtering with instant response",
        "A lightbox with arrow keys, Escape and a focus trap",
        "An interface kept quiet so it never competes with the photographs",
      ],
    },
    capabilities: {
      sk: ["Masonry galéria", "Filter kategórií", "Lightbox", "Ovládanie klávesnicou", "Optimalizované obrázky", "Dopytový formulár"],
      en: ["Masonry gallery", "Category filter", "Lightbox", "Keyboard operation", "Optimised images", "Inquiry form"],
    },
  },
];

export function getProject(slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}
