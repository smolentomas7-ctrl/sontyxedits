# M.I.Auto — čo ešte treba doplniť

Tento súbor je pre vás, nie pre programátora. Je v ňom napísané, čo na stránke
zatiaľ chýba, čo treba doplniť pred spustením a čo na stránke zatiaľ nefunguje
naplno. Žiadny kód tu nie je.

---

## 1. Čo treba doplniť

Na stránke sú miesta, kde zatiaľ nie je skutočný údaj. Sú **naschvál viditeľné**
a napísané v hranatých zátvorkách, napríklad `[EMAIL]`. Je to preto, aby sa na ne
nezabudlo — kým ich nedoplníme, je na stránke jasne vidieť, že tam niečo chýba.

### Údaje o firme

| Čo chýba | Kde to na stránke vidno |
|---|---|
| **E-mailová adresa** | v pätičke, na stránke Kontakt a v ochrane osobných údajov |
| **IČO** | v pätičke a v ochrane osobných údajov |
| **Facebook a Instagram** | zatiaľ sa nezobrazujú vôbec — objavia sa až keď dodáte odkazy |

### Texty o servise

Na stránke **O servise** sú dve prázdne miesta:

- **Text o servise** — pár viet o tom, čo je M.I.Auto a ako funguje.
- **Text o majiteľovi** — pár viet o vás.

Meno **Ivan Kubis** na stránke už je. Texty sme nevymýšľali: čokoľvek, čo by sme
napísali za vás, by bolo vymyslené, a to si zákazník vie overiť.

### Čo presne robíte — sedem otázok

Pri každej službe je žltý rámček začínajúci `[TO CONFIRM: ...]`. Sú to veci,
ktoré nikto nepotvrdil, a preto sme ich nenapísali. **Toto je najdôležitejšia
vec na doplnenie**, pretože zákazník sa presne na toto pýta:

1. **Diagnostika** — ktoré značky a ktoré systémy viete diagnostikovať?
2. **Čipovanie ECU** — aké typy úprav robíte a pre ktoré motory?
3. **Geometria** — máte 3D alebo laserovú? Ktoré vozidlá a rozmery zvládnete?
4. **Pneuservis** — robíte prezúvanie, vyvažovanie, sezónnu výmenu, opravu
   defektov, uskladnenie pneumatík? Ktoré z toho?
5. **Elektroinštalácia** — aké konkrétne elektro opravy robíte?
6. **Rozvody** — na ktorých motoroch okrem 2.0 TDI a 3.0 TDI? Je vo výmene aj
   vodné čerpadlo?
7. **Klimatizácia** — robíte diagnostiku, plnenie, hľadanie únikov, čistenie,
   dezinfekciu, opravy? A s ktorými chladivami (R134a / R1234yf)?

Stačí odpovedať v bežnej reči. Doplnenie je potom otázka chvíle.

### Fotografie

Z toho, čo ste poslali, sú **vaše skutočné fotky** použité na úvodnej stránke, na
stránke O servise a pri servise klimatizácie. Pri ostatných službách sú zatiaľ
všeobecné obrázky — nie je na nich vaša dielňa a v popise obrázka to nikde
netvrdíme.

Hodilo by sa doplniť:

- **logo** ako samostatný súbor (teraz je názov vysádzaný písmom),
- **fotku dielne zvonku** a **vašu fotku**,
- **úvodnú fotku bez loga uprostred** — logo je do nej natvrdo vložené a nadpis
  cez neho musí prekrývať.

---

## 2. Čo zatiaľ nefunguje naplno

### Kontaktný formulár

Formulár odosiela správy **až po nasadení na Netlify**. Dovtedy, keď ho niekto
vyplní, uvidí chybovú hlášku a telefónne číslo. Je to naschvál: radšej čestná
chyba než „správa odoslaná" pri správe, ktorá nikam nešla.

Po nasadení treba v Netlify ešte nastaviť, na ktorý e-mail majú správy chodiť.

### Hláška „Teraz otvorené / zatvorené"

