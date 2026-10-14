# M.I.Auto s.r.o. — stav webu pred spustením

Dokument k odovzdaniu. Opisuje, čo je na stránke hotové, čo musí doplniť klient
predtým, než sa spustí, čo by jej pomohlo, a ako sa nasadzuje.

---

## 1. ČO JE HOTOVÉ

### Obsah a kontaktné údaje
- **E-mail `ivankubis96@centrum.sk`** je doplnený všade: v pätičke v oboch
  jazykoch, na kontaktnej stránke ako klikateľný `mailto:`, v dokumente o
  ochrane osobných údajov ako kontakt na prevádzkovateľa, v štruktúrovaných
  údajoch pre Google (JSON-LD, `AutoRepair → email`) a v podkladoch pre
  asistenta. Veta „E-mailová adresa zatiaľ nie je doplnená" je preč.
- **Žiadne zástupné texty.** Na stránke nezostal ani jeden hranatý token:
  odstránené sú oba odseky „na doplnenie" na stránke O servise, všetkých sedem
  panelov „[TO CONFIRM]" na stránkach služieb a odkazy na Facebook a Instagram,
  ktoré nikam neviedli. Okolitý text je prepísaný tak, aby odseky dávali zmysel
  aj bez nich — vrátane úvodov na stránkach Služby a O servise, z ktorých zmizli
  vety o tom, čo je a nie je potvrdené.
- **Dokument o ochrane osobných údajov** má po novom napísanú dobu uchovávania
  (správy z formulára 12 mesiacov od vybavenia dopytu, kontaktné údaje do
  vybavenia, najviac 12 mesiacov) a úplný výpočet práv dotknutej osoby podľa
  článkov 15 až 22 GDPR vrátane práva podať sťažnosť Úradu na ochranu osobných
  údajov SR. **Upozornenie, že dokument neprešiel právnou kontrolou, zostalo** —
  je hneď na začiatku, nie v poznámke pod čiarou.
- Pribudol odsek o fotografiách majiteľov a o tom, že sú zverejnené s ich
  súhlasom, a odsek o tom, čo presne sa zaznamenáva pri práci s asistentom.

### Partner Castrol Service
- Na úvodnej stránke je sekcia o zmluvnej spolupráci s Castrol Service: nadpis,
  podnadpis, odsek o tom, že pri výmene motorového oleja sa používajú oleje
  Castrol a že sa vyberá podľa požiadaviek výrobcu, a štyri body dôvery.
- Sekcia je typografická — **nereprodukuje žiadnu grafiku Castrolu**, netvrdí
  certifikáciu ani autorizáciu a nenaznačuje, že by jedna špecifikácia oleja
  sedela na každé vozidlo.
- Asistent o spolupráci vie: na otázku „aký olej používate" odpovie z tohto
  textu a odkáže na úvodnú stránku, v slovenčine aj v angličtine.

### Majitelia
- Sekcia **Majitelia** na stránke O servise: dve štvorcové portrétové
  fotografie vedľa seba, na mobile pod sebou, rovnaké orámovanie a rovnaký
  polomer rohov. **Mená sa pod fotografie nepíšu** — každá fotografia má
  vlastnú menovku priamo v obrázku.
- Údaje sú v konfigurácii (`config/miauto.ts`, pole `owners`), komponent funguje
  pre jedného aj pre dvoch. Ak by niekto chýbal alebo nemal fotku, sekcia sa
  nevykreslí vôbec — nevznikne prázdny rámček.
- Fotografie prešli rovnakým spracovaním ako zvyšok webu: odstránené metadáta,
  orez na 4:5, tri veľkosti v troch formátoch (AVIF, WebP, JPEG), farebný
  medzistav počas načítania. **Žiadna fotografia nebola umelo zväčšená.**
- Popisy pre čítačky obrazovky sú vecné: „Marián Hrnčiar — Spolumajiteľ servisu,
  M.I.Auto s.r.o." a to isté pre Ivana Kubisa. Menovka je v obrázku, kam sa
  čítačka nedostane, preto je meno zopakované v popise.

### Skúsenosti a vzdelanie majiteľov
- Na stránke O servise je samostatná sekcia „Skúsenosti, odbornosť a poctivá
  práca" s podnadpisom, odsekom a tromi bodmi: viac ako 10 rokov skúseností,
  odborné technické vzdelanie a dôraz na kvalitu.
