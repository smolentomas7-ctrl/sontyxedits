---
name: miauto-web
description: "Prepares production prompts for Claude Code for the M.I.Auto s.r.o. website (Ružomberok, Slovakia) and for new website briefs. Holds the project facts, hard rules, architecture, deploy paths (Netlify, HostCreators) and the creative interview. Use when asked to plan, prompt or brief any change to this website or to a new one."
---

# MASTER PROMPT — miauto-web

## 0. Úloha tohto skillu

Tento skill **pripravuje výrobné prompty pre Claude Code**. Nekóduje sám, pokiaľ o to
nejde explicitne. Výstup je jeden hotový prompt v tvare z časti 9, ktorý Claude Code
dostane a vie podľa neho pracovať bez ďalších otázok.

- **M.I.Auto** (`miauto/` v tomto repozitári) je predvolený režim. Web je už navrhnutý;
  prompt vychádza z faktov a pravidiel nižšie.
- **Nový web pre iného klienta**: najprv creative interview (časť 10), jeho výsledný brief
  je vstup pre prompt. Bez schválenia nič negenerovať.

Komunikácia s klientom: **slovensky**. Kód, komentáre, commity a prompty pre Claude Code:
**anglicky**. Texty na webe: sk + en.

## 1. Tvrdé pravidlá (nikdy neporušiť)

- **Žiadne vymyslené údaje.** IČO, DIČ, zápis v OR, GPS, ceny, recenzie, hodnotenia,
  otváracie hodiny, certifikáty, školy, ocenenia, zoznamy motorov, vybavenie dielne,
  počty zákazníkov, referencie. Chýbajúce údaje zostanú chýbať; polia sa renderujú až
  po vyplnení.
- **Žiadne placeholdery**: lorem ipsum, „coming soon", sivé boxy namiesto fotiek, `[TBD]`.
  Bez materiálu sa blok nevykreslí.
- **Každý slovenský reťazec má úplný anglický preklad** (`content/sk.ts`, `content/en.ts`).
- **Prístupnosť**: klávesnica, viditeľný focus, správne ARIA, `prefers-reduced-motion`,
  kontrast min. WCAG AA.
- **Žiadne ťažké knižnice.** Animácie = CSS transform/opacity + SVG + malý vlastný JS.
- **Žiadne zavádzajúce tvrdenia.** Pri čipovaní nesľubovať výkon. **Nikdy nenavrhovať
  odstránenie DPF, EGR ani AdBlue** (nelegálne v EÚ).
- **Nepísať, že privacy dokument spĺňa GDPR.** Vyžaduje právnu kontrolu.
- **`ANTHROPIC_API_KEY` iba na serveri.** Nikdy `NEXT_PUBLIC_`, nikdy v klientovi, v repozitári ani v prompte.
- **Originálne fotky sa neupravujú na mieste** (`assets-originals/`, gitignored). Nikdy neupscalovať.
- **Stock fotka sa nikdy nepopisuje ako priestory klienta.** `origin: "own" | "stock"`
  v manifeste; alt text opisuje činnosť, nie priestory, pokiaľ nie je potvrdené, že ide o ich dielňu.
- **Žiadne falošné profily, recenzie ani impersonácia.**
- **DNS, doména, SSL** sa nemenia, pokiaľ klient výslovne nepožiada.
- **Nehlásiť „opravené" ani „live", kým to nie je overené** na vybuildovanom výstupe
  (a na živej doméne, ak sa dá). Čo sa nedá overiť, povedať výslovne a povedať ako.

## 2. Fakty o M.I.Auto (len tieto)

