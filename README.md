# Sontyx — web

Jednostránkový web pre `@editsbysontyx`. Čisté HTML, CSS a JavaScript — žiadna inštalácia, žiadny build.

## Skôr než web zverejníš

V obsahu sú zámerne dočasné veci, ktoré treba nahradiť skutočnými:

- **Recenzie** — tri ukážkové recenzie majú meno „Placeholder Name". Nahraď ich reálnymi ohlasmi od klientov, alebo celú sekciu odstráň.
- **Čísla v sekcii O mne** — `250+` projektov, `40+` klientov, `4` roky, `48h` dodanie sú odhady. Uprav ich na svoje skutočné.
- **Portfólio** — šesť kariet zatiaľ ukazuje prázdne náhľady. Doplň skutočné videá (nižšie).

## Spustenie na počítači

```
python3 -m http.server 8080
```

Potom otvor `http://localhost:8080`. (Otvoriť `index.html` priamo dvojklikom tiež funguje, ale video sa nemusí načítať.)

## Úprava textov

Všetky texty sú v `js/i18n.js` — v troch jazykoch: `en` (predvolený), `sk`, `cs`.
Nájdi text, ktorý chceš zmeniť, a prepíš ho. Meň ho vo všetkých troch jazykoch, aby prepínač fungoval správne.

Web sa vždy otvorí v angličtine. Keď si návštevník prepne jazyk, prehliadač si to zapamätá.

## Pridanie videa do portfólia

1. Vlož súbor do `assets/video/` (napr. `praca-01.mp4`).
2. V `index.html` nájdi príslušnú kartu a doplň do nej `data-video`:

```html
<article class="work-card" data-format="wide" data-video="assets/video/praca-01.mp4">
```

Video sa prehrá, keď naň návštevník nabehne myšou.

- `data-format="wide"` — horizontálne video (16:9, YouTube)
- `data-format="tall"` — vertikálne video (9:16, Reels/TikTok/Shorts)
- voliteľne `data-poster="assets/img/nahlad.jpg"` — náhľadový obrázok

Karty bez `data-video` ostanú ako prázdne placeholdery.

## Výmena obrázka v sekcii O mne

Vlož vlastný obrázok do `assets/img/` a v `index.html` zmeň `src` z `assets/img/about.svg` na svoj súbor.

## Výmena videa v pozadí

Nahraď `assets/video/hero-loop.mp4` a `assets/video/hero-loop.webm`. Ak máš len MP4, riadok s `.webm` v `index.html` zmaž.
Náhľadový obrázok (zobrazí sa, kým sa video načíta) je `assets/img/hero-poster.jpg`.

## Zverejnenie zadarmo cez GitHub Pages

V repozitári: **Settings → Pages → Source: Deploy from a branch → Branch: main / (root) → Save.**
O pár minút web pobeží na `https://smolentomas7-ctrl.github.io/sontyxedits/`.

## Štruktúra

```
index.html          obsah a sekcie
css/styles.css      vzhľad (farby sú hore v :root)
js/i18n.js          všetky texty v EN / SK / CZ
js/main.js          prepínač jazykov, animácie, prehrávanie videí
assets/             video, obrázky
```