- Text je presne ten, ktorý ste dodali. **Nedopĺňali sme** názov školy, rok
  ukončenia, ocenenia, certifikáty výrobcov ani životopis jednotlivých
  majiteľov — nič z toho podklady neurčujú.
- V podkladoch pre asistenta je k tomu veta, že uvedené roky sú skúsenosti
  majiteľov, nie dĺžka pôsobenia firmy, aby si to asistent nespojil.

### Značka
- **Logo je vaše vlastné** — kruhový emblém s monogramom „Mi" a profilom auta.
  Dodaná predloha bola rastrový obrázok; obrysy sme obkreslili do vektora, takže
  je ostrý v akejkoľvek veľkosti, preberá farbu textu a nestojí ani jeden
  obrázkový request navyše.
- Z jednej predlohy vychádza všetko: značka v hlavičke a v pätičke, favicon
  (SVG aj PNG 180×180 pre iOS), ikony pre manifest a obrázok pre zdieľanie na
  sociálnych sieťach (1200×630, zvlášť pre slovenskú a anglickú verziu).
- Logo je vložené priamo do stránky ako SVG, nie ako obrázok. Hlavička stále
  oznamuje čítačkám „M.I.Auto s.r.o.".
- Vo favicone je prsteň vynechaný: pri 16 px tenká kružnica zanikne, preto je
  tam ten istý znak ako plná oranžová plôška s vyrezaným monogramom.

### Diagnostická animácia na úvodnej stránke
Prekreslená od základu. Jeden zdroj svetla vľavo hore, podľa ktorého je
nasvietená celá scéna; každý povrch má základ, prechod a odlesk; tri hrúbky
čiar pre tri úlohy. Konkrétne:
- prístrojový panel s dvoma budíkmi, ktoré majú skutočnú stupnicu — hlavné a
  vedľajšie rysky, číslice, červené pásmo len na otáčkomeri — ručičky s hrotom a
  protizávažím, krytku náboja a digitálne okienko medzi budíkmi;
- diagnostický prístroj s telom, displejom, tlačidlami a LED, kábel kreslený ako
  plocha s premenlivou šírkou a miernym previsom, nie ako čiara;
- zoznam chybových kódov vysádzaný ako na displeji prístroja, so skutočnými
  formátmi kódov a nadpisom, ktorý hovorí, že ide o ukážku;
- schéma okruhu so štyrmi pomenovanými bodmi a s poruchou, ktorú vidno nájsť aj
  opraviť;
- pohyb pruží a dobieha, ručičky mierne prekmitnú a ustália sa.
- **Pri zapnutom „obmedziť pohyb" v systéme sa nehýbe nič** — ani svetlo, ani
  zrno. Scéna sa prepne do koncového stavu okamžite.
- Päť popisov etáp je prepísaných: každý jednou vetou hovorí, čo sa deje a prečo
  na tom záleží, nie čo je na obrázku vidieť.

### Sedem interaktívnych prvkov, jeden na každú službu
Všetky stoja na jednom spoločnom základe (posuvník alebo tlačidlá, scéna,
výstupné hodnoty, upozornenie s telefónnym číslom). Všetky čísla sú v
`config/widgets.ts`, žiadne nie je v komponente.

| Služba | Prvok |
|---|---|
| Diagnostika | od symptómu k príčine — lievik možných príčin, ktorý sa meraním zužuje na jednu |
| Čipovanie ECU | valcová skúšobňa a krivky výkonu a momentu |
| Geometria kolies | pohľad spredu (odklon), pohľad zhora (zbiehavosť) a rez pneumatikou |
| Pneuservis | hĺbka dezénu proti brzdnej dráhe na mokrom |
| Elektroinštalácia | hľadanie prerušenia meraním napätia v štyroch bodoch |
| Výmena rozvodov | opotrebenie remeňa a scenár pretrhnutia |
| Servis klimatizácie | náplň chladiva proti teplote z výduchu |

