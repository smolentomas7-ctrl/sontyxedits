import { reviews as reviewPhotos, type ImageSlot } from "@/config/images";

/**
 * Homepage reviews.
 *
 * Only genuine reviews are shown on the site: entries with `sample: true` are
 * never rendered (see PUBLISHED_REVIEWS at the bottom).
 *
 * The five `sample` entries are invented placeholders — the people,
 * companies and positions do not exist. They are kept here only as slots to
 * be replaced by real reviews: edit an entry in place with what the client
 * approved (`name`, `company`, `position`, `text`), swap its photo in
 * config/images.ts (`reviews` group) or drop `photo` to show initials, and
 * set `sample: false`. It then appears on the site with no label.
 *
 * A real client's card must carry the client's own words. A draft the client
 * has not approved yet sets `awaitingApproval: true`, which also keeps the
 * card off the site.
 *
 * Reviews are written in the reviewer's own language and are shown as-is in
 * both site locales, so they are kept here rather than in the dictionaries.
 */

export type CountryCode = "SK" | "CZ" | "GB" | "US";

export type Review = {
  id: string;
  /** Language the review is written in; set as `lang` on the quote. */
  lang: "sk" | "cs" | "en";
  name: string;
  country: CountryCode;
  /** PLACEHOLDER until a real client supplies it. */
  company: string;
  /** PLACEHOLDER until a real client supplies it. */
  position: string;
  rating: 5;
  /** The client's own words. Empty = not shown on the site yet. */
  text: string;
  /** Portrait; without one the card shows the reviewer's initials. */
  photo?: ImageSlot;
  /** True for an invented placeholder. Placeholders are never rendered. */
  sample: boolean;
  /** Draft text the client has not approved yet. Not rendered while true. */
  awaitingApproval?: boolean;
};

/** Country names in the country's own language, matching each review. */
export const COUNTRY_NAMES: Record<CountryCode, string> = {
  SK: "Slovensko",
  CZ: "Česká republika",
  GB: "United Kingdom",
  US: "United States",
};

export const REVIEWS: Review[] = [
  {
    id: "sk-01",
    lang: "sk",
    name: "Jakub Šimko",
    country: "SK",
    company: "Forma Interiér",
    position: "Zakladateľ a dizajnér interiérov",
    rating: 5,
    text: "Starý web sme mali ešte z čias, keď sa všetko pozeralo na počítači. Dnes nám väčšina dopytov príde z mobilu a konečne to tak aj vyzerá. Páčilo sa mi, že som vždy vedel, na čom sa práve robí.",
    photo: reviewPhotos.sk01,
    sample: true,
  },
  {
    id: "sk-02",
    lang: "sk",
    name: "Peter Valach",
    country: "SK",
    company: "Valach & Partneri",
    position: "Konateľ",
    rating: 5,
    text: "Nečakal som zázraky, skôr to, aby firma na webe pôsobila tak seriózne, ako naozaj pracujeme. To sa podarilo. Komunikácia bola vecná, termíny sedeli a ani zmeny na poslednú chvíľu neboli problém.",
    photo: reviewPhotos.sk02,
    sample: true,
  },
  {
    id: "cz-01",
    lang: "cs",
    name: "Lukáš Dvořák",
    country: "CZ",
    company: "Dvořák Reality",
    position: "Majitel a realitní makléř",
    rating: 5,
    text: "Upřímně jsem měl obavy, jestli spolupráce na dálku bude fungovat. Nakonec to šlo hladčeji než s agenturou, se kterou jsem dělal dřív. Web je rychlý, na mobilu vypadá skvěle a klienti se mě teď ptají, kdo nám ho dělal.",
    photo: reviewPhotos.cz01,
    sample: true,
  },
  {
    id: "en-01",
    lang: "en",
    name: "Daniel Okafor",
    country: "GB",
    company: "Okafor Property Services",
    position: "Founder & Director",
    rating: 5,
    text: "We're a small team up against much bigger firms, and the old site made that obvious. Webora fixed it without overcomplicating anything. Honest advice on what we didn't need, a clear plan, and a site that loads fast on every phone we tried.",
    photo: reviewPhotos.en01,
    sample: true,
  },
  {
    id: "en-02",
    lang: "en",
    name: "Michael Turner",
    country: "US",
    company: "Turner Builders",
    position: "Owner & General Manager",
    rating: 5,
    text: "Straightforward to work with. They asked the right questions up front, kept me posted without me having to chase, and delivered a site I'm happy to send customers to.",
    photo: reviewPhotos.en02,
    sample: true,
  },
  {
    // Real client: M.I. Autoservis (the M.I.Auto site in this repo).
    // DRAFT WORDING: `text` was written by Webora and sent to Ivan Kubis for
    // sign-off. The owner chose to publish it before that confirmation came
    // back (2026-10-16). If Ivan changes anything, replace `text` with his
    // version; if he declines, set `awaitingApproval: true` to hide the card.
    id: "sk-miauto",
    lang: "sk",
    name: "Ivan Kubis",
    country: "SK",
    company: "M.I. Autoservis s.r.o., Ružomberok",
    position: "Spolumajiteľ",
    rating: 5,
    text: "Chceli sme stránku, kde zákazník hneď vidí, čo robíme a kde nás nájde. Webora to vzala od začiatku do konca, pýtali sa na veci, ktoré by mi samému nenapadli, a na mobile to konečne vyzerá tak, ako má. Ozývajú sa nám ľudia, ktorí nás našli cez web.",
    photo: reviewPhotos.skMiauto,
    sample: false,
  },
];

/** Reviews shown on the site: genuine, named, with text, and approved. */
export const PUBLISHED_REVIEWS = REVIEWS.filter(
  (review) => !review.sample && review.name && review.text.trim() && !review.awaitingApproval,
);