| Položka | Hodnota |
|---|---|
| Názov | M.I.Auto s.r.o. (krátko M.I.Auto) — nezávislý autoservis |
| Adresa | Sládkovičova 2528/108, 034 01 Ružomberok, Žilinský kraj |
| Telefón | +421 918 918 109 (hlavné CTA všade) |
| Zverejnený e-mail | ivankubis96@centrum.sk |
| Príjemca dopytov | ivanautoservisrk@gmail.com (`site.formRecipient`) |
| Majitelia | Marián Hrnčiar, Ivan Kubis (spolumajiteľ). Portréty sú, súhlas chýba |
| Partner | Castrol Service |
| Otváracie hodiny | Po–Pi 07:00–17:00, obedňajšia prestávka 12:00–13:00 každý pracovný deň; so–ne zatvorené |
| Služby | diagnostika vozidiel, čipovanie ECU, geometria kolies, pneuservis, elektroinštalácia VW koncernu, výmena rozvodov (2.0 TDI, 3.0 TDI), servis klimatizácie |
| Jazyky | sk (`/sk`, predvolený), en (`/en`) |
| Kanonická doména | `https://autoservisruzomberok.com` (`PRODUCTION_URL` v `config/miauto.ts`) |
| Druhá doména | autoservisruzomberoksro.sk (HostCreators) — rozhodnutie čaká na klienta |

Mesto spomenúť prirodzene, raz v titulku a raz v popise. Žiadne keyword stuffing.

**Blokery spustenia (klient, nie kód):** IČO a zápis v OR (§ 3a Obchodného zákonníka);
súhlas oboch majiteľov s fotkami; právna kontrola privacy dokumentu; výber jednej domény
a presmerovanie druhej; reálna schránka na doméne pre `MAIL_FROM`; Google Search Console
(doména + sitemap).

**Fotky:** vlastné `about-01..03`, `diagnostika`, `klimatizacia`, `owner-01/02`.
Stock/ilustračné: `hero` (dodaný záber, `stock`, kým klient nepotvrdí, že je to jeho dielňa)
a fotky ECU, geometrie, pneu, elektro, rozvodov.

## 3. Architektúra a príkazy

- Next.js 16 (App Router), React 19, TypeScript 5.9 strict + `noUncheckedIndexedAccess`,
  Tailwind 4 cez `@tailwindcss/postcss`. Projekt: `miauto/`. Git root obsahuje nesúvisiaci
  web Sontyx — nikdy ho nemeniť ani nenasadzovať.
- Branch: **`claude/miauto-website-build-7e1gr6`**, nikam inam.
- Routy: `app/[locale]/…`, 12 na jazyk, 24 stránok. `<html lang>` z layoutu v `[locale]`.
- Obsah: `content/sk.ts`, `content/en.ts`, typy `content/types.ts`. Kontakt a značka:
  `config/miauto.ts`. Obrázky: `config/images.ts`.
- Helpery: `lib/i18n.ts` (`ROUTES`, `pageUrl`, `canonicalFor`, `pageSeo`),
  `lib/motion.ts` (`useReveal`, `useParallax`, press, reduced-motion), `lib/forms.ts`,
  `lib/jsonld.ts`, `lib/hours.ts`.
- Komponenty: `components/home`, `about`, `ui`, `widgets` (7 interaktívnych widgetov vrátane
  dyno a pneumatík), `contact`, `chat`, `brand`.

| Príkaz | Účel |
|---|---|
| `npm run typecheck` | `tsc --noEmit`, musí prejsť pred pushom |
| `npm run build` | server build |
| `npm run build:static` | export do `out/` pre Netlify drag-and-drop; spúšťa canonical guard |
| `npm run build:hostcreators` | balík pre Apache → `../hostcreators-deploy/` + `../hostcreators-deploy.zip` |
| `npm run images` | `scripts/process-images.py` (Python + Pillow) |
| `npm run evals` | chat evaluácie |

`npm run lint` neexistuje (Next 16 bez `next lint`, bez ESLint konfigurácie). Použiť `typecheck`.

**Dizajnové tokeny (nemeniť):** `--bg #0b0d0e`, `--surface #14181a`, `--surface-hover #1c2124`,
`--border #262d31`, `--text #f2f4f5`, `--text-muted #94a1a8`, `--accent #ff7a3d`,
`--accent-hover #ff9158`, `--focus #ff9158`, `--danger #f87171`, `--success #4ade80`.
Pohyb: `--ease-ios cubic-bezier(.32,.72,0,1)`, `--dur-press 110ms`, `--dur-release 260ms`,
`--dur-reveal 420ms`, `--dur-state 180ms`.

**Tailwind 4 pasce:** `text-[var(--x)]` je font-size → píš `text-[color:var(--x)]`;
arbitrárny `object-position` cez CSS premennú; nevrstvený CSS prebíja vrstvy → základ v `@layer base`.

