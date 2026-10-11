import type { Metadata } from "next";
import Image from "next/image";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { Gallery } from "./Gallery";
import { InquiryForm } from "./InquiryForm";
import { lens } from "@/config/images";

export const metadata: Metadata = {
  title: "Studio Lens — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#portfolio", label: "Portfólio" },
  { href: "#o-mne", label: "O mne" },
  { href: "#balicky", label: "Balíčky" },
  { href: "#kontakt", label: "Kontakt" },
];

const PACKAGES = [
  {
    name: "Portrét",
    price: "od 180 €",
    items: ["90 minút fotenia", "Jedna lokácia", "20 upravených fotografií", "Dodanie do 10 dní"],
  },
  {
    name: "Svadba",
    price: "od 1 200 €",
    items: [
      "Celý deň, od príprav po prvý tanec",
      "Druhý fotograf",
      "400+ upravených fotografií",
      "Online galéria na rok",
      "Dodanie do 6 týždňov",
    ],
  },
  {
    name: "Produkt",
    price: "od 40 € / kus",
    items: [
      "Štúdio alebo u vás",
      "Biele pozadie aj aranžované zábery",
      "Retuš v cene",
      "Dodanie do 7 dní",
    ],
  },
];

export default function LensDemo() {
  return (
    <DemoShell pkg="starter">
      <div
        id="top"
        className="min-h-screen bg-[#0B0B0C] font-[family-name:var(--font-inter)] text-white antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[15px] font-medium uppercase tracking-[0.34em]">
              Lens
            </span>
          }
          links={NAV}
          bg="rgba(11,11,12,0.9)"
          fg="#FFFFFF"
          border="rgba(255,255,255,0.1)"
          accent="#FFFFFF"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[86vh] min-h-[520px] w-full">
            <Image
              src={lens.hero.src}
              alt={lens.hero.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0B0B0C] via-transparent to-[#0B0B0C]/40" />
            <div className="absolute inset-x-0 bottom-0">
              <div className="mx-auto max-w-[1280px] px-5 pb-16 md:px-8 md:pb-24">
                <h1 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-medium uppercase leading-[1.1] tracking-[0.04em] md:text-[3.25rem]">
                  Studio Lens
                </h1>
                <p className="mt-4 max-w-[40ch] text-[16px] leading-relaxed text-white/60">
                  Portrét, svadba, produkt, krajina. Prirodzené svetlo, minimum réžie.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- PORTFOLIO ---------- */}
        <section id="portfolio" className="mx-auto max-w-[1280px] px-5 py-20 md:px-8 md:py-28">
          <Gallery />
        </section>

        {/* ---------- ABOUT ---------- */}
        <section
          id="o-mne"
          className="border-t border-white/10 py-20 md:py-28"
        >
          <div className="mx-auto max-w-[1100px] px-5 md:px-8">
            <div className="grid items-center gap-12 md:grid-cols-[0.85fr_1.15fr] md:gap-16">
              <Image
                src={lens.about.src}
                width={lens.about.width}
                height={lens.about.height}
                alt={lens.about.alt}
                loading="lazy"
                sizes="(max-width: 768px) 100vw, 40vw"
                className="w-full object-cover grayscale"
              />

              <div>
                <p className="text-[12px] uppercase tracking-[0.3em] text-white/40">O mne</p>
                <h2 className="mt-5 font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-medium leading-tight tracking-[-0.01em] md:text-[2.5rem]">
                  Fotím od roku 2014
                </h2>
                <div className="mt-6 flex flex-col gap-4 text-[16px] leading-relaxed text-white/65">
                  <p>
                    Začínala som pri svadbách kamarátov a ostala pri tom. Dnes fotím zhruba
                    dvadsať svadieb ročne, k tomu portréty a produkty pre menšie značky.
                  </p>
                  <p>
                    Nemám rada pózovanie. Na svadbách sa držím bokom a fotím to, čo sa deje;
                    pri portrétoch radšej hovoríme a fotím medzi vetami.
                  </p>
                  <p>
                    Pracujem s prirodzeným svetlom, kde sa dá. Keď nie, mám so sebou jedno
                    svetlo a softbox — nie celé štúdio.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- PACKAGES ---------- */}
        <section id="balicky" className="border-t border-white/10 py-20 md:py-28">
          <div className="mx-auto max-w-[1100px] px-5 md:px-8">
            <p className="text-[12px] uppercase tracking-[0.3em] text-white/40">Balíčky</p>
            <h2 className="mt-5 font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-medium tracking-[-0.01em] md:text-[2.5rem]">
              Cenník
            </h2>

            <ul className="mt-12 grid gap-px bg-white/10 md:grid-cols-3">
              {PACKAGES.map((pkg) => (
                <li key={pkg.name} className="bg-[#0B0B0C] p-7">
                  <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-medium uppercase tracking-[0.06em]">
                    {pkg.name}
                  </h3>
                  <p className="mt-2 text-[15px] text-white/50">{pkg.price}</p>
                  <ul className="mt-6 flex flex-col gap-2.5">
                    {pkg.items.map((item) => (
                      <li key={item} className="text-[15px] leading-relaxed text-white/65">
                        {item}
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>

            <p className="mt-8 text-[14px] text-white/40">
              Ceny sú orientačné. Konečnú sumu potvrdím po tom, ako si upresníme rozsah.
            </p>
          </div>
        </section>

        {/* ---------- CONTACT ---------- */}
        <section id="kontakt" className="border-t border-white/10 py-20 md:py-28">
          <div className="mx-auto max-w-[1100px] px-5 md:px-8">
            <div className="grid gap-12 lg:grid-cols-2 lg:gap-20">
              <div>
                <p className="text-[12px] uppercase tracking-[0.3em] text-white/40">Kontakt</p>
                <h2 className="mt-5 font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-medium tracking-[-0.01em] md:text-[2.5rem]">
                  Napíšte mi
                </h2>
                <p className="mt-5 max-w-[40ch] text-[16px] leading-relaxed text-white/60">
                  Termíny na svadby sa obsadzujú zhruba rok dopredu. Portréty a produkty
                  väčšinou stihnem do dvoch týždňov.
                </p>

                <dl className="mt-10 flex flex-col gap-4 text-[15px] text-white/65">
                  <div>
                    <dt className="text-[12px] uppercase tracking-[0.2em] text-white/35">
                      E-mail
                    </dt>
                    <dd className="mt-1">ahoj@studiolens.example</dd>
                  </div>
                  <div>
                    <dt className="text-[12px] uppercase tracking-[0.2em] text-white/35">
                      Ateliér
                    </dt>
                    <dd className="mt-1">Mlynské nivy 4, Bratislava</dd>
                  </div>
                </dl>
              </div>

              <InquiryForm />
            </div>
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="border-t border-white/10 py-10">
          <div className="mx-auto flex max-w-[1280px] flex-col gap-3 px-5 text-[13px] text-white/35 md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] uppercase tracking-[0.3em] text-white/70">
              Lens
            </p>
            <p>Vymyslený ateliér. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