Poctivosť čísel:
- Výkon sa **počíta** z krútiaceho momentu vzťahom P = M × n / 9549, takže obe
  krivky vždy sedia jedna s druhou. Ide o typický motor 2.0 TDI, nie o konkrétne
  vozidlo, a widget to pod sebou hovorí. **Nikde nie je prísľub prírastku.**
- Brzdné dráhy sú orientačné hodnoty z verejne publikovaných testov brzdenia na
  mokrom, nie meranie. Je to napísané pod widgetom.
- Interval výmeny rozvodov je označený ako **ilustračný**; text hovorí, že
  skutočný predpisuje výrobca pre konkrétny motor.
- Uhly v geometrii sú na obrázku zväčšené, aby boli viditeľné — a priamo v
  obrázku je napísané, že sú.

Technicky: každý widget je samostatný balík, ktorý sa sťahuje až keď sa sekcia
blíži k obrazovke, takže nespomaľuje vykreslenie stránky. Posuvníky sú skutočné
`<input type="range">`, takže klávesnica a čítačky fungujú bez obchádzok.

### Asistent
- Systémový prompt je prepísaný podľa zadania: hovorí, že nie je človek;
  odpovedá v jazyku stránky; drží sa rozsahu servisu; **nesľubuje cenu ani
  termín**; nediagnostikuje na diaľku; nevymýšľa vybavenie ani zoznamy motorov;
  pri čipovaní **negarantuje výkon a neposkytuje nič o odstránení DPF, EGR ani
  AdBlue**; pri podozrení na problém s bezpečnosťou odporučí nejazdiť a zavolať;
  nezbiera osobné údaje.
- Kľúč sa číta z premennej `ANTHROPIC_API_KEY` **len na serveri**. Nie je to
  `NEXT_PUBLIC_` premenná, nedostane sa do prehliadača ani do repozitára.
- Odpoveď prichádza po častiach (streaming), panel má stav „píše", vlastný
  časový limit a ošetrenú chybu.
- **Keď model nie je dostupný, widget to povie.** Pod odpoveďou sa objaví veta
  „Teraz viem odpovedať len na základné otázky. Na čokoľvek ďalšie zavolajte na
  +421 918 918 109." s číslom ako odkazom. Nikdy sa netvári, že odpovedal, keď
  spadol.
- Panel sa ovláda klávesnicou, fokus v ňom zostáva, Escape ho zavrie a vráti
  fokus na tlačidlo. V hlavičke panela je napísané, že nejde o človeka.
- Podklady sa generujú z toho istého obsahu, z akého sa vykresľujú stránky
  (7 služieb, adresa, hodiny, telefón, e-mail, otázky a odpovede, postup pri
  dopyte) — nemôžu sa teda rozísť s tým, čo je na webe.

### Technika
- **Obsahová bezpečnostná politika (CSP)** a **Permissions-Policy** na oboch
  spôsoboch nasadenia. Nenačíta sa žiadny skript, štýl, rámec ani spojenie mimo
  vlastnej domény a mapy Google.
- **Vlastná stránka 404** v oboch jazykoch, so správnym stavovým kódom, pre
  serverové aj statické nasadenie.
- Otváracie hodiny sú overené cez polnoc, cez víkend aj cez časové pásma —
  počítajú sa podľa hodín v Ružomberku bez ohľadu na to, odkiaľ sa návštevník
  pozerá.
- Formulár je otestovaný na všetkých troch koncoch: odoslanie cez Netlify
  (úspech), hostiteľ, ktorý vráti registračnú stránku (chyba, nie falošný
  úspech), a odmietnutý POST (chyba). Prázdny formulár sa odoslať nedá a pod
  tlačidlom je napísané prečo.
- Na mobile s 4× spomaleným procesorom: posun rozloženia (CLS) 0 až 0,004 pri
  limite 0,1; JavaScript 174–191 kB; všetkých 24 stránok sa vykreslí bez chyby v
  konzole a bez vodorovného posúvania.
- Prístupnosť: všetko interaktívne sa dá ovládať klávesnicou, fokus je viditeľný
  (3 px oranžový rám), kontrast nad úrovňou AA.

### Pohyb

Celý web používa jednu sústavu pohybu — jednu krivku zrýchlenia a tri dĺžky
trvania. Nič sa nehýbe náhodne a nič si neťahá vlastnú knižnicu; animácie sú
čisté CSS a SVG, plus asi sto riadkov vlastného JavaScriptu.

