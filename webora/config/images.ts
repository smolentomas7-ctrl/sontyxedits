/**
 * EVERY image reference in the project lives here, keyed by the slot name from
 * the original asset request. Swap any image by editing one line below.
 *
 * All slots are currently filled by user-supplied files in public/assets/.
 * Nothing is on stock. To move a slot to stock, replace the `src` with an
 * Unsplash URL — next.config.ts already allows images.unsplash.com.
 *
 * Dimensions are the real intrinsic size of each file on disk, so next/image
 * can reserve layout space without a round trip.
 */

export type ImageSlot = {
  /** Path under /public, or an absolute https URL for stock. */
  src: string;
  width: number;
  height: number;
  /** Meaningful alt text. Empty string marks a purely decorative image. */
  alt: string;
};

/* ============================================================
   GROUP 1 — BRAND
   ============================================================ */

export const brand = {
  /** 1.1 Logo, cropped from the supplied JPEG, white keyed to transparent. */
  logo: {
    src: "/assets/brand/webora-logo.png",
    width: 828,
    height: 262,
    alt: "Webora",
  },
  /** 1.1 Same logo with the navy wordmark recolored for dark backgrounds. */
  logoLight: {
    src: "/assets/brand/webora-logo-light.png",
    width: 828,
    height: 262,
    alt: "Webora",
  },
  /** 1.2 Founder portrait — About page. */
  /** 1.3 Studio photo — open-plan workspace. */
  /**
   * Workspace photography. Both slots are defined and ready but currently
   * unplaced: the About page that used them was removed, and the contact area
   * is deliberately kept to the two contact options with no decoration.
   */
  studio1: {
    src: "/assets/brand/webora-studio-01.jpg",
    width: 1200,
    height: 896,
    alt: "Otvorený pracovný priestor štúdia s pracovnými stolmi a monitormi",
  },
  /** 1.3 Studio photo — meeting room with a wall of wireframes. */
  studio2: {
    src: "/assets/brand/webora-studio-02.jpg",
    width: 1200,
    height: 896,
    alt: "Zasadacia miestnosť so stenou plnou wireframov a návrhov",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 2 — MARKETING SITE
   ============================================================ */

export const marketing = {
  /** 2.1 Abstract dark hero texture, sits behind the homepage headline. */
  heroTexture: {
    src: "/assets/marketing/hero-texture.jpg",
    width: 1376,
    height: 768,
    alt: "",
  },
  /** 2.2 Blog cover — what a website should cost. */
  blogCost: {
    src: "/assets/marketing/blog-01-cost.jpg",
    width: 1376,
    height: 768,
    alt: "Ilustrácia responzívneho webu na notebooku, tablete a telefóne",
  },
  /** 2.2 Blog cover — what to prepare before ordering. */
  blogPrepare: {
    src: "/assets/marketing/blog-02-prepare.jpg",
    width: 1376,
    height: 768,
    alt: "Ilustrácia digitalizácie malej firmy",
  },
  /** 2.2 Blog cover — Google Business Profile. */
  blogGbp: {
    src: "/assets/marketing/blog-03-gbp.jpg",
    width: 1376,
    height: 768,
    alt: "Ilustrácia zabezpečenia a dôveryhodnosti webu",
  },
  /** 2.2 Blog cover — signs you need a redesign. */
  blogRedesign: {
    src: "/assets/marketing/blog-04-redesign.jpg",
    width: 1376,
    height: 768,
    alt: "Ilustrácia wireframov a návrhu používateľského rozhrania",
  },
  /** 2.2 Blog cover — writing your own copy. */
  blogCopy: {
    src: "/assets/marketing/blog-05-copy.jpg",
    width: 1376,
    height: 768,
    alt: "Ilustrácia rýchlosti načítania webovej stránky",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 3 — DEMO: BISTRO
   ============================================================ */

export const bistro = {
  /** 3.1 Hero — dining room interior. */
  hero: {
    src: "/assets/bistro/bistro-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Interiér bistra so zelenými sedačkami a mosadzným barom",
  },
  /** 3.4 About — barista behind the espresso machine. */
  about: {
    src: "/assets/bistro/bistro-about.jpg",
    width: 896,
    height: 1200,
    alt: "Barista za espresso kávovarom",
  },
  /** 3.2 Menu items, 1:1. */
  menu1: {
    src: "/assets/bistro/bistro-menu-01.jpg",
    width: 1024,
    height: 1024,
    alt: "Lístkové pečivo s lesným ovocím na mramore",
  },
  menu2: {
    src: "/assets/bistro/bistro-menu-02.jpg",
    width: 1024,
    height: 1024,
    alt: "Avokádový toast so zastretým vajcom",
  },
  menu3: {
    src: "/assets/bistro/bistro-menu-03.jpg",
    width: 1024,
    height: 1024,
    alt: "Šalátová misa s čerstvou zeleninou",
  },
  menu4: {
    src: "/assets/bistro/bistro-menu-04.jpg",
    width: 1024,
    height: 1024,
    alt: "Pečený losos na hráškovom pyré",
  },
  menu5: {
    src: "/assets/bistro/bistro-menu-05.jpg",
    width: 1024,
    height: 1024,
    alt: "Cappuccino s latte art",
  },
  menu6: {
    src: "/assets/bistro/bistro-menu-06.jpg",
    width: 1024,
    height: 1024,
    alt: "Kokteil v krištáľovom pohári",
  },
  /** 3.3 Gallery, 3:2. */
  gallery1: {
    src: "/assets/bistro/bistro-gallery-01.jpg",
    width: 1200,
    height: 896,
    alt: "Osvetlený vchod do bistra za súmraku",
  },
  gallery2: {
    src: "/assets/bistro/bistro-gallery-02.jpg",
    width: 1200,
    height: 896,
    alt: "Kuchár dokončuje tanier v kuchyni",
  },
  gallery3: {
    src: "/assets/bistro/bistro-gallery-03.jpg",
    width: 1200,
    height: 896,
    alt: "Hostia pri káve a rozhovore",
  },
  gallery4: {
    src: "/assets/bistro/bistro-gallery-04.jpg",
    width: 1200,
    height: 896,
    alt: "Barista nalieva mlieko do šálky",
  },
  gallery5: {
    src: "/assets/bistro/bistro-gallery-05.jpg",
    width: 1200,
    height: 896,
    alt: "Prestretý stôl pri sviečkach",
  },
  gallery6: {
    src: "/assets/bistro/bistro-gallery-06.jpg",
    width: 1200,
    height: 896,
    alt: "Bar s pohármi a fľašami v protisvetle",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 4 — DEMO: SHOP
   ============================================================ */

export const fitness = {
  /** 5.1 Hero. */
  hero: {
    src: "/assets/fitness/fitness-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Interiér posilňovne s betónovými stenami a stojanom na činky",
  },
  /** 5.2 Class photos. */
  classHiit: {
    src: "/assets/fitness/fitness-class-01-hiit.jpg",
    width: 1200,
    height: 896,
    alt: "Skupinový HIIT tréning",
  },
  classCycling: {
    src: "/assets/fitness/fitness-class-02-cycling.jpg",
    width: 1200,
    height: 896,
    alt: "Hodina indoor cyclingu",
  },
  classYoga: {
    src: "/assets/fitness/fitness-class-03-yoga.jpg",
    width: 1200,
    height: 896,
    alt: "Hodina jogy vo svetlej sále",
  },
  classStrength: {
    src: "/assets/fitness/fitness-class-04-strength.jpg",
    width: 1200,
    height: 896,
    alt: "Silový tréning s činkami",
  },
  /** 5.3 Trainer portraits. */
  trainer1: {
    src: "/assets/fitness/fitness-trainer-01.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét trénera v posilňovni",
  },
  trainer2: {
    src: "/assets/fitness/fitness-trainer-02.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét lektorky jogy",
  },
  trainer3: {
    src: "/assets/fitness/fitness-trainer-03.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét skúseného osobného trénera",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 6 — DEMO: BUILD
   ============================================================ */

export const build = {
  /** 6.1 Hero. */
  hero: {
    src: "/assets/build/build-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Moderný rodinný dom za súmraku",
  },
  /**
   * 6.2 Before/after pairs. Both images in a pair share identical dimensions
   * so the comparison slider lines up. The supplied files had "BEFORE" and
   * "AFTER" captions burned into the top of the frame; the top 15% was cropped
   * off both halves of each pair by an equal amount, which removes the caption
   * and preserves alignment.
   */
  ba1Before: {
    src: "/assets/build/build-beforeafter-01-before.jpg",
    width: 1376,
    height: 653,
    alt: "Pôjd pred rekonštrukciou, plný škatúľ a odpadu",
  },
  ba1After: {
    src: "/assets/build/build-beforeafter-01-after.jpg",
    width: 1376,
    height: 653,
    alt: "Ten istý pôjd po rekonštrukcii, prerobený na spálňu",
  },
  ba2Before: {
    src: "/assets/build/build-beforeafter-02-before.jpg",
    width: 1376,
    height: 653,
    alt: "Zastaraná kuchyňa pred rekonštrukciou",
  },
  ba2After: {
    src: "/assets/build/build-beforeafter-02-after.jpg",
    width: 1376,
    height: 653,
    alt: "Kuchyňa po rekonštrukcii s novou linkou",
  },
  /** 6.3 Completed projects gallery. */
  project1: {
    src: "/assets/build/build-project-01.jpg",
    width: 1200,
    height: 896,
    alt: "Obnovená fasáda historického domu",
  },
  project2: {
    src: "/assets/build/build-project-02.jpg",
    width: 1200,
    height: 896,
    alt: "Dokončená tehlová prístavba",
  },
  project3: {
    src: "/assets/build/build-project-03.jpg",
    width: 1200,
    height: 896,
    alt: "Dokončený obytný priestor",
  },
  project4: {
    src: "/assets/build/build-project-04.jpg",
    width: 1200,
    height: 896,
    alt: "Presklená zimná záhrada s výhľadom do záhrady",
  },
  project5: {
    src: "/assets/build/build-project-05.jpg",
    width: 1200,
    height: 896,
    alt: "Viacúrovňová terasa s ohniskom",
  },
  project6: {
    src: "/assets/build/build-project-06.jpg",
    width: 1200,
    height: 896,
    alt: "Dláždená príjazdová cesta a kamenný múrik",
  },
  /**
   * 6.2 pair 3 — only the "before" was supplied; no matching "after" exists,
   * so this frame is used in the projects gallery instead of a third slider.
   */
  derelict: {
    src: "/assets/build/build-beforeafter-03-before.jpg",
    width: 1376,
    height: 768,
    alt: "Schátraný dom pred obnovou",
  },
  /** 6.4 Service images. */
  serviceMasonry: {
    src: "/assets/build/build-service-01-masonry.jpg",
    width: 1024,
    height: 1024,
    alt: "Murár kladie tehlu do malty",
  },
  serviceRoofing: {
    src: "/assets/build/build-service-02-roofing.jpg",
    width: 1024,
    height: 1024,
    alt: "Pokrývač kladie bridlicovú krytinu",
  },
  serviceInteriors: {
    src: "/assets/build/build-service-03-interiors.jpg",
    width: 1024,
    height: 1024,
    alt: "Izometrická vizualizácia obývacej izby",
  },
  serviceRenovations: {
    src: "/assets/build/build-service-04-renovations.jpg",
    width: 1024,
    height: 1024,
    alt: "Izometrická ilustrácia rekonštrukcie domu",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 7 — DEMO: LEGAL
   ============================================================ */

export const legal = {
  /**
   * 7.1 Hero. The supplied photo has "THORNE & ASSOCIATES" signage on the
   * building, which is not the demo firm's name, so the hero crops to the
   * upper facade and the signage is pushed out of frame by object-position.
   */
  hero: {
    src: "/assets/legal/legal-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Presklená kancelárska budova za súmraku",
  },
  /** 7.2 Attorney portraits, consistent grey studio backdrop. */
  attorney1: {
    src: "/assets/legal/legal-attorney-01.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét staršieho advokáta v tmavomodrom obleku",
  },
  attorney2: {
    src: "/assets/legal/legal-attorney-02.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét advokátky v tmavomodrom saku",
  },
  attorney3: {
    src: "/assets/legal/legal-attorney-03.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét advokáta v tmavomodrom obleku",
  },
  /** 7.3 Office interiors. */
  office1: {
    src: "/assets/legal/legal-office-01.jpg",
    width: 1200,
    height: 896,
    alt: "Kancelária s orechovým obkladom a knižnicou",
  },
  office2: {
    src: "/assets/legal/legal-office-02.jpg",
    width: 1200,
    height: 896,
    alt: "Zasadacia miestnosť so sklenenou doskou stola",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 8 — DEMO: LENS
   ============================================================ */

export const lens = {
  /** 8.1 Hero — strongest single frame. */
  hero: {
    src: "/assets/lens/lens-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Turista na vrchole hory nad morom oblakov pri východe slnka",
  },
  /** 8.3 Photographer portrait. */
  about: {
    src: "/assets/lens/lens-about.jpg",
    width: 896,
    height: 1200,
    alt: "Fotografka s fotoaparátom vo svojom ateliéri",
  },
  /** 8.2 Portfolio — portrait. */
  portrait1: {
    src: "/assets/lens/lens-portrait-01.jpg",
    width: 768,
    height: 1376,
    alt: "Editoriálny portrét s kovovým make-upom",
  },
  portrait2: {
    src: "/assets/lens/lens-portrait-02.jpg",
    width: 896,
    height: 1200,
    alt: "Čiernobiely portrét staršieho muža",
  },
  portrait3: {
    src: "/assets/lens/lens-portrait-03.jpg",
    width: 1024,
    height: 1024,
    alt: "Smejúce sa dieťa na lúke s kvetmi",
  },
  /** 8.2 Portfolio — wedding. */
  wedding1: {
    src: "/assets/lens/lens-wedding-01.jpg",
    width: 1376,
    height: 768,
    alt: "Nevesta a ženích sa smejú pri svadobnom stole",
  },
  wedding2: {
    src: "/assets/lens/lens-wedding-02.jpg",
    width: 1200,
    height: 896,
    alt: "Svadobný obrad v kamennej katedrále",
  },
  wedding3: {
    src: "/assets/lens/lens-wedding-03.jpg",
    width: 1024,
    height: 1024,
    alt: "Snubné prstene na saténovej stuhe",
  },
  /** 8.2 Portfolio — product. */
  product1: {
    src: "/assets/lens/lens-product-01.jpg",
    width: 1024,
    height: 1024,
    alt: "Hodinky so skeletovým ciferníkom na tmavom podklade",
  },
  product2: {
    src: "/assets/lens/lens-product-02.jpg",
    width: 1200,
    height: 896,
    alt: "Bezdrôtový reproduktor na betónovej doske",
  },
  product3: {
    src: "/assets/lens/lens-product-03.jpg",
    width: 1200,
    height: 896,
    alt: "Zákuskový dezert s malinovou polevou",
  },
  /** 8.2 Portfolio — landscape. */
  landscape1: {
    src: "/assets/lens/lens-landscape-01.jpg",
    width: 1376,
    height: 768,
    alt: "Skalnaté pobrežie za súmraku s dlhou expozíciou",
  },
  landscape2: {
    src: "/assets/lens/lens-landscape-02.jpg",
    width: 1024,
    height: 1024,
    alt: "Púštne duny pri západe slnka",
  },
  landscape3: {
    src: "/assets/lens/lens-landscape-03.jpg",
    width: 1200,
    height: 896,
    alt: "Hmlistý jesenný les",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   GROUP 9 — DEMO: ESTATE
   ============================================================ */

export const estate = {
  /** 9.1 Hero. */
  hero: {
    src: "/assets/estate/estate-hero.jpg",
    width: 1376,
    height: 768,
    alt: "Moderná vila s bazénom za súmraku",
  },
  /** 9.2 Listing 1 main + 9.3 gallery. */
  listing1: {
    src: "/assets/estate/estate-listing-01.jpg",
    width: 1200,
    height: 896,
    alt: "Biely pobrežný dom s balkónmi pri mori",
  },
  listing1g1: {
    src: "/assets/estate/estate-listing-01-gallery-01.jpg",
    width: 1200,
    height: 896,
    alt: "Svetlá obývacia izba s výhľadom na more",
  },
  listing1g2: {
    src: "/assets/estate/estate-listing-01-gallery-02.jpg",
    width: 1200,
    height: 896,
    alt: "Kuchyňa s ostrovom a výhľadom na pláž",
  },
  listing1g3: {
    src: "/assets/estate/estate-listing-01-gallery-03.jpg",
    width: 1200,
    height: 896,
    alt: "Hlavná spálňa v pobrežnom štýle",
  },
  listing1g4: {
    src: "/assets/estate/estate-listing-01-gallery-04.jpg",
    width: 1200,
    height: 896,
    alt: "Terasa s ležadlami pri západe slnka",
  },
  /** 9.2 Listing 2 main + 9.3 gallery. */
  listing2: {
    src: "/assets/estate/estate-listing-02.jpg",
    width: 1200,
    height: 896,
    alt: "Tehlový rodinný dom so záhradou",
  },
  listing2g1: {
    src: "/assets/estate/estate-listing-02-gallery-01.jpg",
    width: 1200,
    height: 896,
    alt: "Obývacia izba s kamenným krbom",
  },
  listing2g2: {
    src: "/assets/estate/estate-listing-02-gallery-02.jpg",
    width: 1200,
    height: 896,
    alt: "Vidiecka kuchyňa s dreveným stolom",
  },
  listing2g3: {
    src: "/assets/estate/estate-listing-02-gallery-03.jpg",
    width: 1200,
    height: 896,
    alt: "Raňajkový kút s lavicou pri okne",
  },
  listing2g4: {
    src: "/assets/estate/estate-listing-02-gallery-04.jpg",
    width: 1200,
    height: 896,
    alt: "Pracovňa s tmavým dreveným obkladom",
  },
  /** 9.2 Listing 3 main + 9.3 gallery. */
  listing3: {
    src: "/assets/estate/estate-listing-03.jpg",
    width: 1200,
    height: 896,
    alt: "Moderný dom z betónu a skla",
  },
  listing3g1: {
    src: "/assets/estate/estate-listing-03-gallery-01.jpg",
    width: 1200,
    height: 896,
    alt: "Minimalistická obývacia izba s bielymi stenami",
  },
  listing3g2: {
    src: "/assets/estate/estate-listing-03-gallery-02.jpg",
    width: 1200,
    height: 896,
    alt: "Moderná kuchyňa s mramorovým ostrovom",
  },
  listing3g3: {
    src: "/assets/estate/estate-listing-03-gallery-03.jpg",
    width: 1200,
    height: 896,
    alt: "Hlavná spálňa s veľkými oknami",
  },
  listing3g4: {
    src: "/assets/estate/estate-listing-03-gallery-04.jpg",
    width: 1200,
    height: 896,
    alt: "Kúpeľňa s voľne stojacou vaňou a sprchovým kútom",
  },
  /** 9.2 Listings 4–6, main photo only. */
  listing4: {
    src: "/assets/estate/estate-listing-04.jpg",
    width: 1200,
    height: 896,
    alt: "Drevený dom v lese",
  },
  listing5: {
    src: "/assets/estate/estate-listing-05.jpg",
    width: 1200,
    height: 896,
    alt: "Malá čierna chata v zeleni",
  },
  listing6: {
    src: "/assets/estate/estate-listing-06.jpg",
    width: 1200,
    height: 896,
    alt: "Strešný byt s terasou a výhľadom na mesto",
  },
  /** 9.4 Agent portraits. */
  agent1: {
    src: "/assets/estate/estate-agent-01.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét realitnej maklérky v kancelárii",
  },
  agent2: {
    src: "/assets/estate/estate-agent-02.jpg",
    width: 896,
    height: 1200,
    alt: "Portrét realitného makléra v interiéri domu",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   CLIENT WORK — M.I.Auto s.r.o. (autoservis, Ružomberok)
   Real project. The screenshots are captures of the delivered site; the
   photography is the client's own, reused from their asset set.
   ============================================================ */

export const miauto = {
  /** Full-page captures of the delivered site, 1440x900 at 1.5x. */
  shotHome: {
    src: "/assets/miauto/miauto-shot-home.webp",
    width: 2160,
    height: 1350,
    alt: "Domovská stránka webu M.I.Auto s veľkou fotografiou dielne a výzvou zavolať do servisu",
  },
  shotServices: {
    src: "/assets/miauto/miauto-shot-services.webp",
    width: 2160,
    height: 1350,
    alt: "Stránka Služby na webe M.I.Auto s rozpisom jednotlivých servisných úkonov",
  },
  shotDetail: {
    src: "/assets/miauto/miauto-shot-detail.webp",
    width: 2160,
    height: 1350,
    alt: "Detail služby Diagnostika vozidiel na webe M.I.Auto",
  },
  shotContact: {
    src: "/assets/miauto/miauto-shot-contact.webp",
    width: 2160,
    height: 1350,
    alt: "Kontaktná stránka webu M.I.Auto s adresou a otváracími hodinami",
  },
  /** Mobile capture, 390x844 at 2x. */
  shotMobile: {
    src: "/assets/miauto/miauto-shot-mobile.webp",
    width: 780,
    height: 1688,
    alt: "Web M.I.Auto zobrazený na mobilnom telefóne",
  },
  /** The client's own photography. */
  hero: {
    src: "/assets/miauto/miauto-hero.webp",
    width: 1200,
    height: 800,
    alt: "Vozidlo zdvihnuté na dvojstĺpovom zdviháku v autoservise",
  },
  interior: {
    src: "/assets/miauto/miauto-about-interior.webp",
    width: 1200,
    height: 800,
    alt: "Interiér servisnej dielne M.I.Auto",
  },
  detail1: {
    src: "/assets/miauto/miauto-about-detail-01.webp",
    width: 1200,
    height: 800,
    alt: "Detail práce mechanika v dielni",
  },
  detail2: {
    src: "/assets/miauto/miauto-about-detail-02.webp",
    width: 1200,
    height: 800,
    alt: "Detail servisného vybavenia",
  },
  serviceDiagnostika: {
    src: "/assets/miauto/miauto-service-diagnostika.webp",
    width: 1200,
    height: 800,
    alt: "Mechanik s diagnostickým tabletom v aute",
  },
  serviceGeometria: {
    src: "/assets/miauto/miauto-service-geometria.webp",
    width: 1200,
    height: 800,
    alt: "Meranie geometrie kolies",
  },
  servicePneuservis: {
    src: "/assets/miauto/miauto-service-pneuservis.webp",
    width: 1200,
    height: 800,
    alt: "Práca s pneumatikami a diskami v pneuservise",
  },
} satisfies Record<string, ImageSlot>;

/* ============================================================
   PORTFOLIO PREVIEWS
   Each demo card on the marketing site uses the demo's own hero image,
   rendered inside a browser-chrome frame.
   ============================================================ */

export const demoPreviews = {
  miauto: miauto.shotHome,
  bistro: bistro.hero,
  fitness: fitness.hero,
  build: build.hero,
  legal: legal.hero,
  lens: lens.hero,
  estate: estate.hero,
} satisfies Record<string, ImageSlot>;

export const images = {
  brand,
  miauto,
  marketing,
  bistro,
  fitness,
  build,
  legal,
  lens,
  estate,
  demoPreviews,
};
