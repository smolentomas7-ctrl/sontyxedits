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
    toConfirmLabel: "Na doplnenie",
    placeholderLabel: "Na doplnenie klientom",
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
      "Potiahnite posuvník a prejdite si, čo sa deje medzi tým, ako sa kontrolka rozsvieti, a tým, ako zhasne.",
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
      "Sedem oblastí, ktorým sa venujeme. Pri každej nájdete, kedy ju riešiť a ako postupujeme. Čo nie je potvrdené, je ako nepotvrdené aj označené.",
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
      toConfirm: ["[TO CONFIRM: ktoré značky a systémy diagnostika pokrýva]"],
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
      toConfirm: [
        "[TO CONFIRM: aké typy úprav ECU servis vykonáva a pre ktoré motory]",
      ],
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
      toConfirm: [
        "[TO CONFIRM: typ geometrie (3D/laser), ktoré vozidlá a rozmery servis zvláda]",
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
        "Práca s pneumatikami a diskami. Presný rozsah služieb si potvrďte telefonicky.",
      lead:
        "Pneumatiky sú jediná časť vozidla, ktorá sa dotýka vozovky. Na ich stave závisí brzdná dráha aj správanie v zákrute. Pneuservis zahŕňa prácu s pneumatikami a diskami; aký presný rozsah u nás viete využiť, si overte telefonicky — nižšie je to označené ako nepotvrdené.",
      overview:
        "Pneumatiky sú jediný kontakt vozidla s vozovkou. Aký presný rozsah pneuservisu ponúkame, zatiaľ nie je potvrdený.",
      covers: [
        "Práca s pneumatikami a diskami",
        "Posúdenie stavu pneumatík",
        "Rozsah služieb na potvrdenie telefonicky",
      ],
      when: [
        "Blíži sa sezóna a potrebujete prejsť na zimné alebo letné pneumatiky.",
        "Pneumatika stráca tlak alebo ste prešli cez niečo ostré.",
        "Pri vyšších rýchlostiach cítite vo volante alebo v sedadle vibrácie.",
        "Dezén je blízko zákonného minima alebo je zjazdený nerovnomerne.",
      ],
      what: [
        "Pozrieme sa na stav pneumatík a diskov a povieme, čo vidíme.",
        "Dohodneme, čo je potrebné urobiť.",
        "Konkrétny rozsah prác si potvrďte telefonicky — pozrite poznámku nižšie.",
      ],
      toConfirm: [
        "[TO CONFIRM: či ponuka zahŕňa prezúvanie, vyvažovanie, sezónnu výmenu, opravu defektov a uskladnenie pneumatík]",
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
      toConfirm: ["[TO CONFIRM: aké konkrétne elektro opravy servis vykonáva]"],
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
      toConfirm: [
        "[TO CONFIRM: úplný zoznam podporovaných motorov a či výmena zahŕňa vodné čerpadlo]",
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
        "Klimatizácia, ktorá nechladí, býva o chladive alebo o netesnosti. Rozsah si potvrďte telefonicky.",
      lead:
        "Klimatizácia stráca chladivo aj bez poruchy — netesnosťami, ktoré sú súčasťou systému. Keď chladenie postupne slabne, dôvodom býva nedostatok chladiva alebo únik. Aký presný rozsah servisu klimatizácie u nás viete využiť, si overte telefonicky; nižšie je to označené ako nepotvrdené.",
      overview:
        "Chladenie slabne postupne, takže si to vodič všimne až v lete. Presný rozsah servisu klimatizácie zatiaľ nie je potvrdený.",
      covers: [
        "Posúdenie stavu klimatizácie",
        "Rozsah služieb na potvrdenie telefonicky",
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
        "Pozrieme sa na systém a povieme, čo vidíme.",
        "Dohodneme ďalší postup — konkrétny rozsah si potvrďte telefonicky.",
      ],
      toConfirm: [
        "[TO CONFIRM: či servis zahŕňa diagnostiku, plnenie chladiva, detekciu únikov, čistenie, dezinfekciu alebo opravy; a ktoré chladivá (R134a / R1234yf)]",
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
      "M.I.Auto s.r.o. je nezávislý autoservis v Ružomberku. Na tejto stránke je zatiaľ len to, čo je potvrdené — zvyšok dopĺňa klient.",
    whatWeDoHeading: "Čomu sa venujeme",
    quietHeading: "Ako k tomu pristupujeme",
    quietBody: [
      "Väčšina porúch sa prejaví inde, než vzniká. Kontrolka motora nehovorí, ktorý diel je pokazený — hovorí, že niektorá riadiaca jednotka zaznamenala hodnotu mimo očakávania. Medzi tými dvoma vetami je celá práca.",
      "Preto sa chybový kód overuje meraním. Je to pomalšie než vymeniť diel, ktorý kód spomína, ale je to jediný spôsob, ako nevymeniť diel, ktorý bol v poriadku.",
      "To isté platí pre elektriku a pre rozvody. Pri elektrike sa postupuje podľa schémy a vylučovaním. Pri rozvodoch sa nečaká na poruchu, pretože keď rozvod zlyhá, oprava už nie je o rozvode.",
    ],
    ownerHeading: "Majiteľ",
    ownerRole: "Majiteľ servisu",
    placeholderShop: "[TEXT O SERVISE — doplní klient]",
    placeholderOwner: "[TEXT O MAJITEĽOVI — doplní klient]",
    factsHeading: "Kde nás nájdete",
    interiorAlt: "Interiér dielne M.I.Auto, vozidlá počas servisu",
    detail01Alt: "Vozidlo zdvihnuté na dvojstĺpovom zdviháku v dielni M.I.Auto",
    detail02Alt: "Terénne vozidlo na zdviháku v dielni M.I.Auto",
  },

  contact: {
    meta: {
      title: "Kontakt | M.I.Auto s.r.o. Ružomberok",
      description:
        "Sládkovičova 2528/108, 034 01 Ružomberok. Otvorené pondelok až piatok 08:00–16:00. Zavolajte na +421 918 918 109 alebo napíšte cez formulár.",
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
    emailPendingNote:
      "E-mailová adresa zatiaľ nie je doplnená. Použite telefón alebo formulár.",
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
      a: "Pondelok až piatok od 08:00 do 16:00. V sobotu a v nedeľu je zatvorené.",
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
        "Aké údaje zbiera kontaktný formulár, ako funguje vložená mapa Google a čo robí automatický asistent. Otázky k svojim údajom: +421 918 918 109.",
    },
    h1: "Ochrana osobných údajov",
    reviewNotice:
      "Tento dokument je ŠABLÓNA a nie je právne posúdený. Pred zverejnením stránky ho musí skontrolovať a doplniť osoba s právnou kvalifikáciou. Netvrdíme, že je v súlade s GDPR ani s iným predpisom.",
    updated: "Posledná úprava: pri nasadení stránky",
    sections: [
      {
        heading: "Kto spracúva údaje",
        body: [
          "Prevádzkovateľom je M.I.Auto s.r.o., Sládkovičova 2528/108, 034 01 Ružomberok.",
          "IČO: [IČO]",
          "Kontakt: +421 918 918 109, [EMAIL]",
        ],
      },
      {
        heading: "Kontaktný formulár",
        body: [
          "Formulár na stránke Kontakt zbiera meno, telefónne číslo, nepovinne e-mail, nepovinne údaj o vozidle, vybranú službu a text správy.",
          "Tieto údaje sa používajú výlučne na to, aby sme vám na správu odpovedali. Nepoužívajú sa na marketing a neposkytujú sa tretím stranám na ich vlastné účely.",
          "Odoslaný formulár spracúva služba Netlify Forms, ktorá správu uloží a sprístupní nám. Dáta sú teda uložené na infraštruktúre poskytovateľa Netlify.",
          "[TO CONFIRM: ako dlho sa odoslané správy uchovávajú a kto k nim má prístup]",
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
          "Prepis rozhovoru sa ukladá len vo vašom prehliadači (sessionStorage) a po zatvorení karty zaniká. Na našej strane sa prepisy neuchovávajú.",
          "Ak je asistent nastavený na jazykový model, text vašej otázky sa odošle poskytovateľovi modelu, aby vedel odpovedať. Neposielame k nemu vaše meno, telefón ani e-mail — asistent o ne nežiada a nemá na ne prístup.",
          "O prevádzke zaznamenávame len technické údaje: čas, jazyk, trvanie odpovede, počet tokenov a to, či sa použila záložná odpoveď. Text správ nezaznamenávame.",
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
          "Jediný externý obsah je mapa Google opísaná vyššie.",
        ],
      },
      {
        heading: "Vaše práva",
        body: [
          "[TO CONFIRM: znenie kapitoly o právach dotknutej osoby — doplní osoba s právnou kvalifikáciou]",
          "S otázkami o svojich údajoch sa obráťte na kontakty uvedené vyššie.",
        ],
      },
    ],
  },

  signature: {
    title: "Od kontrolky k oprave",
    instructions:
      "Potiahnite posuvník alebo použite šípky na klávesnici a prejdite si päť fáz.",
    keyboardHint:
      "Šípky posúvajú po malých krokoch, Page Up a Page Down po fázach, Home a End na začiatok a koniec.",
    svgTitle:
      "Schéma prístrojovky: po oprave je prístrojovka bez svietiacich výstražných kontroliek.",
    stageLabel: "Fáza",
    stages: [
      "Kontrolka svieti",
      "Pripojenie diagnostiky",
      "Načítané chybové kódy",
      "Oprava",
      "Vymazané, kontrolky zhasnuté",
    ],
    codeListLabel: "Zoznam chybových kódov (ukážkový, nie skutočné kódy)",
    codeRowLabel: "Chybový kód",
    dashboardLabel: "Prístrojovka",
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
    scriptedNotice: "Odpovede sú pripravené vopred.",
    thinking: "Píše odpoveď",
    feedbackUp: "Odpoveď pomohla",
    feedbackDown: "Odpoveď nepomohla",
    feedbackThanks: "Ďakujeme.",
  },

  footer: {
    tagline: "Nezávislý autoservis v Ružomberku.",
    servicesHeading: "Služby",
    contactHeading: "Kontakt",
    legalHeading: "Dokumenty",
    rights: "Všetky práva vyhradené.",
    icoLabel: "IČO",
  },

  notFound: {
    title: "Stránka sa nenašla",
    body: "Táto adresa neexistuje. Skúste služby alebo kontakt.",
    cta: "Na úvodnú stránku",
  },
};