- **Tlačidlá.** Pod myšou sa zdvihnú o pixel a zväčšia o 1,2 % a dostanú tichý
  tieň; pri stlačení sa stlačia na 97,5 %. Stlačenie je zámerne rýchle (110 ms) a
  návrat pomalší (260 ms) — tak sa správa fyzické tlačidlo.
- **Fotografie odpovedajú kurzoru.** Hero na úvodnej stránke, veľká fotografia na
  stránke služby a fotografia interiéru na stránke O servise sa za kurzorom
  pohnú o pár pixelov a naklonia o zlomok stupňa. Je to zámerne málo: ide o to,
  aby obrázok pôsobil, že je v stránke, nie na nej.
- **Vypne sa to samo, keď nemá zmysel.** Na dotykovom displeji sa efekt
  nenaštartuje vôbec a fotografia sa ani nezväčší — nie je dôvod orezať záber
  kvôli pohybu, ktorý sa nikdy nespustí. Pri systémovom nastavení „obmedziť
  pohyb" (`prefers-reduced-motion`) stojí všetko úplne.
- **Nestojí to výkon.** Pohyb kurzoru si len poznačí cieľ; zapisuje jediná
  slučka, ktorá sa po návrate do pokoja sama zastaví a uvoľní grafickú pamäť.
  Nemeria sa pri tom rozloženie stránky a nemení sa žiadna vlastnosť, ktorá by
  rozloženie prepočítala.

---

## 2. ČO BLOKUJE NASADENIE

### 🔴 IČO A ZÁPIS V OBCHODNOM REGISTRI

**NA WEBE SPOLOČNOSTI MUSÍ BYŤ UVEDENÉ IČO A ÚDAJ O ZÁPISE V OBCHODNOM
REGISTRI — OZNAČENIE REGISTROVÉHO SÚDU, ČÍSLO VLOŽKY A ODDIEL. VYŽADUJE TO § 3a
OBCHODNÉHO ZÁKONNÍKA. BEZ NICH SA STRÁNKA NESMIE SPUSTIŤ.**

Nevymýšľali sme ich. V `config/miauto.ts` sú pripravené prázdne polia:

```
ico:       ""   ← IČO
zapisVOR:  ""   ← napr. „Obchodný register Okresného súdu Žilina, oddiel: Sro, vložka č. ..."
dic:       ""   ← DIČ (nepovinné)
icDph:     ""   ← IČ DPH (len ak je spoločnosť platiteľom DPH)
```

Stačí ich vyplniť a uložiť. Riadok sa objaví sám — v pätičke, v dokumente o
ochrane osobných údajov aj v štruktúrovaných údajoch. Kým je pole prázdne,
nevykreslí sa ani jeho popis, takže na stránke nie je vidieť, že niečo chýba —
ale chýba to.

### 🔴 Súhlas oboch majiteľov so zverejnením fotografie

Na stránke O servise sú portréty Mariána Hrnčiara a Ivana Kubisa. Pred spustením
**potrebujeme od oboch súhlas so zverejnením** — stačí e-mailom alebo písomne.
Dokument o ochrane osobných údajov už obsahuje odsek, ktorý hovorí, že fotografie
sú zverejnené so súhlasom a že ho možno kedykoľvek odvolať.

### 🟠 Adresa webu pred zostavením

`NEXT_PUBLIC_SITE_URL` sa zapečie do stránok **v okamihu zostavenia**. Treba ju
nastaviť na finálnu doménu (napr. `https://miauto.sk`) a až potom spustiť build.

Priložený balík `deploy/miauto-netlify-drag-and-drop.zip` je zostavený bez nej,
lebo doménu zatiaľ nepoznáme. **Nasadiť sa dá tak, ako je** — stránka funguje a
vyhľadávače ju zaindexujú na tej adrese, na ktorej ju nájdu. Chýbajú len veci,
ktoré musia byť absolútnou adresou, a tie sa radšej nevypíšu, než aby ukazovali
na `localhost`: kanonický odkaz, hreflang, mapa stránok a riadky `Host` a
`Sitemap` v `robots.txt`. Build na to upozorní na konci výpisu.