**Pohyb (existuje, rozširovať, nenahrádzať):** `.tappable` (tlačidlá 0.975, karty 0.985),
`.tappable--lift` iba na tlačidlách pri jemnom pointeri, `.reveal`/`.reveal-image`,
parallax cez `useParallax` + `components/ui/Parallax.tsx`: jeden rAF, dve CSS premenné,
sleduje **statický obal alebo `[data-parallax-area]`, nikdy pohybujúcu sa vrstvu**; len
`(hover:hover) and (pointer:fine)`, vypnutý pri reduced motion. Na hero, veľkú fotku služby
a interiér O servise, nie na karty. Globálny reduced-motion kill switch zachovať.

**Dyno:** `P[kW] = M[Nm] × n[rpm] / 9549`; definovaný je len krútiaci moment.

## 4. Obrázky

`scripts/process-images.py`: z `assets-originals/` strip EXIF → precrop → redakcia → crop na
pomer slotu → resize; full/card/thumb × webp/avif/jpg; rozpočty 200/80/40 KB; zapisuje
`public/assets/miauto/manifest.json` (width, height, placeholder, origin, upscaled).
**Next image optimizer cachuje podľa názvu súboru** — po výmene fotky pod rovnakým
názvom vymazať `.next/cache/images`.

## 5. Formulár, chat, súkromie

**Formulár** má dva režimy podľa `NEXT_PUBLIC_FORM_ENDPOINT`:
- **Netlify** (predvolené): POST na `/__forms.html`. Netlify posiela e-mail až po
  notifikácii nastavenej v dashboarde (Forms → `dopyt` → Settings → Form notifications).
  Súbor musí obsahovať sentinel `MIAUTO_FORM_REGISTRATION_PAGE` (`lib/forms.ts` ním
  rozlišuje neúspech).
- **HostCreators / Apache**: POST na `/contact.php`. Server validuje, odmieta header
  injection, throttluje per IP (čas sa zapíše až po úspešnom `mail()`), odpovedá JSON.
  `MAIL_FROM` musí byť schránka na doméne webu; Gmail tam = tiché zahodenie.

Front-end: úspech iba ak server potvrdí `{"ok":true}`; 200 s `ok:false` = chyba; zámok proti
dvojitému odoslaniu; honeypot `bot-field` nie `display:none`; min. 3 s na vyplnenie; údaje
ostávajú po chybe.

**Chat:** grounded režim potrebuje `app/api/chat` a `ANTHROPIC_API_KEY` na serveri. Statický
hosting beží na skriptovanej úrovni v prehliadači — povedať to klientovi.

**Privacy:** zbierané údaje, právny základ (oprávnený záujem na odpovedi), Netlify ako
sprostredkovateľ, Google (Gmail) ako ďalší pri preposielaní e-mailu, 12 mesiacov retencia,
prístup len majitelia. Bez tvrdenia o GDPR.

## 6. SEO

- Každá stránka **self-canonical**, absolútna, cez `pageUrl(locale, route)`; presne jeden tag.
  SK nikdy na EN ani naopak; nikdy na domovskú stránku.
- `/` → 301 na `/sk/` (Netlify `_redirects`, na Apache `.htaccess`). Na holý koreň z webu
  neodkazovať.
- hreflang `sk`, `en`, `x-default` (= SK) v `<head>`, nie cez JS.
- Sitemap: `app/sitemap.xml/route.ts`, ručne písaný XML, presne 24 `<url><loc>`, namespace
  sitemaps.org. Bez `lastmod`, `changefreq`, `priority`, bez hreflang (je v HTML). Nikdy
  presmerovania, preview URL ani localhost.
- robots.txt: `Allow: /`, `Host:`, `Sitemap: https://<doména>/sitemap.xml`. `Disallow:
  /__forms.html` len v Netlify builde.
- `noindex` iba na 404 stránkach a na formulárovom stube.
- Štruktúrované dáta `AutoRepair`: názov, adresa, telefón, e-mail, hodiny (rozdelené okolo
  prestávky), mapa, majitelia. Bez hodnotení, recenzií, ceny, súradníc, pokiaľ klient neposkytne.
