import type { ChatScript } from "./types";

/**
 * Scripted answers only — no model, no network. Every answer here must match
 * what the site itself says, so when the dictionary changes these change too.
 *
 * Voice is first-person singular to match the rest of the Slovak copy.
 *
 * No answer quotes a figure: there is no fixed price list, and inventing one
 * here would contradict the individual-pricing section on the homepage.
 */
export const chatSk: ChatScript = {
  /** Chips shown under the greeting. */
  initialSuggestions: ["pricing", "delivery", "included", "contact"],

  fallback: {
    id: "fallback",
    answer:
      "Na toto neviem odpovedať — mám pripravené odpovede len na bežné otázky. Napíšte mi e-mail na weboraeurope@gmail.com alebo cez WhatsApp a ozvem sa vám, zvyčajne do 24 hodín.",
    followUps: ["contact", "pricing", "delivery"],
    offerContact: true,
  },

  nodes: {
    pricing: {
      id: "pricing",
      label: "Koľko stojí web?",
      keywords: [
        "cena", "cenu", "ceny", "cenník", "cennik", "stoji", "stojí", "koľko", "kolko",
        "drahé", "drahe", "rozpočet", "rozpocet", "eur", "€", "platiť", "platit", "faktúra",
      ],
      answer:
        "Pevný cenník nemám. Každý web má iný rozsah, iné funkcie a iné podklady, takže cenu počítam individuálne podľa toho, čo konkrétne potrebujete. Keď mi opíšete zadanie, pošlem ponuku s pevnou cenou a termínom — aby ste vedeli, na čom ste, ešte pred začiatkom prác. Od čoho sa cena odvíja, som rozpísal v sekcii Cena na domovskej stránke.",
      followUps: ["included", "delivery", "contact"],
      offerContact: true,
    },

    delivery: {
      id: "delivery",
      label: "Dokedy to bude hotové?",
      keywords: [
        "dlho", "termín", "termin", "kedy", "rýchlo", "rychlo", "dokedy", "čas", "cas",
        "týždeň", "tyzden", "dni", "dodanie", "stihnete",
      ],
      answer:
        "Jednostránkový web zvládnem zvyčajne do týždňa, viacstránkovú firemnú stránku za dva až tri týždne. E-shop závisí od počtu produktov a napojení. Konkrétny termín dohodneme spolu s cenou. Projekty sa najčastejšie predlžujú kvôli čakaniu na texty a fotky — ak ich máte pripravené, ide to podľa plánu.",
      followUps: ["start", "included", "pricing"],
      offerContact: true,
    },

    included: {
      id: "included",
      label: "Čo je v cene?",
      keywords: [
        "zahŕňa", "zahrna", "obsahuje", "v cene", "dostanem", "súčasť", "sucast",
        "zahrnuté", "zahrnute", "patrí", "patri", "rozsah",
      ],
      answer:
        "V každom projekte je responzívny dizajn pre mobil aj desktop, základná optimalizácia pre vyhľadávače, kontaktné odkazy, nasadenie na hosting a prepojenie domény. Na záver vás zaškolím, aby ste si vedeli meniť texty a obrázky sami. Doména, hosting aj kód ostávajú vaše. Čo všetko sa dá doplniť, nájdete v sekcii Čo web môže vedieť.",
      followUps: ["pricing", "contact", "start"],
      offerContact: true,
    },

    start: {
      id: "start",
      label: "Ako začneme?",
      keywords: [
        "začať", "zacat", "začiatok", "zaciatok", "objednať", "objednat", "postup",
        "prvý krok", "prvy krok", "ako to prebieha", "spolupráca", "spolupraca",
      ],
      answer:
        "Napíšete mi e-mail alebo správu cez WhatsApp — stačí pár viet o svojej firme a o tom, čo od webu čakáte. Ozvem sa do 24 hodín a doladíme, čo presne web potrebuje. Potom pošlem cenovú ponuku s pevnou cenou a termínom.",
      followUps: ["contact", "delivery", "pricing"],
      offerContact: true,
    },

    redesign: {
      id: "redesign",
      label: "Robíte redizajn starého webu?",
      keywords: [
        "redizajn", "redesign", "prerobiť", "prerobit", "starý web", "stary web",
        "obnoviť", "obnovit", "zmodernizovať", "zmodernizovat", "vylepšiť", "vylepsit",
      ],
      answer:
        "Áno. Prejdem existujúci web, zachovám obsah aj pozície vo vyhľadávaní, nastavím presmerovania a dám stránke nový vizuál. Cena závisí od toho, koľko obsahu web má a čo z neho treba prepísať — poviem ju po tom, ako sa na web pozriem. Pošlite mi odkaz e-mailom a napíšem, čo by som menil.",
      followUps: ["pricing", "delivery", "contact"],
      offerContact: true,
    },

    contact: {
      id: "contact",
      label: "Ako ťa kontaktujem?",
      keywords: [
        "kontakt", "e-mail", "email", "mail", "whatsapp", "napísať", "napisat",
        "ozvať", "ozvat", "telefón", "telefon", "číslo", "cislo", "formulár", "formular",
      ],
      answer:
        "Dvoma spôsobmi: e-mailom na weboraeurope@gmail.com alebo cez WhatsApp na +421 944 352 238. Formulár na webe zámerne nemám — obe cesty idú priamo mne a odpoviem rýchlejšie. Stačí pár viet o tom, čo vaša firma robí a akú stránku potrebujete.",
      followUps: ["start", "pricing", "delivery"],
      offerContact: true,
    },

    ownership: {
      id: "ownership",
      label: "Komu bude web patriť?",
      keywords: [
        "patriť", "patrit", "vlastní", "vlastni", "vlastníctvo", "vlastnictvo",
        "prístupy", "pristupy", "zdrojový kód", "zdrojovy kod", "viazanosť", "viazanost",
      ],
      answer:
        "Vám. Doména, hosting aj zdrojový kód sú vaše a kedykoľvek si ich môžete zobrať so sebou. Nepoužívam uzavreté systémy a neúčtujem poplatok za vydanie prístupov. Priebežnú správu webu neponúkam práve preto, aby ste na mne neviseli.",
      followUps: ["included", "contact"],
      offerContact: false,
    },
  },
};
