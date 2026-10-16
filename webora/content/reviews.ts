import { reviews as reviewPhotos, type ImageSlot } from "@/config/images";

/**
 * Homepage reviews — SAMPLE CONTENT.
 *
 * Every entry below is demonstration content written to show how the section
 * will look. The people, companies and positions are placeholders, not
 * Webora clients, and the page labels them as samples. Nothing here may be
 * presented as a verified or real testimonial.
 *
 * To publish a genuine review, edit its entry in place: replace `name`,
 * `company`, `position` and `text` with what the client approved, swap the
 * photo in config/images.ts (`reviews` group), and set `sample: false`. Once
 * every entry is genuine, the sample note above the cards disappears on its
 * own (see components/marketing/Testimonials.tsx).
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
  text: string;
  photo: ImageSlot;
  /** True while the entry is demonstration content. */
  sample: boolean;
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
];
