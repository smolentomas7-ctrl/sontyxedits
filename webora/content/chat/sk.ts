import type { ChatScript } from "./types";

export const chatSk: ChatScript = {
  /** Chips shown under the greeting. */
  initialSuggestions: ["pricing", "delivery", "included", "start"],

  fallback: {
    id: "fallback",
    answer:
      "Na toto neviem odpovedať — mám pripravené odpovede len na bežné otázky. Napíšte nám cez kontaktný formulár a ozve sa vám človek, zvyčajne do 24 hodín.",
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
        "Jednostránkový web začína na 490 €, firemná stránka s viacerými podstránkami a blogom na 990 €. E-shop robíme na mieru, takže cenu dávame až po konzultácii. V cenníku máme aj kalkulačku, kde si rozsah naklikáte a hneď uvidíte orientačnú sumu.",
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
        "Jednostránkový web zvládneme za 7 dní, firemnú stránku za 2 až 3 týždne. E-shop závisí od počtu produktov. Projekty sa najčastejšie predlžujú kvôli čakaniu na texty a fotky — ak ich máte pripravené, ide to podľa plánu.",
      followUps: ["start", "included", "pricing"],
      offerContact: true,
    },

    included: {
      id: "included",
      label: "Čo je v cene?",
      keywords: [
        "zahŕňa", "zahrna", "obsahuje", "v cene", "dostanem", "súčasť", "sucast",
        "balík", "balik", "zahrnuté", "zahrnute", "patrí", "patri",
      ],
      answer:
        "V každom projekte je responzívny dizajn pre mobil aj desktop, základná optimalizácia pre vyhľadávače, kontaktný formulár, nasadenie na hosting a prepojenie domény. Na záver vás zaškolíme, aby ste si vedeli meniť texty a obrázky sami. Doména, hosting aj kód ostávajú vaše.",
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
        "Napíšete nám cez formulár pár viet o svojej firme. Ozveme sa do 24 hodín a dohodneme krátky hovor, kde si prejdeme, čo potrebujete. Potom pošleme cenovú ponuku s pevnou cenou a termínom. Konzultácia aj ponuka sú zadarmo a nezáväzné.",
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
        "Áno. Staviame e-shopy s katalógom produktov, variantmi, košíkom, dopravou a platobnou bránou, vrátane administrácie na správu objednávok. Cenu určujeme podľa rozsahu — napíšte nám, koľko produktov plánujete predávať. Funkčný e-shop si môžete vyskúšať v našom portfóliu, ukážka Nordik.",
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
        "Áno, redizajn robíme od 690 €. Prejdeme existujúci web, zachováme obsah a pozície vo vyhľadávaní, nastavíme presmerovania a dáme stránke nový vizuál. Na konci vám ukážeme porovnanie rýchlosti pred a po.",
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
        "Prvý mesiac po spustení opravíme zadarmo čokoľvek, čo nefunguje tak, ako sme sa dohodli. Potom si môžete objednať mesačnú správu za 39 € — zálohy, aktualizácie, drobné zmeny textov a dohľad nad dostupnosťou. Nie je to povinné.",
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
        "Vám. Doména, hosting aj zdrojový kód sú vaše a kedykoľvek si ich môžete zobrať so sebou. Nepoužívame uzavreté systémy a neúčtujeme poplatok za vydanie prístupov.",
      followUps: ["care", "included"],
      offerContact: false,
    },
  },
};
