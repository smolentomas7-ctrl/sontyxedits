import { fitness } from "@/config/images";
import type { ImageSlot } from "@/config/images";

export type GymClass = {
  id: string;
  name: string;
  duration: number;
  level: string;
  description: string;
  image: ImageSlot;
};

export const CLASSES: GymClass[] = [
  {
    id: "hiit",
    name: "HIIT 45",
    duration: 45,
    level: "Pokročilí",
    description:
      "Krátke intervaly na maximum, krátke pauzy. Najtvrdšia hodina v rozvrhu — prvýkrát príďte oddýchnutí.",
    image: fitness.classHiit,
  },
  {
    id: "cycling",
    name: "Indoor Cycling",
    duration: 50,
    level: "Všetky úrovne",
    description:
      "Stúpania, šprinty a tempo v rytme hudby. Odpor si riadite sami, takže hodina sadne začiatočníkovi aj pretekárovi.",
    image: fitness.classCycling,
  },
  {
    id: "yoga",
    name: "Vinyasa Joga",
    duration: 60,
    level: "Začiatočníci",
    description:
      "Plynulé prepojenie dychu a pohybu. Zameriavame sa na bedrá a chrbticu — vhodné po sedavom dni.",
    image: fitness.classYoga,
  },
  {
    id: "strength",
    name: "Silový tréning",
    duration: 60,
    level: "Mierne pokročilí",
    description:
      "Drep, mŕtvy ťah, tlak. Technika pod dohľadom trénera, váhy podľa vašich možností.",
    image: fitness.classStrength,
  },
];

export type Slot = { classId: string; time: string; full: boolean; free: number };

/**
 * Sample timetable keyed by JavaScript weekday (0 = Sunday).
 *
 * This is static demo data, not a real calendar: the same slots repeat every
 * week and the "full" flags are fixed so the booking flow can show a disabled
 * state. The UI states this explicitly.
 */
export const SLOTS_BY_WEEKDAY: Record<number, Slot[]> = {
  1: [
    { classId: "hiit", time: "06:30", full: false, free: 4 },
    { classId: "hiit", time: "18:00", full: true, free: 0 },
    { classId: "cycling", time: "17:00", full: false, free: 7 },
    { classId: "strength", time: "19:00", full: false, free: 3 },
  ],
  2: [
    { classId: "yoga", time: "08:00", full: false, free: 9 },
    { classId: "yoga", time: "18:30", full: true, free: 0 },
    { classId: "strength", time: "17:30", full: false, free: 5 },
    { classId: "cycling", time: "19:30", full: false, free: 2 },
  ],
  3: [
    { classId: "hiit", time: "06:30", full: false, free: 6 },
    { classId: "cycling", time: "17:00", full: false, free: 8 },
    { classId: "cycling", time: "18:30", full: true, free: 0 },
    { classId: "strength", time: "19:00", full: false, free: 4 },
  ],
  4: [
    { classId: "yoga", time: "08:00", full: false, free: 11 },
    { classId: "hiit", time: "18:00", full: false, free: 2 },
    { classId: "strength", time: "17:30", full: false, free: 6 },
  ],
  5: [
    { classId: "cycling", time: "07:00", full: false, free: 5 },
    { classId: "hiit", time: "17:00", full: false, free: 3 },
    { classId: "yoga", time: "18:30", full: false, free: 10 },
  ],
  6: [
    { classId: "yoga", time: "09:00", full: false, free: 12 },
    { classId: "strength", time: "10:30", full: false, free: 7 },
    { classId: "hiit", time: "11:00", full: true, free: 0 },
  ],
  0: [{ classId: "yoga", time: "10:00", full: false, free: 14 }],
};

export const TRAINERS = [
  {
    name: "Marek Dub",
    role: "Silový tréning, HIIT",
    bio: "Dvanásť rokov v posilňovni, z toho osem ako tréner. Špecializuje sa na techniku drepu a mŕtveho ťahu.",
    image: fitness.trainer1,
  },
  {
    name: "Lena Vrábľová",
    role: "Joga, mobilita",
    bio: "Vedie vinyasu a hodiny mobility. Pracuje najmä s ľuďmi, ktorí celý deň sedia za počítačom.",
    image: fitness.trainer2,
  },
  {
    name: "Pavol Hruška",
    role: "Cycling, kondícia",
    bio: "Bývalý cestný cyklista. Jeho hodiny majú povesť najtvrdších v rozvrhu a najlepšieho playlistu.",
    image: fitness.trainer3,
  },
];

export const MEMBERSHIPS = [
  {
    name: "Jednorazový vstup",
    price: "9 €",
    period: "za hodinu",
    features: ["Ktorákoľvek hodina", "Bez viazanosti", "Zapožičanie uteráka"],
    popular: false,
  },
  {
    name: "Mesačné",
    price: "59 €",
    period: "mesačne",
    features: [
      "Neobmedzené hodiny",
      "Rezervácia 7 dní dopredu",
      "Vstup do posilňovne",
      "Zrušenie kedykoľvek",
    ],
    popular: true,
  },
  {
    name: "Ročné",
    price: "540 €",
    period: "ročne",
    features: [
      "Všetko z mesačného",
      "Dva mesiace zadarmo",
      "Vstupná diagnostika",
      "Jeden osobný tréning",
    ],
    popular: false,
  },
];

export const WEEKDAYS = [
  { index: 1, label: "Pondelok" },
  { index: 2, label: "Utorok" },
  { index: 3, label: "Streda" },
  { index: 4, label: "Štvrtok" },
  { index: 5, label: "Piatok" },
  { index: 6, label: "Sobota" },
  { index: 0, label: "Nedeľa" },
];
