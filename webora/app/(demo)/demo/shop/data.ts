import { shop } from "@/config/images";
import type { ImageSlot } from "@/config/images";

export type Category = "vazy" | "textil" | "nabytok" | "osvetlenie" | "kuchyna";

export type Product = {
  slug: string;
  name: string;
  price: number;
  category: Category;
  short: string;
  description: string;
  /** First entry is the main image. */
  gallery: ImageSlot[];
  variants?: { label: string; options: string[] };
  material: string;
  dimensions: string;
};

export const CATEGORIES: { id: Category; label: string }[] = [
  { id: "vazy", label: "Vázy a keramika" },
  { id: "textil", label: "Textil" },
  { id: "nabytok", label: "Nábytok" },
  { id: "osvetlenie", label: "Osvetlenie" },
  { id: "kuchyna", label: "Kuchyňa" },
];

export const products: Product[] = [
  {
    slug: "vaza-fjord",
    name: "Váza Fjord",
    price: 68,
    category: "vazy",
    short: "Ručne točená kamenina s matnou glazúrou.",
    description:
      "Váza točená na kruhu v malej dielni. Každý kus má mierne odlišný tvar hrdla — je to znak ručnej práce, nie chyba. Matná glazúra je priedušná, takže váza drží vodu bez vnútorného náteru.",
    gallery: [shop.product1, shop.product1g1, shop.product1g2, shop.product1g3],
    variants: { label: "Veľkosť", options: ["Malá — 18 cm", "Stredná — 26 cm", "Veľká — 34 cm"] },
    material: "Kamenina, matná glazúra",
    dimensions: "⌀ 14 × 26 cm",
  },
  {
    slug: "stolicka-oslo",
    name: "Stolička Oslo",
    price: 149,
    category: "nabytok",
    short: "Masívny dub, okrúhle sedadlo, olejovaný povrch.",
    description:
      "Stolička z masívneho dubu s okrúhlym sedadlom a tromi nohami. Povrch je ošetrený tvrdým voskovým olejom, ktorý sa dá kedykoľvek obnoviť bez brúsenia celého kusu. Unesie 120 kg.",
    gallery: [shop.product2, shop.product2g1, shop.product2g2],
    variants: { label: "Povrch", options: ["Prírodný dub", "Dub morený na tmavo"] },
    material: "Masívny dub, tvrdý voskový olej",
    dimensions: "⌀ 34 × 45 cm",
  },
  {
    slug: "vankus-len",
    name: "Vankúš Len",
    price: 39,
    category: "textil",
    short: "Praný ľan, skrytý zips, výplň v cene.",
    description:
      "Obliečka z praného ľanu, ktorý je mäkký už pri prvom použití a praním sa ďalej zjemňuje. Zips je skrytý v spodnom šve. Vnútorný vankúš s perovou náplňou je súčasťou balenia.",
    gallery: [shop.product3, shop.product3g1, shop.product3g2, shop.product3g3],
    variants: { label: "Rozmer", options: ["40 × 40 cm", "50 × 50 cm", "60 × 40 cm"] },
    material: "100 % praný ľan",
    dimensions: "50 × 50 cm",
  },
  {
    slug: "lampa-kupol",
    name: "Lampa Kupol",
    price: 128,
    category: "osvetlenie",
    short: "Mosadzné tienidlo, stmievateľná, textilný kábel.",
    description:
      "Stolová lampa s tieneným mosadzným kupolom, ktorý nasmeruje svetlo nadol — vhodná na nočný stolík alebo pracovný stôl. Kábel je textilný, vypínač na šnúre. Objímka E27, žiarovka nie je súčasťou.",
    gallery: [shop.product4],
    material: "Mosadz, textilný kábel",
    dimensions: "⌀ 22 × 38 cm",
  },
  {
    slug: "misky-sada",
    name: "Misky Sada",
    price: 54,
    category: "kuchyna",
    short: "Štyri stohovateľné misky, vhodné do umývačky.",
    description:
      "Sada štyroch mištičiek rôznych veľkostí, ktoré sa dajú uložiť do seba. Znesú umývačku aj mikrovlnku. Glazúra je bez olova a kadmia.",
    gallery: [shop.product5],
    material: "Kamenina",
    dimensions: "⌀ 12 až 22 cm",
  },
  {
    slug: "karafa-sklo",
    name: "Karafa Sklo",
    price: 46,
    category: "kuchyna",
    short: "Fúkané sklo s dubovým uzáverom.",
    description:
      "Ručne fúkaná karafa s dubovým uzáverom a silikónovým tesnením. Objem 1 liter. Vhodná na vodu aj na studený čaj; do mrazničky nepatrí.",
    gallery: [shop.product6],
    material: "Fúkané sklo, dub",
    dimensions: "⌀ 10 × 27 cm, 1 l",
  },
  {
    slug: "svieca-blok",
    name: "Sviečka Blok",
    price: 24,
    category: "vazy",
    short: "Sójový vosk, bez vône, horí 40 hodín.",
    description:
      "Geometrická sviečka z lisovaného sójového vosku. Bez parfumácie, takže neprekáža pri jedle. Horí približne 40 hodín a vosk sa pri horení neprepadáva dovnútra.",
    gallery: [shop.product7],
    variants: { label: "Farba", options: ["Piesková", "Antracitová"] },
    material: "Sójový vosk, bavlnený knôt",
    dimensions: "9 × 9 × 14 cm",
  },
  {
    slug: "hodiny-orech",
    name: "Hodiny Orech",
    price: 92,
    category: "nabytok",
    short: "Orechová dyha, mosadzné ručičky, tichý strojček.",
    description:
      "Nástenné hodiny s telom z orechovej dyhy a mosadznými ručičkami bez číslic. Strojček je plynulý, takže netiká — vhodné aj do spálne. Na batériu AA.",
    gallery: [shop.product8],
    material: "Orechová dyha, mosadz",
    dimensions: "⌀ 30 × 4 cm",
  },
  {
    slug: "stolicka-barova",
    name: "Barová stolička Nord",
    price: 186,
    category: "nabytok",
    short: "Sedlové sedadlo, moriaci dub, výška 65 cm.",
    description:
      "Vyššia stolička so sedlovo tvarovaným sedadlom, ktoré je pohodlné aj bez operadla. Moreným dubom tmavšia než stolička Oslo, takže sa dá kombinovať ako kontrast.",
    gallery: [shop.product9],
    material: "Morený dub",
    dimensions: "⌀ 36 × 65 cm",
  },
];

export const PRICE_BOUNDS = { min: 0, max: 200 };

export function getProduct(slug: string): Product | undefined {
  return products.find((product) => product.slug === slug);
}

export function formatPrice(value: number): string {
  return `${value.toFixed(2).replace(".", ",")} €`;
}
