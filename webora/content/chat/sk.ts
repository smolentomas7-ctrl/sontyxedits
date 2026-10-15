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
  initialSuggestions: ["pricing", "delivery", "included", "start"],

  fallback: {
    id: "fallback",
    answer:
      "Na toto neviem odpovedať — mám pripravené odpovede len na bežné otázky. Napíšte mi cez kontaktný formulár a ozvem sa vám, zvyčajne do 24 hodín.",
    followUps: ["pricing", "delivery", "included"],
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
        "Pevný cenník nemám. Každý web má iný rozsah, iné funkcie a iné podklady, takže cenu počítam individuálne podľa toho, čo konkrétne potrebujete. Po krátkej konzultácii dostanete ponuku s pevnou cenou a termínom — aby ste vedeli, na čom ste, ešte pred začiatkom prác. Od čoho sa cena odvíja, som rozpísal v sekcii Cena na domovskej stránke.",
      followUps: ["included", "delivery", "eshop"],
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
        "V každom projekte je responzívny dizajn pre mobil aj desktop, základná optimalizácia pre vyhľadávače, kontaktný formulár, nasadenie na hosting a prepojenie domény. Na záver vás zaškolím, aby ste si vedeli meniť texty a obrázky sami. Doména, hosting aj kód ostávajú vaše. Čo všetko sa dá doplniť, nájdete v sekcii Čo web môže vedieť.",
      followUps: ["pricing", "care", "start"],
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
        "Napíšete mi cez formulár pár viet o svojej firme. Ozvem sa do 24 hodín a dohodneme krátky hovor, kde si prejdeme, čo potrebujete. Potom pošlem cenovú ponuku s pevnou cenou a termínom. Konzultácia aj ponuka sú zadarmo a nezáväzné.",
      followUps: ["delivery", "pricing"],
      offerContact: true,
    },

    eshop: {
      id: "eshop",
      label: "Robíte e-shopy?",
      keywords: [
        "eshop", "e-shop", "obchod", "predaj", "produkty", "košík", "kosik",
        "platobná", "platobna", "brána", "brana", "objednávky", "objednavky",
      ],
      answer:
        "Áno. Staviam e-shopy s katalógom produktov, variantmi, košíkom, dopravou a platobnou bránou, vrátane administrácie na správu objednávok. Cenu určujem podľa rozsahu — napíšte mi, koľko produktov plánujete predávať a či potrebujete napojenie na sklad alebo účtovníctvo. Funkčnú ukážku si môžete prejsť v portfóliu, demo Nordik.",
      followUps: ["pricing", "delivery", "start"],
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
        "Áno. Prejdem existujúci web, zachovám obsah aj pozície vo vyhľadávaní, nastavím presmerovania a dám stránke nový vizuál. Cena závisí od toho, koľko obsahu web má a čo z neho treba prepísať — poviem ju po tom, ako sa na web pozriem. Pošlite mi odkaz a napíšem, čo by som menil.",
      followUps: ["pricing", "delivery", "start"],
      offerContact: true,
    },

    care: {
      id: "care",
      label: "Čo po spustení?",
      keywords: [
        "údržba", "udrzba", "správa", "sprava", "po spustení", "po spusteni",
        "podpora", "zálohy", "zalohy", "aktualizácie", "aktualizacie", "mesačne", "mesacne",
      ],
      answer:
        "Prvý mesiac po spustení opravím zadarmo čokoľvek, čo nefunguje tak, ako sme sa dohodli. Potom si môžete objednať mesačnú správu — zálohy, aktualizácie, drobné zmeny textov a dohľad nad dostupnosťou. Cenu dohodneme podľa toho, čo má správa pokrývať, a povinná nie je.",
      followUps: ["included", "start"],
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
        "Vám. Doména, hosting aj zdrojový kód sú vaše a kedykoľvek si ich môžete zobrať so sebou. Nepoužívam uzavreté systémy a neúčtujem poplatok za vydanie prístupov.",
      followUps: ["care", "included"],
      offerContact: false,
    },
  },
};
