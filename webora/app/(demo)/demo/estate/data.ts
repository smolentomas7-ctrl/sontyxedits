import { estate } from "@/config/images";
import type { ImageSlot } from "@/config/images";

export type Deal = "predaj" | "prenajom";
export type PropertyType = "byt" | "dom" | "chata";

export type Property = {
  slug: string;
  title: string;
  location: string;
  city: string;
  price: number;
  deal: Deal;
  type: PropertyType;
  rooms: number;
  area: number;
  landArea?: number;
  year: number;
  energy: string;
  description: string;
  features: string[];
  main: ImageSlot;
  gallery: ImageSlot[];
};

export const properties: Property[] = [
  {
    slug: "pobrezny-dom-balkony",
    title: "Pobrežný dom s tromi balkónmi",
    location: "Pri pláži",
    city: "Senec",
    price: 745000,
    deal: "predaj",
    type: "dom",
    rooms: 6,
    area: 268,
    landArea: 640,
    year: 2019,
    energy: "A",
    description:
      "Trojpodlažný dom s panoramatickým výhľadom na vodu z každého podlažia. Otvorený denný priestor, tri balkóny a priamy prístup na pláž cez drevený chodník.",
    features: [
      "Výhľad na vodu zo všetkých podlaží",
      "Tri balkóny a terasa",
      "Podlahové kúrenie",
      "Garáž pre dve autá",
      "Rekuperácia",
    ],
    main: estate.listing1,
    gallery: [
      estate.listing1g1,
      estate.listing1g2,
      estate.listing1g3,
      estate.listing1g4,
    ],
  },
  {
    slug: "tehlovy-rodinny-dom",
    title: "Tehlový rodinný dom so záhradou",
    location: "Vilová štvrť",
    city: "Bratislava — Koliba",
    price: 598000,
    deal: "predaj",
    type: "dom",
    rooms: 5,
    area: 210,
    landArea: 820,
    year: 1968,
    energy: "C",
    description:
      "Udržiavaný tehlový dom v pokojnej vilovej štvrti. Pôvodné prvky — kamenný krb, drevené obloženie pracovne — zostali zachované, kuchyňa a kúpeľne prešli rekonštrukciou v roku 2021.",
    features: [
      "Vzrastlá záhrada 820 m²",
      "Kamenný krb",
      "Pracovňa s dreveným obkladom",
      "Rekonštruované kúpeľne (2021)",
      "Podpivničené",
    ],
    main: estate.listing2,
    gallery: [
      estate.listing2g1,
      estate.listing2g2,
      estate.listing2g3,
      estate.listing2g4,
    ],
  },
  {
    slug: "dom-beton-sklo",
    title: "Dom z betónu a skla",
    location: "Nová štvrť",
    city: "Bratislava — Záhorská Bystrica",
    price: 812000,
    deal: "predaj",
    type: "dom",
    rooms: 5,
    area: 245,
    landArea: 710,
    year: 2022,
    energy: "A0",
    description:
      "Súčasná architektúra s pohľadovým betónom a celosklenenou obývacou časťou. Minimalistický interiér, mramorový kuchynský ostrov a kúpeľňa s voľne stojacou vaňou.",
    features: [
      "Pohľadový betón",
      "Celosklenená obývacia časť",
      "Bazén",
      "Mramorový ostrov v kuchyni",
      "Inteligentné ovládanie domu",
    ],
    main: estate.listing3,
    gallery: [
      estate.listing3g1,
      estate.listing3g2,
      estate.listing3g3,
      estate.listing3g4,
    ],
  },
  {
    slug: "drevodom-v-lese",
    title: "Drevodom na okraji lesa",
    location: "Pri lese",
    city: "Modra",
    price: 465000,
    deal: "predaj",
    type: "dom",
    rooms: 4,
    area: 178,
    landArea: 1100,
    year: 2020,
    energy: "A",
    description:
      "Drevostavba s cédrovým obkladom priamo na hranici lesa. Veľké presklenia na juh, terasa po celej dĺžke a pozemok, ktorý nikto neuvidí z cesty.",
    features: ["Cédrový obklad", "Pozemok 1 100 m²", "Terasa po celej dĺžke", "Krb na drevo"],
    main: estate.listing4,
    gallery: [],
  },
  {
    slug: "cierna-chata",
    title: "Čierna chata v zeleni",
    location: "Záhradkárska oblasť",
    city: "Pezinok",
    price: 189000,
    deal: "predaj",
    type: "chata",
    rooms: 2,
    area: 64,
    landArea: 480,
    year: 2021,
    energy: "B",
    description:
      "Malá novostavba s čiernym fasádnym obkladom a plechovou strechou. Jedna veľká obytná miestnosť s galériou na spanie. Vhodná na víkendy aj na celoročné bývanie.",
    features: ["Novostavba 2021", "Galéria na spanie", "Zateplená na celoročné bývanie"],
    main: estate.listing5,
    gallery: [],
  },
  {
    slug: "strecny-byt-terasa",
    title: "Strešný byt s terasou a vírivkou",
    location: "Centrum",
    city: "Bratislava — Staré Mesto",
    price: 2400,
    deal: "prenajom",
    type: "byt",
    rooms: 4,
    area: 156,
    year: 2023,
    energy: "A",
    description:
      "Posledné podlažie novostavby s terasou po obvode, vírivkou a výhľadom na celé mesto. Zariadený, k dispozícii od budúceho mesiaca. Cena je mesačný nájom bez energií.",
    features: [
      "Terasa po obvode",
      "Vírivka",
      "Dve parkovacie státia",
      "Zariadený",
      "Recepcia v budove",
    ],
    main: estate.listing6,
    gallery: [],
  },
];

export const AGENTS = [
  {
    name: "Jana Hrušková",
    role: "Konateľka, rezidenčné nehnuteľnosti",
    phone: "+421 900 000 001",
    email: "hruskova@domovreality.example",
    image: estate.agent1,
  },
  {
    name: "Tomáš Ondrejka",
    role: "Realitný maklér, novostavby",
    phone: "+421 900 000 002",
    email: "ondrejka@domovreality.example",
    image: estate.agent2,
  },
];

export const TYPE_LABELS: Record<PropertyType, string> = {
  byt: "Byt",
  dom: "Dom",
  chata: "Chata",
};

export const DEAL_LABELS: Record<Deal, string> = {
  predaj: "Na predaj",
  prenajom: "Na prenájom",
};

export function getProperty(slug: string): Property | undefined {
  return properties.find((property) => property.slug === slug);
}

export function formatEur(value: number): string {
  return new Intl.NumberFormat("sk-SK", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function priceLabel(property: Property): string {
  return property.deal === "prenajom"
    ? `${formatEur(property.price)} / mesiac`
    : formatEur(property.price);
}
