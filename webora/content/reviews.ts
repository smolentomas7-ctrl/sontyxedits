import { reviews as reviewPhotos, type ImageSlot } from "@/config/images";

/**
 * Homepage reviews — SAMPLE CONTENT.
 *
 * Every entry below is demonstration content written to show how the section
 * will look. The people, companies and positions are placeholders, not
 * Webora clients, and the page labels them as samples. Nothing here may be
 * presented as a verified or real testimonial.
 *
 * The "Ukážka" label is per review: a card with `sample: true` carries it,
 * a card with `sample: false` renders with no label at all. The note above
 * the grid only shows while at least one visible card is a sample, so it
 * disappears on its own once every sample has been replaced.
 *
 * To publish a genuine review, edit its entry in place: replace `name`,
 * `company`, `position` and `text` with what the client approved, swap the
 * photo in config/images.ts (`reviews` group) or drop `photo` to show the
 * client's initials, and set `sample: false`.
 *
 * A real client's card must carry the client's own words. Until they arrive,
 * leave `text` empty: entries without text are kept here but not rendered.
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
  {
    // Real client (the M.I.Auto site in this repo). Awaiting their own
    // wording: fill in `name`, `position` and `text` with what they approved.
    // Hidden until `text` is set.
    id: "sk-miauto",
    lang: "sk",
    name: "",
    country: "SK",
    company: "M.I.Auto s.r.o.",
    position: "",
    rating: 5,
    text: "",
    sample: false,
  },
];

/** Reviews ready to show: every entry that has the reviewer's name and words. */
export const PUBLISHED_REVIEWS = REVIEWS.filter((review) => review.name && review.text.trim());