Na stránke sa automaticky počíta, či máte práve otvorené. Vie o vašich hodinách
pondelok až piatok 07:00–17:00, o obedňajšej prestávke 12:00–13:00 a o
zatvorenom víkende. Počas prestávky nepíše „zatvorené", ale „Obedňajšia
prestávka — otvárame o 13:00", aby zákazníka neposlala preč.

**Nevie o štátnych sviatkoch.** Na sviatok, ktorý padne na pracovný deň, bude
stránka tvrdiť, že máte otvorené. Nevymýšľali sme zoznam sviatkov, lebo
nesprávny zoznam je horší než žiadny.

### Mapa

Mapa hľadá adresu `Sládkovičova 2528/108, 034 01 Ružomberok`. Presné súradnice
sme nedostali, takže polohu určuje Google z adresy. **Prosím, pozrite si po
spustení, či ukazuje na správnu budovu.** Ak nie, dá sa to opraviť zmenou
jedného riadku.

### Automatický asistent (chat vpravo dole)

Teraz funguje v **jednoduchom režime**: má pripravené odpovede na bežné otázky —
služby, otváracie hodiny, adresa, ako sa objednať. Nepozná ceny, termíny ani
trvanie opravy a na takéto otázky zámerne odpovie, že ich nevie, a dá telefónne
číslo.

Dá sa prepnúť do **inteligentného režimu**, kde odpovedá voľnejšie a stále len z
obsahu tejto stránky. To si vyžaduje platený prístup k jazykovému modelu
(programátor nastaví dva údaje v Netlify). Aj potom platí to isté: ceny, termíny
ani výkonové čísla nepovie nikdy — je to v ňom zablokované a overené testami.

V hlavičke chatu je napísané, že ide o automatického asistenta, nie o človeka.
Rozhovor sa nikde neukladá — zmizne, keď zákazník zatvorí okno.

### Ochrana osobných údajov

Stránka s ochranou osobných údajov je **vzor, nie hotový právny dokument**. Je to
na nej hore aj napísané. Pred spustením by sa na to mal pozrieť niekto, kto sa
právu venuje. Netvrdíme na nej, že je v súlade s GDPR — také tvrdenie by sme za
vás urobiť nemohli.

---

## 3. Čo sme naschvál neurobili

Aby bolo jasné, že to nie je opomenutie:

- **Žiadne ceny.** Nikde na stránke ani v chate. Žiadne sme nedostali.
- **Žiadne recenzie ani hviezdičky.** Žiadne neexistujú, a vymyslené recenzie sú
  vymyslené.
- **Žiadne čísla typu „20 rokov skúseností" alebo „5000 opravených vozidiel".**
  Nikto nám ich nepotvrdil.
- **Nikde netvrdíme, že ste autorizovaný servis Volkswagen.** Na stránke o
  elektroinštalácii je naopak jasne napísané, že ste **nezávislý** autoservis.
  Ak autorizáciu máte, povedzte — doplní sa.
- **Žiadne lišty so súhlasom so sušienkami.** Stránka nič nesleduje, nemá
  analytiku a nenastavuje sledovacie súbory. Nie je na čo dávať súhlas. Keby ste
  neskôr chceli merať návštevnosť, lišta bude potrebná a musí byť **pred** tým,
  než sa čokoľvek načíta.
- **Pri úprave softvéru motora nie sú žiadne čísla.** Žiadne kone, žiadne Nm,
  žiadna spotreba, a nič o emisiách ani o technickej kontrole. Na stránke je
  napísané, že sa to preberá telefonicky nad konkrétnym vozidlom.

---

## 4. Keď budete chcieť niečo zmeniť

Všetky texty sú v dvoch súboroch — jeden slovenský, jeden anglický. Keď pošlete,
čo chcete zmeniť, úprava je rýchla. **Dôležité:** text treba zmeniť v oboch
jazykoch, inak sa stránka ani nedá zostaviť — je to naschvál poistka proti tomu,
aby anglická verzia potichu zaostávala za slovenskou.
