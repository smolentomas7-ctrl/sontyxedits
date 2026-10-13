import type { LocaleContent } from "./types";

export const sk: LocaleContent = {
  locale: "sk",
  htmlLang: "sk",

  common: {
    skipToContent: "Preskočiť na obsah",
    callCta: "Zavolať do servisu",
    callAria: "Zavolať do servisu na číslo +421 918 918 109",
    servicesCta: "Naše služby",
    contactCta: "Napísať nám",
    navigateCta: "Navigovať k nám",
    readMore: "Viac o službe",
    backToServices: "Späť na služby",
    home: "Domov",
    openNow: "Teraz otvorené — zatvárame o {time}",
    closedNow: "Teraz zatvorené — otvárame {day} o {time}",
    breakNow: "Obedňajšia prestávka — otvárame o {time}",
    breakLabel: "Obedňajšia prestávka",
    closedToday: "Dnes zatvorené",
    today: "dnes",
    hoursHeading: "Otváracie hodiny",
    addressHeading: "Adresa",
    phoneHeading: "Telefón",
    days: {
      mon: "Pondelok",
      tue: "Utorok",
      wed: "Streda",
      thu: "Štvrtok",
      fri: "Piatok",
      sat: "Sobota",
      sun: "Nedeľa",
    },
    closedLabel: "Zatvorené",
    menu: "Menu",
    closeMenu: "Zavrieť menu",
    languageLabel: "Jazyk",
    switchTo: "English",
    copyAddress: "Skopírovať adresu",
    addressCopied: "Adresa skopírovaná",
    relatedServices: "Súvisiace služby",
  },

  nav: {
    services: "Služby",
    about: "O servise",
    contact: "Kontakt",
    privacy: "Ochrana osobných údajov",
  },

  home: {
    meta: {
      title: "Autoservis Ružomberok | M.I.Auto s.r.o.",
      description:
        "Autoservis v Ružomberku. Diagnostika, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia, rozvody a klimatizácia. Zavolajte na +421 918 918 109.",
    },
    heroTitle: "Autoservis v Ružomberku",
    heroTitleSecond: "Diagnostika, elektronika, rozvody.",
    heroLead:
      "Riešime poruchy od kontrolky po opravu. Diagnostika, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia vozidiel koncernu Volkswagen, výmena rozvodov a servis klimatizácie.",
    heroImageAlt:
      "Dielňa M.I.Auto v Ružomberku, dve vozidlá s otvorenou kapotou počas servisu",
    servicesHeading: "Čo robíme",
    servicesLead:
      "Sedem služieb. Pri väčšine porúch sa začína diagnostikou — preto má svoje miesto na začiatku.",
    signatureHeading: "Od kontrolky k oprave",
    signatureLead:
      "Medzi rozsvietenou kontrolkou a opraveným autom je päť krokov. Potiahnite posuvník a pozrite si, čo sa v ktorom deje a prečo sa žiadny z nich nedá preskočiť.",
    whyHeading: "Prečo k nám",
    why: [
      {
        title: "Sedem služieb na jednom mieste",
        body:
          "Diagnostika, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia vozidiel koncernu Volkswagen, výmena rozvodov a servis klimatizácie.",
      },
      {
        title: "Najprv príčina, potom oprava",
        body:
          "Chybový kód je vodidlo, nie diagnóza. Poruchu zužujeme meraním, aby sa nemenili diely, ktoré sú v poriadku.",
      },
      {
        title: "Elektrika vozidiel koncernu Volkswagen",
        body:
          "Elektrické a elektronické poruchy na vozidlách koncernu Volkswagen hľadáme postupným vylučovaním podľa schémy.",
      },
      {
        title: "Rozvody na 2.0 TDI a 3.0 TDI",
        body:
          "Výmenu rozvodov robíme na motoroch 2.0 TDI a 3.0 TDI. Je to práca, kde sa neoplatí čakať na poruchu.",
      },
    ],
    mapHeading: "Kde nás nájdete",
    mapLead:
      "Sme na Sládkovičovej v Ružomberku. Zavolajte pred príchodom — budeme vedieť, že prídete.",
    mapLoadButton: "Zobraziť mapu",
    mapLoadNote:
      "Mapa sa načíta zo serverov Google až po kliknutí. Dovtedy táto stránka na Google nič neposiela.",
    finalHeading: "Zavolajte a povedzte, čo vozidlo robí",
    finalLead:
      "Najrýchlejšia cesta k odpovedi je telefón. Ak voláte mimo otváracích hodín, napíšte nám cez formulár.",
    finalFormCta: "Radšej napíšem",
  },

  servicesPage: {
    meta: {
      title: "Služby autoservisu Ružomberok | M.I.Auto s.r.o.",
      description:
        "Diagnostika, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia, rozvody a klimatizácia v Ružomberku. Zavolajte na +421 918 918 109.",
    },
    h1: "Služby",
    lead:
      "Sedem oblastí, ktorým sa venujeme. Pri každej nájdete, kedy ju riešiť, ako postupujeme a čo si na nej viete sami vyskúšať.",
    faqHeading: "Časté otázky",
    ctaHeading: "Neviete, do ktorej služby vaša porucha patrí?",
    ctaLead:
      "To je bežné — väčšina porúch sa prejaví inde, než vzniká. Zavolajte a popíšte, čo vozidlo robí.",
  },

  services: {
    "diagnostika-vozidiel": {
      slug: "diagnostika-vozidiel",
      name: "Diagnostika vozidiel",
      h1: "Diagnostika vozidiel — Ružomberok",
      icon: "scan-line",
      cardDescription:
        "Načítame chybové kódy a hľadáme príčinu, ktorá kontrolku rozsvietila. Nie len vymazanie hlásenia.",
      lead:
        "Kontrolka na prístrojovke hovorí, že riadiaca jednotka zaznamenala chybu. Nehovorí, čo ju spôsobilo. Diagnostika je krok, ktorým sa z hlásenia dostaneme k príčine — načítame uložené chybové kódy, pozrieme sa na živé údaje zo snímačov a porovnáme ich s tým, ako sa vozidlo správa v skutočnosti.",
      overview:
        "Chybový kód povie, ktorý okruh hlási problém, nie ktorý diel je pokazený. Diagnostika je práca medzi tými dvoma vetami.",
      covers: [
        "Načítanie uložených a aktuálnych chybových kódov",
        "Kontrola živých údajov zo snímačov",
        "Zúženie poruchy na konkrétny okruh alebo komponent",
      ],
      when: [
        "Na prístrojovke svieti kontrolka motora, ABS, airbagu alebo iná výstraha.",
        "Vozidlo stráca výkon, trhá, nerovnomerne beží na voľnobehu alebo ťažšie štartuje.",
        "Spotreba stúpla bez zjavnej príčiny.",
        "Niektorá funkcia prestala fungovať — klimatizácia, svetlá, elektrické okná.",
        "Po predchádzajúcej oprave sa kontrolka rozsvietila znova.",
      ],
      what: [
        "Pripojíme diagnostiku do OBD konektora a načítame uložené aj aktuálne chybové kódy.",
        "Kód overíme meraním a živými údajmi zo snímačov, aby sa nemenil diel, ktorý je v poriadku.",
        "Poruchu zúžime na konkrétny okruh alebo komponent.",
        "Povieme, čo sme našli, a dohodneme ďalší postup.",
      ],
      related: ["cipovanie-ecu", "elektroinstalacia-vw"],
      meta: {
        title: "Diagnostika vozidiel Ružomberok | M.I.Auto s.r.o.",
        description:
          "Svieti vám kontrolka? V Ružomberku načítame chybové kódy a hľadáme príčinu, nie len symptóm. Zavolajte na +421 918 918 109 a popíšte, čo vozidlo robí.",
      },
    },

    "cipovanie-ecu": {
      slug: "cipovanie-ecu",
      name: "Čipovanie ECU",
      h1: "Čipovanie ECU — Ružomberok",
      icon: "cpu",
      cardDescription:
        "Úprava softvéru riadiacej jednotky motora. Čo je možné, závisí od konkrétneho vozidla.",
      lead:
        "Čipovanie znamená zmenu softvéru v riadiacej jednotke motora. Nie je to univerzálny zákrok — čo sa dá a čo nie, závisí od konkrétneho motora, od jeho stavu a od toho, čo od vozidla očakávate. Preto to neriešime cez cenník ani cez formulár, ale telefonicky nad konkrétnym vozidlom.",
      overview:
        "Softvérová úprava riadiacej jednotky motora. Odpoveď na otázku „čo sa dá s mojím autom“ existuje len pri konkrétnom vozidle.",
      covers: [
        "Úprava softvéru riadiacej jednotky motora",
        "Posúdenie možností pri konkrétnom vozidle",
        "Konzultácia telefonicky, nad vaším motorom",
      ],
      when: [
        "Zvažujete úpravu softvéru motora a chcete vedieť, čo je pri vašom vozidle vôbec možné.",
        "Po predchádzajúcom zásahu do softvéru sa vozidlo správa inak, než očakávate.",
        "Chcete sa poradiť skôr, než sa pre niečo rozhodnete.",
      ],
      what: [
        "Povieme si, o aké vozidlo a motor ide a čo od úpravy očakávate.",
        "Prejdeme, čo je pri tomto konkrétnom vozidle možné a čo nie.",
        "Rozsah a postup dohodneme telefonicky nad vaším vozidlom.",
      ],
      note:
        "Pred rozhodnutím zvážte okolnosti svojho vozidla a to, ako ho používate. Konkrétne otázky preberieme telefonicky.",
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "Čipovanie ECU Ružomberok | M.I.Auto s.r.o.",
        description:
          "Úprava softvéru riadiacej jednotky motora v Ružomberku. Čo je možné pri vašom konkrétnom motore, preberieme telefonicky na +421 918 918 109.",
      },
    },

    "geometria-kolies": {
      slug: "geometria-kolies",
      name: "Geometria kolies",
      h1: "Geometria kolies — Ružomberok",
      icon: "crosshair",
      cardDescription:
        "Meranie a nastavenie geometrie náprav. Rieši ťahanie do strany aj nerovnomerné zjazdenie pneumatík.",
      lead:
        "Geometria určuje, ako kolesá stoja voči vozovke a voči sebe. Keď sa nastavenie posunie — po obrubníku, po výmene dielu podvozku alebo postupne opotrebením — vozidlo ťahá do strany, volant nestojí rovno a pneumatiky sa zjazdia nerovnomerne. Meraním zistíme skutočné hodnoty a nastavíme ich.",
      overview:
        "Keď vozidlo ťahá do strany alebo sa pneumatiky zjazdávajú po jednej hrane, príčina býva v geometrii. Meraním sa to dá zistiť presne.",
      covers: [
        "Meranie skutočných hodnôt geometrie",
        "Nastavenie na hodnoty predpísané pre dané vozidlo",
        "Kontrola vôle na podvozku pred meraním",
      ],
      when: [
        "Vozidlo ťahá do strany, hoci vozovka je rovná.",
        "Volant pri priamej jazde nestojí na stred.",
        "Pneumatiky sú zjazdené viac na vnútornej alebo vonkajšej hrane.",
        "Po výmene dielu podvozku alebo po náraze do obrubníka.",
        "Po prezutí, keď chcete mať istotu, že sa nové pneumatiky nebudú zjazdávať nakrivo.",
      ],
      what: [
        "Vozidlo pripravíme a skontrolujeme, či na podvozku nie je vôľa, ktorá by meranie skreslila.",
        "Zmeriame skutočné hodnoty a porovnáme ich s hodnotami pre dané vozidlo.",
        "Nastavíme to, čo sa na danom vozidle nastaviť dá.",
        "Prejdeme s vami namerané hodnoty pred nastavením a po ňom.",
      ],
      related: ["pneuservis", "diagnostika-vozidiel"],
      meta: {
        title: "Geometria kolies Ružomberok | M.I.Auto s.r.o.",
        description:
          "Ťahá vám auto do strany alebo sa pneumatiky zjazdávajú nerovnomerne? Zmeriame a nastavíme geometriu kolies v Ružomberku. Volajte +421 918 918 109.",
      },
    },

    pneuservis: {
      slug: "pneuservis",
      name: "Pneuservis",
      h1: "Pneuservis — Ružomberok",
      icon: "circle-dot",
      cardDescription:
        "Práca s pneumatikami a diskami. Dezén rozhoduje o brzdnej dráhe viac, než si väčšina vodičov myslí.",
      lead:
        "Pneumatiky sú jediná časť vozidla, ktorá sa dotýka vozovky. Na ich stave závisí brzdná dráha aj správanie v zákrute, a rozdiel medzi takmer novým a zjazdeným dezénom je na mokrom väčší, než sa čaká. Pozrieme sa na stav pneumatík aj diskov a povieme, čo s nimi.",
      overview:
        "Pneumatiky sú jediný kontakt vozidla s vozovkou. Pri hĺbke dezénu blízko zákonného minima rastie brzdná dráha na mokrom výrazne.",
      covers: [
        "Práca s pneumatikami a diskami",
        "Posúdenie stavu a hĺbky dezénu",
        "Sezónna výmena podľa dohody",
      ],
      when: [
        "Blíži sa sezóna a potrebujete prejsť na zimné alebo letné pneumatiky.",
        "Pneumatika stráca tlak alebo ste prešli cez niečo ostré.",
        "Pri vyšších rýchlostiach cítite vo volante alebo v sedadle vibrácie.",
        "Dezén je blízko zákonného minima alebo je zjazdený nerovnomerne.",
      ],
      what: [
        "Pozrieme sa na stav pneumatík a diskov a odmeriame hĺbku dezénu.",
        "Povieme, čo vidíme, a čo z toho je naozaj potrebné riešiť.",
        "Dohodneme rozsah prác a termín — zavolajte a povedzte, o aké vozidlo ide.",
      ],
      related: ["geometria-kolies", "diagnostika-vozidiel"],
      meta: {
        title: "Pneuservis Ružomberok | M.I.Auto s.r.o.",
        description:
          "Pneuservis v Ružomberku — práca s pneumatikami a diskami. Zavolajte na +421 918 918 109 a overte si, čo presne pre vaše vozidlo vieme urobiť.",
      },
    },

    "elektroinstalacia-vw": {
      slug: "elektroinstalacia-vw",
      name: "Elektroinštalácia vozidiel koncernu Volkswagen",
      h1: "Elektroinštalácia vozidiel koncernu Volkswagen — Ružomberok",
      icon: "cable",
      cardDescription:
        "Hľadanie a oprava elektrických a elektronických porúch na vozidlách koncernu Volkswagen.",
      lead:
        "Elektrická porucha sa málokedy prejaví tam, kde vzniká. Prerušený vodič, skorodovaný kontakt alebo chyba v komunikácii medzi jednotkami sa navonok ukáže ako nefunkčná výbava alebo kontrolka. Príčinu hľadáme meraním a postupným vylučovaním, nie výmenou dielov naslepo.",
      overview:
        "Elektrická porucha sa prejaví inde, než vzniká. Hľadá sa meraním a vylučovaním, podľa schémy daného vozidla.",
      covers: [
        "Hľadanie elektrických a elektronických porúch",
        "Meranie v dotknutom okruhu a porovnanie so schémou",
        "Opravy kabeláže a kontaktov",
      ],
      when: [
        "Nefunguje elektrická výbava — okná, zrkadlá, svetlá, centrálne zamykanie.",
        "Porucha sa objavuje a mizne, často po daždi alebo pri otrasoch.",
        "Batéria sa vybíja, aj keď vozidlo stojí.",
        "Po montáži príslušenstva alebo po zásahu do kabeláže niečo prestalo fungovať.",
      ],
      what: [
        "Poruchu si necháme popísať — kedy sa objavuje a za akých okolností.",
        "Zmeriame napätie a odpor v dotknutom okruhu a porovnáme so schémou.",
        "Chybu zúžime na konkrétny vodič, kontakt alebo jednotku.",
        "Opravíme to, čo sa opraviť dá, a povieme, čo je potrebné vymeniť.",
      ],
      note:
        "M.I.Auto s.r.o. je nezávislý autoservis. Nie sme autorizovaný servis Volkswagen. „Vozidlá koncernu Volkswagen“ je len popis toho, na čom pracujeme.",
      related: ["diagnostika-vozidiel", "cipovanie-ecu"],
      meta: {
        title: "Elektroinštalácia vozidiel Volkswagen Ružomberok | M.I.Auto s.r.o.",
        description:
          "Elektrické a elektronické poruchy na vozidlách koncernu Volkswagen hľadáme v Ružomberku meraním, nie výmenou dielov naslepo. Volajte +421 918 918 109.",
      },
    },

    "vymena-rozvodov": {
      slug: "vymena-rozvodov",
      name: "Výmena rozvodov",
      h1: "Výmena rozvodov — Ružomberok",
      icon: "cog",
      cardDescription:
        "Výmena rozvodov na motoroch 2.0 TDI a 3.0 TDI. Zanedbaný rozvod poškodí motor.",
      lead:
        "Rozvodový mechanizmus drží v súlade pohyb kľukového a vačkového hriadeľa. Keď remeň alebo reťaz zlyhá, piesty a ventily sa stretnú a škoda býva rozsiahla. Preto sa rozvody menia preventívne, podľa intervalu výrobcu. Výmenu robíme na motoroch 2.0 TDI a 3.0 TDI.",
      overview:
        "Rozvody sa menia preventívne, podľa intervalu výrobcu. Výmenu robíme na motoroch 2.0 TDI a 3.0 TDI.",
      covers: [
        "Výmena rozvodov na motoroch 2.0 TDI",
        "Výmena rozvodov na motoroch 3.0 TDI",
        "Kontrola stavu kladiek a napínača",
      ],
      when: [
        "Vozidlo sa blíži k intervalu výmeny predpísanému výrobcom.",
        "Neviete, či bol rozvod pri predchádzajúcom majiteľovi menený.",
        "Od rozvodov počuť pískanie, hvizd alebo hrkot.",
        "Motor štartuje ťažšie alebo beží nepokojne a je podozrenie na posunutý rozvod.",
      ],
      what: [
        "Overíme, o aký motor ide a čo je preň predpísané.",
        "Sprístupníme rozvodovú oblasť a skontrolujeme stav remeňa, kladiek a napínača.",
        "Vymeníme diely a nastavíme rozvod podľa hodnôt výrobcu.",
        "Po zložení motor skontrolujeme za chodu.",
      ],
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "Výmena rozvodov 2.0 TDI a 3.0 TDI Ružomberok | M.I.Auto s.r.o.",
        description:
          "Výmena rozvodov na motoroch 2.0 TDI a 3.0 TDI v Ružomberku. Neodkladajte to — zavolajte na +421 918 918 109 a overte si interval pre svoj motor.",
      },
    },

    "servis-klimatizacie": {
      slug: "servis-klimatizacie",
      name: "Servis klimatizácie",
      h1: "Servis klimatizácie — Ružomberok",
      icon: "snowflake",
      cardDescription:
        "Klimatizácia, ktorá nechladí, býva o chladive alebo o netesnosti. Chladenie slabne postupne.",
      lead:
        "Klimatizácia stráca chladivo aj bez poruchy — netesnosťami, ktoré sú súčasťou systému. Keď chladenie postupne slabne, dôvodom býva nedostatok chladiva alebo únik. Práve preto si to vodič všimne až v lete, hoci systém strácal výkon celé mesiace.",
      overview:
        "Chladenie slabne postupne, takže si to vodič všimne až v lete. Teplota z výduchu povie o stave náplne viac než pocit.",
      covers: [
        "Posúdenie stavu klimatizácie",
        "Kontrola chladiaceho výkonu",
        "Konzultácia nad konkrétnym vozidlom",
      ],
      when: [
        "Klimatizácia chladí slabšie než predtým alebo nechladí vôbec.",
        "Po zapnutí je z ventilácie cítiť zápach.",
        "Okná sa v zime zahmlievajú dlhšie než zvyčajne.",
        "Systém ste roky neriešili a chcete vedieť, v akom je stave.",
      ],
      what: [
        "Popíšete, ako sa klimatizácia správa a odkedy.",
        "Pozrieme sa na systém a zmeriame, ako chladí.",
        "Povieme, čo sme našli, a dohodneme ďalší postup.",
      ],
      related: ["diagnostika-vozidiel", "elektroinstalacia-vw"],
      meta: {
        title: "Servis klimatizácie Ružomberok | M.I.Auto s.r.o.",
        description:
          "Klimatizácia nechladí ako predtým? Pozrieme sa na ňu v Ružomberku. Zavolajte na +421 918 918 109 a overte si rozsah servisu pre vaše vozidlo.",
      },
    },
  },

  about: {
    meta: {
      title: "O servise | M.I.Auto s.r.o. Ružomberok",
      description:
        "M.I.Auto s.r.o. je nezávislý autoservis v Ružomberku na Sládkovičovej. Diagnostika, elektronika, rozvody, pneuservis a klimatizácia. Volajte +421 918 918 109.",
    },
    h1: "O servise",
    lead:
      "M.I.Auto s.r.o. je nezávislý autoservis v Ružomberku na Sládkovičovej. Venujeme sa diagnostike, elektronike a mechanike vozidiel.",
    whatWeDoHeading: "Čomu sa venujeme",
    quietHeading: "Ako k tomu pristupujeme",
    quietBody: [
      "Väčšina porúch sa prejaví inde, než vzniká. Kontrolka motora nehovorí, ktorý diel je pokazený — hovorí, že niektorá riadiaca jednotka zaznamenala hodnotu mimo očakávania. Medzi tými dvoma vetami je celá práca.",
      "Preto sa chybový kód overuje meraním. Je to pomalšie než vymeniť diel, ktorý kód spomína, ale je to jediný spôsob, ako nevymeniť diel, ktorý bol v poriadku.",
      "To isté platí pre elektriku a pre rozvody. Pri elektrike sa postupuje podľa schémy a vylučovaním. Pri rozvodoch sa nečaká na poruchu, pretože keď rozvod zlyhá, oprava už nie je o rozvode.",
    ],
    ownersHeading: "Majitelia",
    ownerRoles: {
      owner: "Majiteľ servisu",
      coOwner: "Spolumajiteľ servisu",
    },
    experience: {
      heading: "Skúsenosti, odbornosť a poctivá práca",
      lead: "Vaše auto v rukách odborníkov.",
      body:
        "Za našou prácou stoja viac ako 10 rokov skúseností so servisom a údržbou automobilov. Naše odborné základy vychádzajú aj z absolvovaného štúdia na automechanickej škole, kde sme dosahovali výborné študijné výsledky. Získané vedomosti a praktické skúsenosti využívame pri každodennej starostlivosti o vozidlá našich zákazníkov.",
      points: [
        {
          title: "Viac ako 10 rokov skúseností",
          body: "Praktické skúsenosti so servisom a údržbou automobilov.",
        },
        {
          title: "Odborné technické vzdelanie",
          body: "Absolvované štúdium na automechanickej škole.",
        },
        {
          title: "Dôraz na kvalitu",
          body: "Precízny prístup, zodpovedná práca a starostlivosť o každé vozidlo.",
        },
      ],
    },
    factsHeading: "Kde nás nájdete",
    interiorAlt: "Interiér dielne M.I.Auto, vozidlá počas servisu",
    detail01Alt: "Vozidlo zdvihnuté na dvojstĺpovom zdviháku v dielni M.I.Auto",
    detail02Alt: "Terénne vozidlo na zdviháku v dielni M.I.Auto",
  },

  contact: {
    meta: {
      title: "Kontakt | M.I.Auto s.r.o. Ružomberok",
      description:
        "Sládkovičova 2528/108, 034 01 Ružomberok. Otvorené pondelok až piatok 07:00–17:00, prestávka 12:00–13:00. Zavolajte na +421 918 918 109 alebo napíšte cez formulár.",
    },
    h1: "Kontakt",
    lead:
      "Najrýchlejšie sa dohodneme telefonicky. Ak voláte mimo otváracích hodín, napíšte cez formulár nižšie.",
    mapHeading: "Mapa",
    mapTitle: "Mapa s polohou M.I.Auto s.r.o., Sládkovičova 2528/108, Ružomberok",
    mapDisclosure:
      "Mapa je vložená zo služby Google Maps. Jej načítaním sa spojíte so servermi Google.",
    mapDisclosureLink: "Viac v ochrane osobných údajov",
    formHeading: "Napíšte nám",
    formLead:
      "Čím konkrétnejšie popíšete, čo vozidlo robí, tým lepšie sa vieme pripraviť.",
  },

  form: {
    name: "Meno",
    namePlaceholder: "Ján Novák",
    phone: "Telefón",
    phonePlaceholder: "+421 900 000 000",
    email: "E-mail",
    emailOptional: "nepovinné",
    vehicle: "Vozidlo",
    vehiclePlaceholder: "Škoda Octavia 2.0 TDI, 2016",
    vehicleHint: "Značka, model a rok — pomôže nám to pri príprave.",
    service: "Služba",
    serviceOther: "Iné",
    servicePrompt: "Vyberte službu",
    message: "Správa",
    messagePlaceholder:
      "Popíšte, čo vozidlo robí, odkedy a za akých okolností sa to objavuje.",
    consent: "Súhlasím so spracovaním údajov na účel odpovede na túto správu.",
    consentLink: "Ochrana osobných údajov",
    submit: "Odoslať správu",
    submitting: "Odosielam…",
    disabledReason:
      "Odoslanie je zatiaľ neaktívne: vyplňte meno, telefón, správu a potvrďte súhlas.",
    successHeading: "Správa odoslaná",
    successBody:
      "Dostali sme vašu správu a ozveme sa. Ak sa to ponáhľa, zavolajte priamo.",
    errorHeading: "Správu sa nepodarilo odoslať",
    errorBody:
      "Odoslanie zlyhalo a vaša správa sa neodoslala. Skúste to znova, alebo zavolajte priamo — to je aj tak najrýchlejšie.",
    charactersLeft: "Zostáva {n} znakov",
    errors: {
      nameRequired: "Zadajte meno.",
      nameLength: "Meno musí mať 2 až 80 znakov.",
      phoneRequired: "Zadajte telefónne číslo.",
      phoneInvalid: "Toto nevyzerá ako telefónne číslo.",
      emailInvalid: "Skontrolujte tvar e-mailovej adresy.",
      messageRequired: "Napíšte, s čím vám môžeme pomôcť.",
      messageLength: "Správa musí mať 10 až 1500 znakov.",
      consentRequired: "Bez súhlasu správu nevieme spracovať.",
      tooFast: "Formulár bol odoslaný príliš rýchlo. Skúste to prosím znova.",
    },
  },

  faq: [
    {
      id: "sluzby",
      q: "Aké služby ponúkate?",
      a: "Diagnostiku vozidiel, čipovanie ECU, geometriu kolies, pneuservis, elektroinštaláciu vozidiel koncernu Volkswagen, výmenu rozvodov a servis klimatizácie.",
    },
    {
      id: "kde",
      q: "Kde vás nájdem?",
      a: "Sládkovičova 2528/108, 034 01 Ružomberok. Na stránke Kontakt je mapa aj odkaz na navigáciu.",
    },
    {
      id: "hodiny",
      q: "Aké máte otváracie hodiny?",
      a: "Pondelok až piatok od 07:00 do 17:00, s obedňajšou prestávkou od 12:00 do 13:00. V sobotu a v nedeľu je zatvorené.",
    },
    {
      id: "termin",
      q: "Ako si dohodnem termín?",
      a: "Zavolajte na +421 918 918 109. Mimo otváracích hodín použite formulár na stránke Kontakt.",
    },
    {
      id: "priprava",
      q: "Čo si mám pripraviť, keď volám?",
      a: "Značku, model a rok vozidla, motorizáciu ak ju viete, popis toho, čo vozidlo robí, odkedy sa to deje a ktoré kontrolky svietia.",
    },
    {
      id: "vw",
      q: "Robíte na vozidlách koncernu Volkswagen?",
      a: "Áno, elektroinštalácii vozidiel koncernu Volkswagen sa venujeme. M.I.Auto s.r.o. je pritom nezávislý autoservis, nie autorizovaný servis Volkswagen.",
    },
    {
      id: "ecu",
      q: "Robíte čipovanie ECU?",
      a: "Áno. Čo je pri konkrétnom motore možné, závisí od vozidla, preto to preberáme telefonicky.",
    },
  ],

  privacy: {
    meta: {
      title: "Ochrana osobných údajov | M.I.Auto s.r.o.",
      description:
        "Aké údaje zbiera kontaktný formulár, ako dlho ich uchovávame, ako funguje vložená mapa a automatický asistent, a aké máte práva.",
    },
    h1: "Ochrana osobných údajov",
    reviewNotice:
      "Tento dokument nie je právne posúdený. Pred spustením stránky ho má skontrolovať a doplniť osoba s právnou kvalifikáciou. Netvrdíme, že je v súlade s GDPR ani s iným predpisom.",
    updated: "Posledná úprava: pri nasadení stránky",
    controller: {
      heading: "Kto spracúva údaje",
      intro:
        "Prevádzkovateľom, ktorý rozhoduje o spracúvaní osobných údajov z tejto stránky, je:",
    },
    sections: [
      {
        heading: "Kontaktný formulár",
        body: [
          "Formulár na stránke Kontakt zbiera meno, telefónne číslo, nepovinne e-mail, nepovinne údaj o vozidle, vybranú službu a text správy.",
          "Tieto údaje spracúvame výlučne preto, aby sme vám na správu odpovedali a dohodli prípadný termín. Nepoužívame ich na marketing a neposkytujeme ich tretím stranám na ich vlastné účely.",
          "Právnym základom je náš oprávnený záujem odpovedať na dopyt, ktorý ste nám sami poslali, prípadne kroky pred uzavretím zmluvy, ak sa dohodneme na oprave.",
          "Odoslaný formulár spracúva služba Netlify Forms spoločnosti Netlify, ktorá správu uloží a sprístupní nám; dáta sú uložené na jej infraštruktúre. Netlify v tomto vystupuje ako sprostredkovateľ.",
          "Odoslané správy uchovávame 12 mesiacov od vybavenia dopytu a potom ich mažeme. Ak z dopytu vznikne zákazka, údaje k nej sa riadia lehotami pre účtovné a daňové doklady. Prístup k správam majú len majitelia servisu.",
        ],
      },
      {
        heading: "Fotografie majiteľov",
        body: [
          "Na stránke O servise sú zverejnené fotografie majiteľov servisu spolu s ich menami. Fotografia identifikovateľnej osoby je osobný údaj a zverejňujeme ju so súhlasom dotknutých osôb.",
          "Súhlas so zverejnením je možné kedykoľvek odvolať na kontaktoch uvedených vyššie; po odvolaní fotografiu zo stránky odstránime.",
        ],
      },
      {
        heading: "Vložená mapa Google",
        body: [
          "Na stránke Kontakt je vložená mapa zo služby Google Maps. Keď sa mapa načíta, prehliadač sa spojí so servermi spoločnosti Google a tá môže spracovať vašu IP adresu a ďalšie technické údaje podľa svojich vlastných podmienok.",
          "Na úvodnej stránke sa mapa nenačíta sama. Zobrazí sa až po kliknutí na tlačidlo, takže kým naň nekliknete, úvodná stránka na Google nič neposiela.",
        ],
      },
      {
        heading: "Automatický asistent",
        body: [
          "V pravom dolnom rohu je automatický asistent. Nie je to človek a v hlavičke panela je to aj uvedené.",
          "Prepis rozhovoru sa ukladá len vo vašom prehliadači (sessionStorage) a po zatvorení karty zaniká. Na našej strane prepisy neuchovávame.",
          "Keď je asistent napojený na jazykový model, text vašej otázky sa odošle poskytovateľovi modelu — spoločnosti Anthropic — aby vedel odpovedať. Neposielame k nemu vaše meno, telefón ani e-mail; asistent o ne nežiada a nemá na ne prístup. Asistent je zároveň inštruovaný, aby osobné údaje nezbieral.",
          "O prevádzke zaznamenávame len technické údaje: čas požiadavky, jazyk stránky, trvanie odpovede, počet spracovaných tokenov, to, či sa použila záložná odpoveď, a označenie sekcie webu, z ktorej odpoveď vychádzala. Text správ nezaznamenávame a tieto záznamy nespájame s vašou totožnosťou.",
          "Ak pod odpoveďou kliknete na palec hore alebo dole, zaznamená sa len tento signál a poradové číslo odpovede v rozhovore — nie jej text ani text vašej otázky.",
        ],
      },
      {
        heading: "Súbory cookie a meranie návštevnosti",
        body: [
          "Táto stránka nenastavuje sledovacie cookie a nemá nasadené analytické nástroje. Preto na nej nie je ani lišta so súhlasom — nebolo by na čo dávať súhlas.",
          "Prehliadač si lokálne pamätá len zvolený jazyk a prebiehajúci rozhovor s asistentom. Tieto údaje neopúšťajú vaše zariadenie.",
        ],
      },
      {
        heading: "Písma a externý obsah",
        body: [
          "Písma sú súčasťou stránky a načítavajú sa z nej. Stránka si ich nesťahuje zo žiadnej externej služby.",
          "Externý obsah tvorí mapa Google opísaná vyššie a, ak je asistent zapnutý, jeho požiadavky na poskytovateľa modelu.",
        ],
      },
      {
        heading: "Vaše práva",
        body: [
          "Ako dotknutá osoba máte vo vzťahu k svojim osobným údajom tieto práva:",
          "Právo na prístup — môžete žiadať potvrdenie, či o vás spracúvame údaje, a ich kópiu.",
          "Právo na opravu — ak sú údaje nesprávne alebo neúplné, môžete žiadať ich opravu alebo doplnenie.",
          "Právo na výmaz — môžete žiadať vymazanie údajov, najmä ak už nie sú potrebné na účel, na ktorý sme ich získali.",
          "Právo na obmedzenie spracúvania — môžete žiadať, aby sme údaje dočasne iba uchovávali, napríklad kým sa overí ich správnosť.",
          "Právo na prenosnosť — údaje, ktoré ste nám poskytli, vám vieme vydať v bežne používanom strojovo čitateľnom formáte.",
          "Právo namietať — proti spracúvaniu založenému na oprávnenom záujme môžete kedykoľvek podať námietku.",
          "Právo odvolať súhlas — ak je spracúvanie založené na súhlase, môžete ho kedykoľvek odvolať; odvolanie nemá vplyv na zákonnosť spracúvania pred odvolaním.",
          "Právo podať sťažnosť — môžete sa obrátiť na Úrad na ochranu osobných údajov Slovenskej republiky, Hraničná 12, 820 07 Bratislava.",
          "Svoje práva uplatníte na kontaktoch uvedených v úvode tohto dokumentu. Odpovieme bez zbytočného odkladu.",
        ],
      },
    ],
  },

  castrol: {
    eyebrow: "Spolupráca",
    heading: "Partner Castrol Service",
    lead: "Kvalita, na ktorú sa môžete spoľahnúť.",
    body:
      "Spolupracujeme so značkou Castrol Service a pri výmene motorového oleja používame oleje Castrol. Pri každom vozidle vyberáme olej podľa požiadaviek výrobcu, potrebných špecifikácií a odporúčaní pre konkrétny motor.",
    points: [
      "Zmluvná spolupráca s Castrol Service",
      "Motorové oleje Castrol",
      "Výber oleja podľa špecifikácií výrobcu vozidla",
      "Dôraz na kvalitu a správny servisný postup",
    ],
  },

  signature: {
    title: "Od kontrolky k oprave",
    hint: "Potiahnite posuvník a prejdite si päť fáz.",
    keyboardHint:
      "Šípky posúvajú po malých krokoch, Page Up a Page Down po fázach, Home a End na začiatok a koniec.",
    svgTitle:
      "Prístrojová doska s diagnostickým prístrojom. V poslednej fáze je prístrojovka bez svietiacich výstražných kontroliek.",
    stageLabel: "Fáza",
    stages: [
      {
        name: "Kontrolka svieti",
        body: "Riadiaca jednotka zaznamenala hodnotu mimo očakávania a rozsvietila kontrolku. Čo ju spôsobilo, sa z nej prečítať nedá.",
      },
      {
        name: "Pripojenie diagnostiky",
        body: "Prístroj sa pripojí do OBD konektora a začne komunikovať s jednotkami vo vozidle. Až tým sa dostaneme k tomu, čo si zapamätali.",
      },
      {
        name: "Načítané chybové kódy",
        body: "Kódy povedia, ktorý okruh hlási problém. Sú to vodidlá, nie diagnóza — jeden kód vie mať niekoľko rôznych príčin.",
      },
      {
        name: "Oprava",
        body: "Meraním zúžime okruh na konkrétne miesto a opravíme ho. Práve toto je krok, ktorý sa nedá preskočiť výmenou dielu podľa kódu.",
      },
      {
        name: "Vymazané, kontrolky zhasnuté",
        body: "Po oprave pamäť vymažeme a overíme, že sa kontrolka nevráti. Zhasnutá kontrolka bez opravy by znamenala len odložený problém.",
      },
    ],
    codes: [
      { id: "P0401", label: "recirkulácia EGR" },
      { id: "P0299", label: "plniaci tlak" },
      { id: "P0133", label: "lambda sonda" },
    ],
    displayTitle: "CHYBOVÉ KÓDY — UKÁŽKA",
    circuitTitle: "MERANIE OKRUHU",
    circuitPoints: ["napájanie", "poistka", "konektor", "kostra"],
    dialRpm: "ot/min × 1000",
    dialSpeed: "km/h",
    odo: "124 870",
  },

  chat: {
    launcherLabel: "Otvoriť automatického asistenta",
    panelTitle: "Automatický asistent",
    panelSubtitle: "Odpovedá z obsahu tejto stránky",
    automatedBadge: "Automatický asistent, nie človek",
    greeting:
      "Dobrý deň. Odpoviem na otázky o službách, otváracích hodinách a o tom, kde nás nájdete. Na ceny, termíny a trvanie opravy neodpovedám — to vám povedia po telefóne.",
    inputLabel: "Vaša otázka",
    inputPlaceholder: "Napíšte otázku…",
    send: "Odoslať",
    stop: "Zastaviť",
    close: "Zavrieť",
    sourceLabel: "Zdroj",
    errorMessage:
      "Momentálne neviem odpovedať. Zavolajte na +421 918 918 109, tam vám poradia hneď.",
    turnLimit:
      "Pre tentoraz to stačí. S konkrétnym vozidlom vám najlepšie poradia na čísle +421 918 918 109.",
    suggestedLabel: "Môžete sa opýtať",
    starterChips: [
      "Svieti mi kontrolka motora",
      "Robíte geometriu?",
      "Aké máte otváracie hodiny?",
      "Kde vás nájdem?",
    ],
    scriptedNotice:
      "Teraz viem odpovedať len na základné otázky. Na čokoľvek ďalšie zavolajte na {phone}.",
    thinking: "Píše odpoveď",
    feedbackUp: "Odpoveď pomohla",
    feedbackDown: "Odpoveď nepomohla",
    feedbackThanks: "Ďakujeme.",
  },

  widgets: {
    dyno: {
      heading: "Čo robí úprava s krivkou výkonu",
      lead: "Posuvníkom pridávate výkon a vedľa vidíte, ako sa mení krivka. Sivá je východisková, oranžová upravená. Výkon sa počíta z krútiaceho momentu vzťahom P = M × n / 9549, takže obe krivky vždy sedia jedna s druhou.",
      disclaimer:
        "Ide o ilustráciu princípu na typickom motore 2.0 TDI, nie o meranie vášho vozidla a nie o prísľub výsledku. Čo je možné pri konkrétnom motore, závisí od jeho stavu a preberá sa telefonicky:",
      sliderLabel: "Prírastok výkonu",
      power: "Výkon",
      torque: "Krútiaci moment",
      stock: "sériový stav",
      sceneAlt: "Vozidlo na valcovej skúšobni, kolesá sa otáčajú na valcoch.",
      chartAlt: "Graf výkonu a krútiaceho momentu v závislosti od otáčok motora.",
      legendPower: "výkon (kW)",
      legendTorque: "moment (Nm)",
      legendStock: "sériový stav",
    },
    diagnostics: {
      heading: "Od symptómu k príčine",
      lead: "Vyberte, čo vozidlo robí. Uvidíte, koľko príčin prichádza do úvahy a ako sa meraním zužujú na jednu. Presne o tomto je diagnostika — chybový kód je vodidlo, nie diagnóza.",
      disclaimer:
        "Zjednodušená ilustrácia postupu. Skutočný počet aj poradie krokov závisia od vozidla a od toho, čo sa pri meraní ukáže. Popíšte nám, čo auto robí:",
      pick: "Čo vozidlo robí",
      remaining: "Zostáva príčin",
      narrowed: "Zúžené na",
      stepLabel: "Krok merania",
      reset: "Začať znova",
      sceneAlt: "Zoznam možných príčin, ktorý sa meraním postupne zužuje.",
      symptoms: [
        {
          id: "mil",
          label: "Svieti kontrolka motora",
          causes: [
            "snímač tlaku v sacom potrubí",
            "netesnosť sacieho systému",
            "ventil recirkulácie",
            "turbodúchadlo",
            "snímač hmotnosti vzduchu",
            "vstrekovanie",
          ],
          steps: [
            "Načítame uložené kódy a podmienky, za ktorých vznikli.",
            "Porovnáme požadovaný a skutočný plniaci tlak v živých údajoch.",
            "Skúškou tesnosti vylúčime netesnosť sacieho traktu.",
            "Zostáva jedna príčina a tú overíme meraním priamo na komponente.",
          ],
        },
        {
          id: "power",
          label: "Stráca výkon",
          causes: [
            "upchatý filter paliva",
            "regulácia plniaceho tlaku",
            "snímač hmotnosti vzduchu",
            "vôľa v rozvodoch",
            "obmedzenie výfuku",
          ],
          steps: [
            "Overíme, či riadiaca jednotka hlási obmedzenie výkonu a prečo.",
            "Skontrolujeme tlak paliva pod záťažou.",
            "Porovnáme plniaci tlak s požadovanou hodnotou.",
            "Zostáva jedna príčina a tú potvrdíme meraním.",
          ],
        },
        {
          id: "cold",
          label: "Ťažko štartuje za studena",
          causes: [
            "žhaviace sviečky",
            "tesnosť palivovej sústavy",
            "tlak v rail",
            "snímač teploty",
            "stav batérie",
          ],
          steps: [
            "Zmeriame napätie batérie pri štarte.",
            "Overíme činnosť žhavenia a odpor jednotlivých sviečok.",
            "Skontrolujeme, či palivová sústava cez noc drží tlak.",
            "Zostáva jedna príčina a tú potvrdíme meraním.",
          ],
        },
      ],
    },
    alignment: {
      heading: "Ako geometria zjazdí pneumatiku",
      lead: "Posuňte zbiehavosť a odklon kolesa a pozrite sa, čo to urobí s pneumatikou a so správaním vozidla. Pri správnych hodnotách je dezén zjazdený rovnomerne a auto drží smer.",
      disclaimer:
        "Ilustrácia princípu. Správne hodnoty sú pre každé vozidlo iné a určuje ich výrobca; zmerať sa dajú len na vozidle:",
      toe: "Zbiehavosť",
      camber: "Odklon kolesa",
      wear: "Zjazdenie dezénu",
      pull: "Ťahanie do strany",
      ok: "V poriadku",
      sceneAlt: "Schéma nápravy a pneumatika v reze s profilom zjazdenia.",
      wearInner: "po vnútornej hrane",
      wearOuter: "po vonkajšej hrane",
      wearEven: "rovnomerné",
      pullLeft: "doľava",
      pullRight: "doprava",
      pullNone: "žiadne",
      frontView: "pohľad spredu — odklon",
      topView: "pohľad zhora — zbiehavosť",
      section: "rez pneumatikou",
      exaggerated: "Uhly sú na obrázku zväčšené, aby boli viditeľné.",
    },
    tyres: {
      heading: "Hĺbka dezénu a brzdná dráha",
      lead: "Posuňte hĺbku dezénu od novej pneumatiky po zákonné minimum a pozrite sa, čo to urobí s brzdnou dráhou na mokrej vozovke.",
      disclaimer:
        "Orientačné hodnoty z verejne publikovaných testov brzdenia na mokrom, nie meranie vašej pneumatiky. Skutočná dráha závisí od pneumatiky, povrchu aj množstva vody. Stav vašich pneumatík zmeriame:",
      depth: "Hĺbka dezénu",
      braking: "Brzdná dráha na mokrom",
      legalMin: "zákonné minimum",
      versusNew: "oproti novej pneumatike",
      fromSpeed: "z 80 km/h",
      sceneAlt: "Pneumatika v reze s ubúdajúcim dezénom a porovnanie brzdnej dráhy.",
    },
    electrics: {
      heading: "Hľadanie prerušenia v okruhu",
      lead: "Kliknite na jednotlivé body okruhu a zmerajte, kde napätie ešte je a kde už nie. Medzi posledným bodom s napätím a prvým bez neho leží porucha.",
      disclaimer:
        "Zjednodušený okruh pre ilustráciu postupu. Skutočná schéma konkrétneho vozidla má podstatne viac vetiev a konektorov:",
      instruction: "Zmerajte napätie v jednotlivých bodoch",
      measure: "Zmerať",
      reset: "Začať znova",
      found: "Prerušenie je medzi týmito bodmi",
      notMeasured: "nezmerané",
      sceneAlt: "Schéma okruhu od napájania cez poistku a konektor k spotrebiču a kostre.",
      points: [
        { id: "supply", label: "Napájanie" },
        { id: "fuse", label: "Za poistkou" },
        { id: "connector", label: "Za konektorom" },
        { id: "load", label: "Na spotrebiči" },
      ],
    },
    timing: {
      heading: "Prečo sa na rozvody nečaká",
      lead: "Posuňte nájazd a pozrite sa, čo sa deje s remeňom. Kedykoľvek si môžete spustiť, čo nastane pri jeho pretrhnutí — a to je dôvod, prečo sa rozvody menia podľa intervalu a nie podľa stavu.",
      disclaimer:
        "Ilustrácia opotrebenia, nie predpoveď pre vaše vozidlo. Interval výmeny predpisuje výrobca pre konkrétny motor a overíme ho pre vás:",
      mileage: "Nájazd od poslednej výmeny",
      condition: "Stav remeňa",
      interval: "ilustračný interval výmeny",
      run: "Spustiť scenár pretrhnutia",
      reset: "Späť",
      sceneAlt: "Rozvodový remeň s ozubenými kolesami a jeho opotrebenie.",
      states: ["bez viditeľného opotrebenia", "začínajúce opotrebenie zubov", "praskliny, po intervale"],
      failure: "Pretrhnutý remeň",
      failureBody:
        "Vačkový hriadeľ sa zastaví, kľukový beží ďalej. Piest sa stretne s otvoreným ventilom. Z výmeny rozvodov sa stáva oprava hlavy motora.",
    },
    aircon: {
      heading: "Náplň chladiva a teplota z výduchu",
      lead: "Posuňte množstvo chladiva a pozrite sa, ako na to reaguje teplota vzduchu z výduchu. Chladenie neslabne skokom, ale postupne — preto si to vodič všimne až v lete.",
      disclaimer:
        "Ilustrácia princípu pri teplote v kabíne okolo 30 °C, nie meranie vašej klimatizácie. Skutočný stav zistíme na vozidle:",
      charge: "Náplň chladiva",
      ventTemp: "Teplota z výduchu",
      state: "Stav",
      sceneAlt: "Okruh klimatizácie s kompresorom, kondenzátorom a výparníkom.",
      states: ["výrazný nedostatok", "znížená náplň", "správna náplň"],
      parts: ["kompresor", "kondenzátor", "expanzný ventil", "výparník"],
      cabin: "kabína",
    },
  },

  footer: {
    tagline: "Nezávislý autoservis v Ružomberku.",
    servicesHeading: "Služby",
    contactHeading: "Kontakt",
    legalHeading: "Dokumenty",
    rights: "Všetky práva vyhradené.",
    icoLabel: "IČO",
    dicLabel: "DIČ",
    icDphLabel: "IČ DPH",
    registryLabel: "Zápis",
  },

  notFound: {
    title: "Stránka sa nenašla",
    body: "Táto adresa neexistuje. Skúste služby alebo kontakt.",
    cta: "Na úvodnú stránku",
  },
};
