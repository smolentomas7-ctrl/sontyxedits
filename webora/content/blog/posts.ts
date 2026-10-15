import { marketing } from "@/config/images";
import type { ImageSlot } from "@/config/images";
import type { Locale } from "../i18n";

/**
 * Blog content. Both locales share one slug, matching the routing rule that
 * slugs are never translated.
 *
 * `body` is an array of blocks rather than raw HTML so the prose typography
 * stays under our control and nothing unescaped ever reaches the DOM.
 */

export type Block =
  | { type: "p"; text: string }
  | { type: "h2"; text: string }
  | { type: "h3"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "quote"; text: string };

export type Post = {
  slug: string;
  cover: ImageSlot;
  date: string;
  /** Rough reading time in minutes. */
  readMinutes: number;
  category: Record<Locale, string>;
  title: Record<Locale, string>;
  excerpt: Record<Locale, string>;
  body: Record<Locale, Block[]>;
};

export const posts: Post[] = [
  {
    slug: "kolko-stoji-web",
    cover: marketing.blogCost,
    date: "2026-09-02",
    readMinutes: 6,
    category: { sk: "Ceny", en: "Pricing" },
    title: {
      sk: "Koľko má stáť web na Slovensku v roku 2026",
      en: "What a website should cost in Slovakia in 2026",
    },
    excerpt: {
      sk: "Od 300 € po 15 000 €. Prečo je rozptyl taký veľký, čo za tie peniaze naozaj dostanete a kedy je nízka cena varovný signál.",
      en: "From €300 to €15,000. Why the range is so wide, what you actually get for the money, and when a low price is a warning sign.",
    },
    body: {
      sk: [
        {
          type: "p",
          text: "Keď sa pýtate, koľko stojí web, je to podobné, ako keby ste sa pýtali, koľko stojí auto. Odpoveď „od 300 do 15 000 eur“ je pravdivá a zároveň úplne nepoužiteľná. Skúsme ju rozobrať na niečo konkrétnejšie.",
        },
        { type: "h2", text: "Štyri cenové pásma" },
        {
          type: "h3",
          text: "300 – 600 €: šablóna s vaším obsahom",
        },
        {
          type: "p",
          text: "Niekto kúpi hotovú šablónu, doplní do nej vaše logo, texty a fotky a web je za pár dní vonku. Je to legitímna voľba, ak potrebujete hlavne to, aby ste na internete existovali. Nečakajte však originálny vzhľad ani to, že sa niekto bude zaoberať tým, čo má web dosiahnuť.",
        },
        {
          type: "h3",
          text: "600 – 1 500 €: jednostránkový alebo malý viacstránkový web na mieru",
        },
        {
          type: "p",
          text: "Toto je pásmo, v ktorom končí väčšina malých firiem. Dostanete vlastný návrh, nie šablónu, prispôsobenie pre mobil, kontaktný formulár a základnú optimalizáciu pre vyhľadávače. Pri troche šťastia aj niekoho, kto sa vás spýta, kto sú vaši zákazníci.",
        },
        {
          type: "h3",
          text: "1 500 – 5 000 €: firemný web s obsahovou stratégiou",
        },
        {
          type: "p",
          text: "Viac stránok, blog, premyslená štruktúra pre vyhľadávače, pomoc s textami, niekedy aj fotenie. V tomto pásme už web nie je vizitka, ale nástroj, ktorý má privádzať dopyty.",
        },
        {
          type: "h3",
          text: "5 000 € a viac: rozsiahle weby a riešenia na mieru",
        },
        {
          type: "p",
          text: "Web s desiatkami stránok, rezervačným systémom alebo napojením na externé systémy, prípadne vo viacerých jazykových verziách. Cena rastie s počtom integrácií, nie s počtom stránok.",
        },
        { type: "h2", text: "Z čoho sa cena skladá" },
        {
          type: "ul",
          items: [
            "Návrh vzhľadu — čím viac kôl pripomienok, tým vyššia cena.",
            "Programovanie — počet unikátnych typov stránok, nie celkový počet stránok.",
            "Obsah — kto napíše texty a kto zoženie fotky. Toto býva skrytá položka.",
            "Funkcie navyše — rezervácie, kalkulačky, prihlasovanie, viacjazyčnosť.",
            "Nasadenie a zaškolenie — nastavenie domény, hostingu a odovzdanie.",
          ],
        },
        { type: "h2", text: "Kedy je nízka cena varovný signál" },
        {
          type: "p",
          text: "Ak niekto ponúka kompletný firemný web za 200 € do troch dní, zvyčajne to znamená jednu z troch vecí: použije šablónu bez akejkoľvek úpravy, nechá vás napísať úplne všetok obsah a nepozrie sa naň, alebo vás uviaže na platformu, z ktorej sa nedá odísť bez toho, aby ste prišli o web.",
        },
        {
          type: "quote",
          text: "Najdrahší web je ten, ktorý si o rok musíte dať urobiť znova.",
        },
        { type: "h2", text: "Čo sa pýtať pred podpisom" },
        {
          type: "ul",
          items: [
            "Komu bude patriť doména, hosting a zdrojový kód?",
            "Je cena konečná, alebo sa fakturujú zmeny navyše?",
            "Kto píše texty a kto zabezpečuje fotky?",
            "Čo sa stane, keď budem chcieť po roku niečo zmeniť?",
            "Dostanem prístupy do administrácie a zaškolenie?",
          ],
        },
        {
          type: "p",
          text: "Ak na tieto otázky dostanete jasné odpovede, cena je zrazu oveľa menej dôležitá — viete totiž, čo kupujete.",
        },
      ],
      en: [
        {
          type: "p",
          text: "Asking what a website costs is a bit like asking what a car costs. The answer \"somewhere between €300 and €15,000\" is true and completely useless at the same time. Let's break it into something more concrete.",
        },
        { type: "h2", text: "Four price brackets" },
        { type: "h3", text: "€300 – €600: a template with your content in it" },
        {
          type: "p",
          text: "Someone buys a ready-made template, drops in your logo, text and photos, and the site is live in a few days. It is a legitimate choice if what you mainly need is to exist online. Do not expect an original design, or for anyone to think about what the site has to achieve.",
        },
        { type: "h3", text: "€600 – €1,500: a custom one-page or small multi-page site" },
        {
          type: "p",
          text: "This is where most small businesses land. You get a design made for you rather than a template, mobile layouts, a contact form and basic search optimisation. With luck, also someone who asks who your customers actually are.",
        },
        { type: "h3", text: "€1,500 – €5,000: a business site with a content strategy" },
        {
          type: "p",
          text: "More pages, a blog, a structure thought through for search engines, help with the copy, sometimes a photo shoot. In this bracket the site stops being a business card and starts being a tool that brings in enquiries.",
        },
        { type: "h3", text: "€5,000 and up: large sites and bespoke builds" },
        {
          type: "p",
          text: "A site with dozens of pages, a booking system or connections to external systems, possibly in several language versions. The price rises with the number of integrations, not the number of pages.",
        },
        { type: "h2", text: "What makes up the price" },
        {
          type: "ul",
          items: [
            "Design — the more rounds of revisions, the higher the cost.",
            "Build — the number of distinct page types, not the total page count.",
            "Content — who writes the copy and who sources the photos. This is the usual hidden line.",
            "Extra features — bookings, calculators, logins, multiple languages.",
            "Deployment and training — domain and hosting setup, and the handover.",
          ],
        },
        { type: "h2", text: "When a low price is a warning sign" },
        {
          type: "p",
          text: "If someone offers a complete business website for €200 in three days, it usually means one of three things: they will use a template with no adjustment at all, they will have you write every word and never look at it, or they will tie you to a platform you cannot leave without losing the site.",
        },
        { type: "quote", text: "The most expensive website is the one you have to rebuild a year later." },
        { type: "h2", text: "What to ask before you sign" },
        {
          type: "ul",
          items: [
            "Who will own the domain, the hosting and the source code?",
            "Is the price final, or are changes billed on top?",
            "Who writes the copy and who provides the photos?",
            "What happens when I want to change something a year from now?",
            "Will I get admin access and training?",
          ],
        },
        {
          type: "p",
          text: "If you get clear answers to those, the price suddenly matters a lot less — because you know what you are buying.",
        },
      ],
    },
  },

  {
    slug: "co-si-pripravit",
    cover: marketing.blogPrepare,
    date: "2026-09-10",
    readMinutes: 5,
    category: { sk: "Príprava", en: "Preparation" },
    title: {
      sk: "Čo si pripraviť, než si objednáte web",
      en: "What to prepare before you order a website",
    },
    excerpt: {
      sk: "Projekty sa nepredlžujú kvôli programovaniu, ale kvôli čakaniu na podklady. Tu je zoznam, ktorý to vyrieši.",
      en: "Projects do not slip because of the build. They slip waiting for materials. Here is the list that fixes that.",
    },
    body: {
      sk: [
        {
          type: "p",
          text: "Skúsenosť z každého projektu je rovnaká: programovanie trvá týždeň, čakanie na texty tri. Ak si pripravíte nižšie uvedené veci ešte pred prvým stretnutím, skrátite dodanie aj o polovicu.",
        },
        { type: "h2", text: "1. Vedieť, čo má web dosiahnuť" },
        {
          type: "p",
          text: "Toto je jediná položka, ktorú za vás nikto neurobí. Má web zbierať dopyty? Predávať? Odbremeniť telefón od opakujúcich sa otázok? Rôzne ciele vedú k úplne odlišným webom. Napíšte si jednu vetu: „Web je úspešný, keď…“",
        },
        { type: "h2", text: "2. Zoznam toho, čo predávate" },
        {
          type: "p",
          text: "Nie marketingový text, len vecný zoznam služieb alebo produktov. Pri každej položke jedna veta o tom, pre koho je, a orientačná cena, ak ju chcete zverejniť.",
        },
        { type: "h2", text: "3. Texty, aj keď nie sú pekné" },
        {
          type: "p",
          text: "Mnohí klienti čakajú, kým napíšu „poriadny“ text, a tým brzdia celý projekt. Pošlite surový text — radšej päť odsekov v poznámkach v telefóne ako nič. Prepísať existujúci text je rýchlejšie, než vymyslieť ho od nuly.",
        },
        { type: "h2", text: "4. Fotky v použiteľnej kvalite" },
        {
          type: "ul",
          items: [
            "Minimálne 1 600 px na šírku, ideálne priamo z fotoaparátu alebo novšieho telefónu.",
            "Nie screenshoty z Facebooku a nie fotky stiahnuté z Google — sú malé a často chránené autorským právom.",
            "Fotky vašich skutočných priestorov a práce fungujú lepšie než stock.",
          ],
        },
        { type: "h2", text: "5. Logo v pôvodnom formáte" },
        {
          type: "p",
          text: "Ak máte logo, nájdite súbor od grafika — ideálne SVG, AI alebo PDF. JPG s bielym pozadím sa na tmavom webe nedá použiť bez kompromisov. Ak originál nemáte, povedzte to vopred.",
        },
        { type: "h2", text: "6. Prístupy, ak web už máte" },
        {
          type: "p",
          text: "Doména, hosting, administrácia, Google Analytics, Google Business Profile. Zháňanie zabudnutých hesiel od bývalého dodávateľa býva najdlhšia časť celého projektu.",
        },
        { type: "h2", text: "7. Dva alebo tri weby, ktoré sa vám páčia" },
        {
          type: "p",
          text: "Nemusia byť z vášho odvetvia. Pri každom napíšte jednu vetu o tom, čo konkrétne sa vám na ňom páči. „Páči sa mi, ako majú jednoducho spravené ceny“ povie dizajnérovi viac než hodina abstraktnej debaty.",
        },
        {
          type: "p",
          text: "Ak máte týchto sedem vecí, prvé stretnutie trvá štyridsať minút namiesto dvoch hodín a termín dodania platí.",
        },
      ],
      en: [
        {
          type: "p",
          text: "Every project tells the same story: the build takes a week, waiting for the text takes three. Prepare the things below before the first meeting and you can halve the delivery time.",
        },
        { type: "h2", text: "1. Know what the site has to achieve" },
        {
          type: "p",
          text: "This is the one item nobody can do for you. Should the site collect enquiries? Sell? Take repetitive questions off the phone? Different goals produce completely different websites. Write one sentence: \"The site is a success when…\"",
        },
        { type: "h2", text: "2. A list of what you sell" },
        {
          type: "p",
          text: "Not marketing copy, just a plain list of services or products. One sentence per item about who it is for, and an indicative price if you want to publish one.",
        },
        { type: "h2", text: "3. Text, even if it is not polished" },
        {
          type: "p",
          text: "Many clients wait until they have written something \"proper\" and hold up the whole project doing it. Send the rough version — five paragraphs in your phone's notes app beats nothing. Rewriting existing text is far quicker than inventing it from scratch.",
        },
        { type: "h2", text: "4. Photos at a usable size" },
        {
          type: "ul",
          items: [
            "At least 1,600 px wide, ideally straight from a camera or a recent phone.",
            "Not screenshots from Facebook and not images pulled off Google — they are small and often copyrighted.",
            "Photos of your real premises and real work beat stock every time.",
          ],
        },
        { type: "h2", text: "5. Your logo in its original format" },
        {
          type: "p",
          text: "If you have a logo, find the designer's file — ideally SVG, AI or PDF. A JPG with a white background cannot be used on a dark site without compromises. If you do not have the original, say so up front.",
        },
        { type: "h2", text: "6. Logins, if you already have a site" },
        {
          type: "p",
          text: "Domain, hosting, admin area, Google Analytics, Google Business Profile. Chasing forgotten passwords from a previous supplier is routinely the longest part of a project.",
        },
        { type: "h2", text: "7. Two or three sites you like" },
        {
          type: "p",
          text: "They do not need to be from your industry. For each one, write a sentence about what specifically you like. \"I like how simply they handle pricing\" tells a designer more than an hour of abstract discussion.",
        },
        {
          type: "p",
          text: "With those seven things in hand, the first meeting takes forty minutes instead of two hours — and the delivery date holds.",
        },
      ],
    },
  },

  {
    slug: "google-business-profile",
    cover: marketing.blogGbp,
    date: "2026-09-18",
    readMinutes: 5,
    category: { sk: "Lokálne SEO", en: "Local SEO" },
    title: {
      sk: "Prečo vaša firma potrebuje Google Business Profile",
      en: "Why your business needs a Google Business Profile",
    },
    excerpt: {
      sk: "Bezplatný nástroj, ktorý pre lokálnu firmu často prinesie viac zákazníkov než samotný web. A väčšina ho má vyplnený zle.",
      en: "A free tool that often brings a local business more customers than its website does. And most are filled in badly.",
    },
    body: {
      sk: [
        {
          type: "p",
          text: "Keď niekto hľadá „kaviareň v okolí“ alebo „inštalatér Žilina“, prvé, čo uvidí, nie je váš web. Je to mapa s tromi firmami a hviezdičkami. To je Google Business Profile a je zadarmo.",
        },
        { type: "h2", text: "Čo to vlastne je" },
        {
          type: "p",
          text: "Profil firmy, ktorý sa zobrazuje vo vyhľadávaní a v Mapách. Obsahuje otváracie hodiny, adresu, telefón, fotky, recenzie a odkaz na web. Pre lokálne služby je to často dôležitejšie než samotná webová stránka — zákazník si len potrebuje overiť, že existujete a máte otvorené.",
        },
        { type: "h2", text: "Päť chýb, ktoré vidíme najčastejšie" },
        { type: "h3", text: "1. Nevyplnené alebo neaktuálne otváracie hodiny" },
        {
          type: "p",
          text: "Najhoršia možná chyba. Zákazník príde pred zatvorené dvere a nabudúce už nepríde vôbec. Nezabudnite na sviatky — Google na ne upozorňuje, väčšina firiem to ignoruje.",
        },
        { type: "h3", text: "2. Žiadne fotky, alebo tri rozmazané spred piatich rokov" },
        {
          type: "p",
          text: "Profily s fotkami dostávajú výrazne viac kliknutí. Stačí desať slušných záberov z telefónu: interiér, exteriér, produkt, ľudia pri práci.",
        },
        { type: "h3", text: "3. Zle zvolená kategória" },
        {
          type: "p",
          text: "Kategória rozhoduje o tom, pri akých hľadaniach sa zobrazíte. „Reštaurácia“ a „kaviareň“ sú dva veľmi odlišné výsledky vyhľadávania.",
        },
        { type: "h3", text: "4. Ignorované recenzie" },
        {
          type: "p",
          text: "Odpovedajte na všetky, aj na tie dobré, a hlavne pokojne na tie zlé. Verejná, vecná odpoveď na kritiku pôsobí lepšie než desať päťhviezdičkových hodnotení bez reakcie.",
        },
        { type: "h3", text: "5. Chýbajúci odkaz na web" },
        {
          type: "p",
          text: "Znie to triviálne, no chýba to prekvapivo často. Odkaz by mal viesť na hlavnú stránku, nie na Facebook.",
        },
        { type: "h2", text: "Ako to prepojiť s webom" },
        {
          type: "ul",
          items: [
            "Rovnaký názov, adresa a telefón na webe aj v profile, znak po znaku.",
            "Otváracie hodiny uvádzajte na obidvoch miestach a meňte ich naraz.",
            "Na web pridajte štruktúrované dáta o firme, aby si Google údaje overil.",
          ],
        },
        {
          type: "p",
          text: "Vyplnenie profilu trvá hodinu a je zadarmo. Pri lokálnej firme je to pravdepodobne najlepšie zhodnotená hodina marketingu, akú tento rok strávite.",
        },
      ],
      en: [
        {
          type: "p",
          text: "When somebody searches for \"coffee shop near me\" or \"plumber Bratislava\", the first thing they see is not your website. It is a map with three businesses and star ratings. That is Google Business Profile, and it is free.",
        },
        { type: "h2", text: "What it actually is" },
        {
          type: "p",
          text: "A business profile shown in search results and in Maps. It holds your opening hours, address, phone number, photos, reviews and a link to your site. For local services it is often more important than the website itself — the customer just needs to confirm you exist and you are open.",
        },
        { type: "h2", text: "The five mistakes we see most" },
        { type: "h3", text: "1. Missing or out-of-date opening hours" },
        {
          type: "p",
          text: "The worst mistake there is. A customer turns up to a closed door and does not come back. Do not forget public holidays — Google prompts you about them and most businesses ignore it.",
        },
        { type: "h3", text: "2. No photos, or three blurry ones from five years ago" },
        {
          type: "p",
          text: "Profiles with photos get substantially more clicks. Ten decent phone shots are enough: the interior, the exterior, the product, people at work.",
        },
        { type: "h3", text: "3. The wrong category" },
        {
          type: "p",
          text: "The category decides which searches you appear in. \"Restaurant\" and \"café\" are two very different sets of results.",
        },
        { type: "h3", text: "4. Ignored reviews" },
        {
          type: "p",
          text: "Reply to all of them, including the good ones, and above all calmly to the bad ones. A public, factual reply to criticism reads better than ten five-star ratings nobody acknowledged.",
        },
        { type: "h3", text: "5. No link to the website" },
        {
          type: "p",
          text: "It sounds trivial, but it is missing surprisingly often. The link should go to your home page, not to Facebook.",
        },
        { type: "h2", text: "Connecting it to your site" },
        {
          type: "ul",
          items: [
            "The same business name, address and phone number on the site and in the profile, character for character.",
            "Publish opening hours in both places and change them at the same time.",
            "Add structured business data to the site so Google can verify the details.",
          ],
        },
        {
          type: "p",
          text: "Filling in the profile takes an hour and costs nothing. For a local business it is probably the best-spent marketing hour of your year.",
        },
      ],
    },
  },

  {
    slug: "kedy-redizajn",
    cover: marketing.blogRedesign,
    date: "2026-09-25",
    readMinutes: 6,
    category: { sk: "Redizajn", en: "Redesign" },
    title: {
      sk: "7 signálov, že váš web potrebuje redizajn",
      en: "7 signs your website needs a redesign",
    },
    excerpt: {
      sk: "Nie každý starší web treba vyhodiť. Tu je sedem konkrétnych signálov, pri ktorých sa redizajn naozaj oplatí.",
      en: "Not every older site needs throwing away. Here are seven concrete signs that a redesign genuinely pays off.",
    },
    body: {
      sk: [
        {
          type: "p",
          text: "Web nie je zlý len preto, že je starý. Niektoré stránky spred desiatich rokov fungujú lepšie než novšie, pretože majú jasnú štruktúru. Tu sú signály, ktoré sú skutočným dôvodom na prerobenie.",
        },
        { type: "h2", text: "1. Na mobile sa nedá používať" },
        {
          type: "p",
          text: "Otvorte si vlastný web na telefóne. Musíte približovať, aby ste prečítali text? Je telefónne číslo neklikateľné? Viac než polovica návštevníkov malých firiem prichádza z mobilu, takže toto nie je kozmetická chyba.",
        },
        { type: "h2", text: "2. Načítava sa dlhšie než tri sekundy" },
        {
          type: "p",
          text: "Otestujte si ho v PageSpeed Insights. Najčastejšia príčina sú nezmenšené fotky nahrané priamo z fotoaparátu — jeden obrázok s 6 MB dokáže položiť celú stránku.",
        },
        { type: "h2", text: "3. Nedá sa aktualizovať bez programátora" },
        {
          type: "p",
          text: "Ak musíte volať dodávateľovi kvôli zmene otváracích hodín, web neaktualizujete a postupne na ňom ostanú nepravdivé informácie.",
        },
        { type: "h2", text: "4. Návštevníci odchádzajú z hlavnej stránky" },
        {
          type: "p",
          text: "V analytike sa pozrite, koľko ľudí odíde bez toho, aby klikli ďalej. Ak je to nad 70 %, stránka zrejme nehovorí dostatočne rýchlo, čo robíte.",
        },
        { type: "h2", text: "5. Nezodpovedá tomu, čo dnes robíte" },
        {
          type: "p",
          text: "Firmy sa menia rýchlejšie než ich weby. Ak máte na stránke služby, ktoré už neposkytujete, a chýbajú tie, z ktorých dnes žijete, nejde o dizajn, ale o obsah.",
        },
        { type: "h2", text: "6. Hanbíte sa poslať naň odkaz" },
        {
          type: "p",
          text: "Toto je neformálny, ale veľmi spoľahlivý test. Ak pri odovzdávaní vizitky dodávate „ten web už prerábame“, odpoveď poznáte.",
        },
        { type: "h2", text: "7. Nemáte HTTPS" },
        {
          type: "p",
          text: "Ak sa v adresnom riadku zobrazuje upozornenie „Nezabezpečené“, časť návštevníkov odíde okamžite. Certifikát je dnes zadarmo a nastavuje sa za pár minút.",
        },
        { type: "h2", text: "Kedy redizajn nepotrebujete" },
        {
          type: "p",
          text: "Ak sa vám web len „zunoval“, ale funguje na mobile, načítava sa rýchlo a prináša dopyty, nechajte ho. Peniaze sa v takom prípade lepšie zhodnotia v obsahu alebo v reklame.",
        },
        {
          type: "quote",
          text: "Redizajn, ktorý rieši vkus majiteľa a nie problém zákazníka, zvyčajne zhorší výsledky.",
        },
      ],
      en: [
        {
          type: "p",
          text: "A website is not bad simply because it is old. Some ten-year-old sites work better than newer ones because their structure is clear. Here are the signs that are a genuine reason to rebuild.",
        },
        { type: "h2", text: "1. It is unusable on a phone" },
        {
          type: "p",
          text: "Open your own site on your phone. Do you have to pinch to read the text? Is the phone number untappable? More than half of a small business's visitors arrive on mobile, so this is not a cosmetic issue.",
        },
        { type: "h2", text: "2. It takes more than three seconds to load" },
        {
          type: "p",
          text: "Test it in PageSpeed Insights. The usual culprit is un-resized photos uploaded straight from a camera — a single 6 MB image can sink a whole page.",
        },
        { type: "h2", text: "3. You cannot update it without a developer" },
        {
          type: "p",
          text: "If you have to call your supplier to change your opening hours, you will not update the site, and false information will gradually settle on it.",
        },
        { type: "h2", text: "4. Visitors leave from the home page" },
        {
          type: "p",
          text: "Check your analytics for how many people leave without clicking further. Above 70% and the page is probably not saying what you do quickly enough.",
        },
        { type: "h2", text: "5. It no longer reflects what you do" },
        {
          type: "p",
          text: "Businesses change faster than their websites. If the site lists services you no longer offer and omits the ones you live on today, the problem is content, not design.",
        },
        { type: "h2", text: "6. You are embarrassed to send the link" },
        {
          type: "p",
          text: "An informal test, but a very reliable one. If you hand over a business card while saying \"we're redoing the site\", you already know the answer.",
        },
        { type: "h2", text: "7. You do not have HTTPS" },
        {
          type: "p",
          text: "If the address bar shows a \"Not secure\" warning, some visitors leave immediately. A certificate is free these days and takes minutes to set up.",
        },
        { type: "h2", text: "When you do not need a redesign" },
        {
          type: "p",
          text: "If you have simply grown tired of the site but it works on mobile, loads fast and brings in enquiries, leave it alone. The money is better spent on content or advertising.",
        },
        {
          type: "quote",
          text: "A redesign that solves the owner's taste rather than the customer's problem usually makes the results worse.",
        },
      ],
    },
  },

  {
    slug: "ako-pisat-texty",
    cover: marketing.blogCopy,
    date: "2026-10-01",
    readMinutes: 6,
    category: { sk: "Obsah", en: "Content" },
    title: {
      sk: "Ako si napísať texty na vlastný web",
      en: "How to write the text for your own website",
    },
    excerpt: {
      sk: "Nemusíte byť copywriter. Stačí prestať písať, ako keby ste písali úradný list, a odpovedať na otázky, ktoré zákazník naozaj má.",
      en: "You do not need to be a copywriter. Just stop writing like it is an official letter and answer the questions the customer actually has.",
    },
    body: {
      sk: [
        {
          type: "p",
          text: "Väčšina textov na firemných weboch znie rovnako: „Sme dynamicky sa rozvíjajúca spoločnosť s dlhoročnou tradíciou a individuálnym prístupom ku každému klientovi.“ Táto veta neznamená nič a dá sa použiť pre pekárňu aj pre softvérovú firmu. Dá sa to lepšie — aj bez copywritera.",
        },
        { type: "h2", text: "Začnite otázkami, nie vetami" },
        {
          type: "p",
          text: "Spomeňte si na posledných päť zákazníkov. Čo sa vás pýtali po telefóne? „Koľko to stojí?“, „Dokedy to viete urobiť?“, „Robíte aj u nás v dedine?“ Toto sú skutočné otázky a web, ktorý na ne odpovedá, je lepší než akýkoľvek slohový útvar.",
        },
        { type: "h2", text: "Hlavná stránka: povedzte to v prvej vete" },
        {
          type: "p",
          text: "Návštevník sa rozhoduje za pár sekúnd. Prvý nadpis by mal povedať, čo robíte a pre koho, bez metafor. „Rekonštrukcie bytov v Košiciach a okolí“ je lepší nadpis než „Váš domov, naša vášeň“.",
        },
        { type: "h2", text: "Píšte „vy“, nie „my“" },
        {
          type: "p",
          text: "Porovnajte: „Disponujeme moderným strojovým parkom“ verzus „Zákazku dokončíme do dvoch týždňov, lebo nečakáme na externé stroje.“ Druhá veta hovorí o tom istom, ale z pohľadu zákazníka.",
        },
        { type: "h2", text: "Konkrétnosť namiesto prídavných mien" },
        {
          type: "ul",
          items: [
            "Nie „rýchle dodanie“, ale „do 7 pracovných dní“.",
            "Nie „kvalitné materiály“, ale „dubová škárovka, 40 mm“.",
            "Nie „dlhoročné skúsenosti“, ale „od roku 2019“.",
            "Nie „férové ceny“, ale konkrétna cena alebo rozpätie.",
          ],
        },
        { type: "h2", text: "Ceny uvádzajte, aj keď sú „od“" },
        {
          type: "p",
          text: "Najčastejšia obava: „keď dáme ceny, odradíme ľudí“. V skutočnosti odradíte tých, ktorí by si to aj tak nemohli dovoliť, a ušetríte si hodiny telefonátov. Zvyšok ocení, že vedia, do čoho idú.",
        },
        { type: "h2", text: "Praktický postup na jeden večer" },
        {
          type: "ul",
          items: [
            "Napíšte päť otázok, ktoré dostávate najčastejšie.",
            "Odpovedzte na ne tak, ako by ste odpovedali po telefóne. Nahrajte si to a prepíšte, ak sa vám tak píše ľahšie.",
            "Vyhoďte každú vetu, ktorá by mohla stáť na webe konkurencie.",
            "Prečítajte si to nahlas. Kde sa zaseknete, tam je veta zlá.",
          ],
        },
        {
          type: "quote",
          text: "Dobrý text na webe znie ako váš najlepší predajca, keď hovorí so zákazníkom, ktorý sa ponáhľa.",
        },
        {
          type: "p",
          text: "Ak po tomto postupe stále nie ste spokojní, pošlite nám surový text. Prepísať existujúce vety je výrazne lacnejšie než písať celý web od nuly.",
        },
      ],
      en: [
        {
          type: "p",
          text: "Most copy on business websites sounds identical: \"We are a dynamically growing company with a long tradition and an individual approach to every client.\" That sentence means nothing and would fit a bakery as well as a software firm. You can do better — without hiring a copywriter.",
        },
        { type: "h2", text: "Start with questions, not sentences" },
        {
          type: "p",
          text: "Think of your last five customers. What did they ask on the phone? \"How much is it?\", \"How soon can you do it?\", \"Do you come out to our village?\" Those are the real questions, and a site that answers them beats any amount of prose.",
        },
        { type: "h2", text: "Home page: say it in the first sentence" },
        {
          type: "p",
          text: "A visitor decides in a few seconds. The first heading should say what you do and who for, with no metaphors. \"Flat renovations in Košice and the surrounding area\" is a better heading than \"Your home, our passion\".",
        },
        { type: "h2", text: "Write \"you\", not \"we\"" },
        {
          type: "p",
          text: "Compare: \"We operate a modern machine park\" against \"We'll finish the job within two weeks because we're not waiting on hired machinery.\" The second says the same thing from the customer's side.",
        },
        { type: "h2", text: "Specifics instead of adjectives" },
        {
          type: "ul",
          items: [
            "Not \"fast delivery\" but \"within 7 working days\".",
            "Not \"quality materials\" but \"40 mm solid oak board\".",
            "Not \"years of experience\" but \"since 2019\".",
            "Not \"fair prices\" but an actual price or range.",
          ],
        },
        { type: "h2", text: "Publish prices, even as a \"from\"" },
        {
          type: "p",
          text: "The usual worry: \"if we publish prices we'll put people off\". In reality you put off the people who could not have afforded it anyway, and you save yourself hours of phone calls. Everyone else appreciates knowing what they are getting into.",
        },
        { type: "h2", text: "A practical method for one evening" },
        {
          type: "ul",
          items: [
            "Write down the five questions you are asked most often.",
            "Answer them the way you would on the phone. Record yourself and transcribe it if that comes more easily.",
            "Delete every sentence that could sit on a competitor's website unchanged.",
            "Read it aloud. Wherever you stumble, the sentence is wrong.",
          ],
        },
        {
          type: "quote",
          text: "Good website copy sounds like your best salesperson talking to a customer who is in a hurry.",
        },
        {
          type: "p",
          text: "If you are still not happy after all that, send us the raw text. Rewriting existing sentences is considerably cheaper than writing a whole site from scratch.",
        },
      ],
    },
  },
];

export function getPost(slug: string): Post | undefined {
  return posts.find((post) => post.slug === slug);
}

/** Posts newest first. */
export function sortedPosts(): Post[] {
  return [...posts].sort((a, b) => (a.date < b.date ? 1 : -1));
}