Keď doménu poviete, balík prerobím za minútu a všetko sa objaví:

```
NEXT_PUBLIC_SITE_URL=https://www.miauto.sk npm run build:static
```

Pri nasadení cez Git to netreba riešiť zvlášť — Netlify si vlastnú adresu
nastaví sám a stránka ju použije; premenná ju len prepíše na tú finálnu.

Jediné, čo v balíku bez domény zostáva neúplné, je obrázok pre náhľad
zdieľaného odkazu (`og:image`) — ten musí byť absolútny a Next ho vyrába sám, s
adresou `localhost`. Pri zdieľaní odkazu sa teda zobrazí názov a popis, ale bez
obrázka. Zostavenie s doménou to spraví správne.

### 🟠 Právna kontrola dokumentu o ochrane osobných údajov

Dokument je napísaný vecne a podľa GDPR, **ale nie je to právne stanovisko a
netvrdíme, že je v súlade s GDPR.** Na stránke je to napísané. Pred spustením by
ho mal prejsť niekto s právnym vzdelaním.

### 🟠 Asistent beží len pri nasadení cez Git alebo CLI

Grounded asistent potrebuje serverovú funkciu. **Nasadenie potiahnutím
priečinka do Netlify žiadny build ani funkcie nespúšťa**, takže tam asistent
spadne na pevné odpovede. Ak má odpovedať naozaj:

1. pripojte repozitár v Netlify (Add new site → Import an existing project), alebo
2. nasaďte cez `netlify deploy` z príkazového riadka,

a nastavte `ANTHROPIC_API_KEY` v premenných prostredia. Bez kľúča je stránka plne
funkčná, len asistent odpovedá z pripravených odpovedí a sám to hovorí.

---

## 3. ČO BY WEB ZLEPŠILO

### Fotografie
- **Šesť zo siedmich fotografií k službám sú ilustračné**, nie z vašej dielne:
  diagnostika, čipovanie ECU, geometria, pneuservis, elektroinštalácia a
  rozvody. Vlastné sú klimatizácia, tri fotografie na stránke O servise a oba
  portréty.
  Popisy pri ilustračných fotografiách opisujú činnosť a nikde netvrdia, že ide
  o vaše priestory. Vlastné fotografie by boli priamočiare zlepšenie — stačí ich
  poslať a prejdú rovnakým spracovaním.
- **Logo je pri 16 px nečitateľné v detaile.** Kresba má tenký prsteň a jemné
  ťahy; vo favicone sme to riešili plnou plôškou s vyrezaným monogramom, ale na
  karte prehliadača z neho zostane oranžový krúžok. Je to vlastnosť predlohy,
  nie chyba — ak raz vznikne zjednodušená verzia znaku pre malé veľkosti,
  nahradí sa jedným súborom.
- **Menovky v portrétoch sú po anglicky.** Na fotografiách je „co-owner";
  slovenská stránka by privítala „spolumajiteľ". Fotografie sme neupravovali —
  stačí poslať znovu vyexportované verzie s rovnakým rozložením a nahradia sa
  jedna k jednej. (Pre čítačky obrazovky je rola po slovensky už teraz.)