- OG: `og:url` = kanonická. Metadáta cez `pageSeo()`.
- `scripts/check-canonicals.mjs` na konci statického buildu zhodí build, ak chýba alebo je
  zlý kanonický odkaz. Zachovať.

## 7. Nasadenie

**Netlify drag-and-drop:** `cd miauto && npm run build:static`; obsah `out/` (alebo
`deploy/miauto-netlify-drag-and-drop.zip`) potiahnuť do Netlify Deploys — **obsah**, nie priečinok.
Žiadne funkcie, chat na skriptovanej úrovni.

**HostCreators (Apache, WebFTP):**
1. `cd miauto && npm run build:hostcreators` — build s doménou, `NEXT_PUBLIC_TRAILING_SLASH=1`,
   `NEXT_PUBLIC_FORM_ENDPOINT=/contact.php`; odstráni Netlify súbory, pridá `.htaccess`,
   `contact.php`, root `index.html`, skontroluje balík a zapíše zip s `index.html` v koreni.
2. Nahrať **obsah** `hostcreators-deploy/` do web rootu (`public_html`/`www`/`web`).
   Starý testovací `index.html` („Test") zmazať.
3. Zapnúť vo WebFTP **zobrazovanie skrytých súborov** — `.htaccess` je bodkový súbor.
4. Overiť: `https://<doména>/` → presmerovanie na `/sk/`.
5. Potvrdiť u hostingu `mod_rewrite`, `mod_headers` a PHP.

Príčina 403: v koreni chýbal `index.html` (presmerovanie v `_redirects`, ktorý Apache ignoruje)
a stránky boli adresáre bez indexu. Opravené trailing-slash exportom + `.htaccess`.

**Overenie bez prístupu na živý server:** obsluhovať výstup serverom, ktorý sa správa ako
Apache (DirectoryIndex, 403 na adresár bez indexu, mod_dir redirect), prejsť headless
prehliadačom od `/` po odkazoch; kontrola: status 200, jeden `h1`, jeden kanonický odkaz,
nulové chyby požiadaviek. Nahlásiť ako simuláciu, nie živé overenie.

## 8. Checklist pred odovzdaním

- [ ] `npm run typecheck` prejde
- [ ] `build:static` / `build:hostcreators` prejde vrátane canonical guardu
- [ ] 24 stránok: jeden `h1`, jeden kanonický, tri hreflang
- [ ] sitemap: platné XML, 24 URL, všetky 200, žiadne presmerovanie
- [ ] robots.txt ukazuje na správnu sitemap; žiadny noindex na indexovaných stránkach
- [ ] v výstupe žiadny localhost, netlify.app ani dev odkaz
- [ ] koreň → `/sk/`
- [ ] formulár: validácia, zámok, úspech len pri potvrdení servera
- [ ] pohyb: parallax len pri jemnom pointeri, press, reduced motion
- [ ] šírka 390 px: žiadne horizontálne posúvanie, ciele dotyku ≥ 44 px
- [ ] konzola bez chýb
- [ ] commit a push na `claude/miauto-website-build-7e1gr6`
- [ ] report v slovenčine: čo sa zmenilo, čo overené, čo nie a prečo, presné kroky nasadenia

## 9. Formát výrobného promptu pre Claude Code

Každý prompt, ktorý tento skill pripraví, má tieto sekcie v tomto poradí:

1. **Goal**: výsledok v 1–2 vetách.
2. **Context**: len relevantné fakty z časti 2 a stav z `SPRAVA.md`.
3. **Scope**: smú sa meniť tieto súbory; tieto sa nesmú.
4. **Constraints**: pravidlá z časti 1, ktoré sa týkajú tejto úlohy.
5. **Steps**: číslované kroky vrátane príkazov.
6. **Verification**: checklist z časti 8 + úlohovo špecifické kontroly; výstup buildu sa kontroluje, nie len zdrojový kód.
7. **Deliverables**: commit na správnu vetvu, zoznam zmenených súborov, balík a postup nasadenia ak vzniká.
8. **Report**: slovenský report (zmenené, overené, neoverené a prečo, ručné kroky pre klienta).

Pravidlá pre prompt: anglicky; žiadne tajomstvá ani kľúče; žiadny identifikátor modelu v
prompte, v commitoch ani v súboroch repozitára; chýbajúci údaj sa označí ako chýbajúci,
nikdy sa nevymýšľa.

## 10. Nový web pre iného klienta — creative interview

Len pre nový web alebo redesign s kreatívnym zadaním. Nie pre M.I.Auto.

**Rola:** senior web designer, creative director, UX/UI a art director. Najprv pochopiť, nie generovať.

**Pravidlo:** negenerovať obrázky, videá, mockupy ani web bez výslovného súhlasu. Pred každou
platenou generáciou vypísať: čo, prečo, model, odhadovaná cena (ak nie je istá, povedať, že
treba overiť v účte klienta; cenu nevymýšľať), výsledok. Potom sa opýtať
**„Môžem túto generáciu spustiť?"** Bez jasného áno nič. Negenerovať takmer identické obrázky.

**Bloky** (po malých skupinách, po každom zhrnutie, nie 30 otázok naraz; pri neistote ponúknuť voľby):
- **A. Základ:** názov, slogan, čo sa ponúka, hlavný cieľ (predaj, leady, portfólio, služba, rezervácie, e-shop, značka, kontakty), cieľový návštevník (B2B/B2C, vek, odbornosť, problém, prečo práve oni).
- **B. Vizuál:** farby (existujúce firemné?), svetlý/tmavý, akcenty, nálada; pri neistote max. 3 smery. Logo, písmo, či má web patriť k existujúcej značke.
- **C. Štýl:** minimalistický, futuristický, technologický, luxusný, brutalistický, editoriálny, Apple-štýl, dark, clean white, retro-futuristický, industriálny, elegantný, playful, cinematic, 3D. Otázka: „Tromi slovami, aký má byť web?"
- **D. Referencie:** web, ktorý sa páči; screenshoty; Pinterest/Behance; konkrétne prvky (hero, animácie, navigácia, typografia, layout, fotky, 3D, scroll). Bez referencie najprv slovný creative direction (štýl, farebná atmosféra, typ fotiek, grafika, typografia, kompozícia, animácie, nálada); referenčný obrázok až po schválení.
- **E. Emócia:** čo má návštevník cítiť v prvých 5 sekundách a čo si odnesie (drahé, profesionálne, dôveryhodné, jednoduché, odvážne…).
- **F. Funkcie:** kontakt, e-shop, rezervácie, galéria, blog, portfólio, login, viac jazykov, animácie, video, 3D, mobil ako priorita. Nenavrhovať funkcie, ktoré k projektu nepatria.
- **G. Správanie:** rýchly a jednoduchý, alebo cinematic a imerzívny? Scroll, micro-interakcie, reakcia na pohyb myši.
- **H. Obsah:** sekcie, texty, fotky, videá, logo. Ak nič nie je, pomôcť so plánom obsahu.

**Doplňujúce otázky** prispôsobiť projektu: fullscreen hero?, je produkt hneď viditeľný?, výrazná
alebo minimalistická navigácia?, veľká alebo jemná typografia?, symetria alebo experiment?,
viac whitespace alebo hustejšie?, statické alebo dynamické?, viac fotiek alebo grafiky?,
nadčasový alebo trendový?

**Výstup:** creative brief v deviatich bodoch (projekt, návštevník, hlavná emócia, vizuálny štýl,
hero vízia, vizuálne prvky, animácie s podporou dizajnu, funkcie, poradie sekcií). Z neho sa
pripraví prompt podľa časti 9. Záver: **„Schvaľuješ tento plán a môžem pokračovať?"**

## 11. Začiatok práce na M.I.Auto

1. Prečítať tento skill; `git status`; overiť branch.
2. Prečítať `miauto/SPRAVA.md` a `miauto/README.md` (aktuálny stav).
3. `npm run typecheck` ako základ.
4. Pýtať len to, čo chýba v časti 2 alebo 7. Nezopakovať zodpovedané otázky.
5. Pripraviť prompt podľa časti 9 alebo vykonať úlohu, ak je to výslovne žiadané.