- **Novú hero fotografiu vedieme ako ilustračnú — a radi to zmeníme.** Záber,
  ktorý ste poslali, je na úvodnej stránke presne tak, ako prišiel. Nevieme však
  doložiť, že je z vašej dielne: na ostatných vlastných fotografiách je iný
  priestor a na stene je iné logo. Preto má v `public/assets/miauto/manifest.json`
  príznak `origin: "stock"` a popis pre čítačky obrazovky hovorí o činnosti
  („vozidlo na dvojstĺpovom zdviháku, mechanik pracuje na prednom kolese"), nie o
  vašich priestoroch. **Ak je to vaša dielňa, napíšte jedno slovo** — v
  `scripts/process-images.py` sa prepíše `ORIGIN["hero"]` na `"own"`, popis sa
  zmení na vetu o vlastnej dielni a je to. Opačne to nejde: tvrdiť o cudzom
  priestore, že je váš, je klamlivé označenie.

### Údaje
- **GPS súradnice prevádzky.** Mapa teraz funguje z adresy a Google ju nájde
  správne, ale do štruktúrovaných údajov (`geo`) patria presné súradnice — Google
  si potom miesto spáruje istejšie. V konfigurácii je pole `geo`, prázdne.
- **Facebook a Instagram**, ak existujú. Dnes sa odkazy nevykresľujú vôbec.
- **Sviatky stránka nepozná.** Otváracie hodiny sú pondelok až piatok 7:00–17:00
  s obedňajšou prestávkou 12:00–13:00, víkend zatvorené. O sviatkoch stránka
  zámerne nič netvrdí — žiadne údaje o nich nemá.

### Rozšírenia
- **Oznámenie o dopyte e-mailom.** Po prvom nasadení sa formulár objaví v Netlify
  pod **Forms → dopyt**; tam treba doplniť adresu `ivankubis96@centrum.sk`, inak
  dopyty ležia v administrácii a nikto o nich nevie. Je to nastavenie v Netlify,
  nie v kóde.
- **Lacnejší model pre asistenta.** Predvolený je najschopnejší; premennou
  `CHAT_MODEL` sa dá prepnúť na lacnejší (`claude-haiku-5-5`) za cenu menej
  presných formulácií. Denný strop spotreby je nastavený a dá sa zmeniť.
- **Referencie zákazníkov.** Žiadne sme nevymýšľali. Keď budú skutočné, je to
  najsilnejší obsah, ktorý na stránke chýba.

---

## 4. KROKY NASADENIA

### A. Pred zostavením
1. Doplniť **IČO** a **zápis v obchodnom registri** do `config/miauto.ts`
   (prípadne DIČ a IČ DPH).
2. Získať **súhlas oboch majiteľov** so zverejnením fotografie.
3. Dať dokument o ochrane osobných údajov **skontrolovať právnikovi**.
4. Ak už je známa **doména**, nastaviť ju ako `NEXT_PUBLIC_SITE_URL` a zostaviť
   znova. Nie je to podmienka spustenia — bez nej stránka funguje a indexuje sa
   — ale s ňou dostanú vyhľadávače kanonické odkazy, hreflang aj mapu stránok.

### B. Nasadenie cez Git (odporúčané — asistent funguje)
1. Netlify → **Add new site → Import an existing project**, vybrať repozitár.
   Nastavenia prídu z `netlify.toml` (základný priečinok `miauto`, príkaz
   `npm run build`).
2. **Site configuration → Environment variables** nastaviť:
   - `NEXT_PUBLIC_SITE_URL` = finálna adresa (napr. `https://miauto.sk`)
   - `ANTHROPIC_API_KEY` = kľúč k modelu (nepovinné; bez neho asistent odpovedá
     z pripravených odpovedí)
3. Spustiť nasadenie.
4. **Forms → dopyt → Settings → Form notifications**: pridať e-mailové
   oznámenie na `ivankubis96@centrum.sk`.
5. **Domain management**: pridať doménu, nasmerovať DNS (buď štyri nameservery
   Netlify, alebo `ALIAS`/`A` záznam pre doménu a `CNAME` pre `www`), počkať na
   certifikát a zapnúť **Force HTTPS**.
6. Keď je doména aktívna, upraviť `NEXT_PUBLIC_SITE_URL` na ňu a **nasadiť
   znova** — adresa sa zapeká pri zostavení.

### C. Nasadenie potiahnutím priečinka (bez asistenta)
1. `cd miauto && npm install && npm run build:static`
2. Do Netlify potiahnuť **obsah priečinka `out/`** (alebo priložený zip
   `deploy/miauto-netlify-drag-and-drop.zip`).
3. Kroky 4 a 5 z časti B platia rovnako. Asistent beží v režime pripravených
   odpovedí a hovorí to.

### D. Po nasadení skontrolovať
- Formulár: odoslať skúšobný dopyt a overiť, že prišiel e-mail.
- Telefónne číslo na mobile: ťuknutie musí otvoriť vytáčanie.
- Mapa na kontaktnej stránke a tlačidlo navigácie.
- Obe jazykové verzie a prepínač medzi nimi.
- Zdieľanie odkazu (Messenger, WhatsApp) — má sa zobraziť obrázok s logom.

---

*Dokument zodpovedá stavu vetvy `claude/miauto-website-build-7e1gr6`.*
