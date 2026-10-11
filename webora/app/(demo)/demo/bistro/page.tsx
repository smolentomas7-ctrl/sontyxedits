import type { Metadata } from "next";
import Image from "next/image";
import { MapPin, Clock, Phone } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { BistroMenu } from "./BistroMenu";
import { ReservationForm } from "./ReservationForm";
import { bistro } from "@/config/images";

export const metadata: Metadata = {
  title: "Bistro Hĺbka — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#o-nas", label: "O nás" },
  { href: "#menu", label: "Menu" },
  { href: "#galeria", label: "Galéria" },
  { href: "#kontakt", label: "Kontakt" },
];

const HOURS = [
  { day: "Pondelok – Štvrtok", time: "8:00 – 22:00" },
  { day: "Piatok", time: "8:00 – 24:00" },
  { day: "Sobota", time: "9:00 – 24:00" },
  { day: "Nedeľa", time: "9:00 – 16:00" },
];

const GALLERY = [
  bistro.gallery1,
  bistro.gallery2,
  bistro.gallery3,
  bistro.gallery4,
  bistro.gallery5,
  bistro.gallery6,
];

export default function BistroDemo() {
  return (
    <DemoShell pkg="business">
      <div
        id="top"
        className="min-h-screen bg-[#FAF7F2] font-[family-name:var(--font-inter)] text-[#243B30] antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[19px] font-bold tracking-[-0.01em]">
              Bistro Hĺbka
            </span>
          }
          links={NAV}
          action={{ href: "#rezervacia", label: "Rezervovať stôl" }}
          bg="rgba(250,247,242,0.92)"
          fg="#1F3D2F"
          border="#E3DACB"
          accent="#C4653A"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[72vh] min-h-[460px] w-full">
            <Image
              src={bistro.hero.src}
              alt={bistro.hero.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#1F3D2F]/88 via-[#1F3D2F]/45 to-[#1F3D2F]/20" />

            <div className="absolute inset-0 flex items-end">
              <div className="mx-auto w-full max-w-[1200px] px-5 pb-14 md:px-8 md:pb-20">
                <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.22em] text-[#E9B894]">
                  Káva · raňajky · večere
                </p>
                <h1 className="max-w-[16ch] font-[family-name:var(--font-space-grotesk)] text-[2.5rem] font-bold leading-[1.05] tracking-[-0.02em] text-[#FAF7F2] md:text-[4.25rem]">
                  Miesto, kde sa dá zostať dlhšie
                </h1>
                <p className="mt-5 max-w-[46ch] text-[17px] leading-relaxed text-[#FAF7F2]/85">
                  Sezónna kuchyňa, káva z vlastnej pražiarne a stôl, ktorý vás nikto nepýta uvoľniť.
                  V centre mesta od roku 2019.
                </p>
                <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                  <a
                    href="#rezervacia"
                    className="inline-flex h-12 items-center justify-center rounded-lg bg-[#C4653A] px-7 font-medium text-[#FAF7F2] transition-colors duration-150 hover:bg-[#A8522C]"
                  >
                    Rezervovať stôl
                  </a>
                  <a
                    href="#menu"
                    className="inline-flex h-12 items-center justify-center rounded-lg border border-[#FAF7F2]/55 bg-[#14291F]/88 px-7 font-medium text-[#FAF7F2] backdrop-blur-sm transition-colors duration-150 hover:bg-[#14291F]"
                  >
                    Pozrieť menu
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- ABOUT ---------- */}
        <section id="o-nas" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="grid items-center gap-10 md:grid-cols-2 md:gap-16">
            <div className="overflow-hidden rounded-2xl">
              <Image
                src={bistro.about.src}
                width={bistro.about.width}
                height={bistro.about.height}
                alt={bistro.about.alt}
                sizes="(max-width: 768px) 100vw, 50vw"
                className="h-full w-full object-cover"
              />
            </div>

            <div>
              <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.2em] text-[#C4653A]">
                O nás
              </p>
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold leading-tight tracking-[-0.02em] text-[#1F3D2F] md:text-[2.75rem]">
                Varíme z toho, čo je práve teraz dobré
              </h2>
              <div className="mt-6 flex flex-col gap-4 text-[16px] leading-relaxed text-[#4A5D52]">
                <p>
                  Menu meníme každé tri týždne podľa toho, čo nám dovezú pestovatelia z okolia.
                  Nie je to marketingová fráza — znamená to, že vaše obľúbené jedlo sa na jeseň
                  nemusí v ponuke objaviť.
                </p>
                <p>
                  Kávu pražíme sami v malej pražiarni za rohom. Ak chcete vedieť, odkiaľ je,
                  spýtajte sa ktoréhokoľvek baristu — povie vám aj meno farmy.
                </p>
                <p>
                  Máme desať stolov. Je to málo, ale znamená to, že vás nikto nebude naháňať.
                </p>
              </div>

              <dl className="mt-9 grid grid-cols-3 gap-4 border-t border-[#E3DACB] pt-7">
                {[
                  { k: "Otvorené od", v: "2019" },
                  { k: "Stolov", v: "10" },
                  { k: "Menu meníme", v: "3 týždne" },
                ].map((stat) => (
                  <div key={stat.k}>
                    <dt className="text-[13px] text-[#7E8C84]">{stat.k}</dt>
                    <dd className="mt-1 font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#1F3D2F]">
                      {stat.v}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>
        </section>

        {/* ---------- MENU ---------- */}
        <section id="menu" className="border-y border-[#E3DACB] bg-[#F3EEE5] py-20 md:py-28">
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <div className="mb-12 text-center">
              <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.2em] text-[#C4653A]">
                Menu
              </p>
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.02em] text-[#1F3D2F] md:text-[2.75rem]">
                Čo u nás nájdete
              </h2>
              <p className="mx-auto mt-4 max-w-[52ch] text-[16px] text-[#4A5D52]">
                Ukážka aktuálnej ponuky. Kompletný lístok vrátane alergénov nájdete na stole.
              </p>
            </div>

            <BistroMenu />
          </div>
        </section>

        {/* ---------- GALLERY ---------- */}
        <section id="galeria" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="mb-12">
            <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.2em] text-[#C4653A]">
              Galéria
            </p>
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.02em] text-[#1F3D2F] md:text-[2.75rem]">
              U nás
            </h2>
          </div>

          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {GALLERY.map((image) => (
              <li key={image.src} className="overflow-hidden rounded-xl">
                <Image
                  src={image.src}
                  width={image.width}
                  height={image.height}
                  alt={image.alt}
                  loading="lazy"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  className="aspect-[3/2] w-full object-cover transition-transform duration-300 hover:scale-[1.04]"
                />
              </li>
            ))}
          </ul>
        </section>

        {/* ---------- HOURS + LOCATION + RESERVATION ---------- */}
        <section
          id="kontakt"
          className="border-t border-[#E3DACB] bg-[#1F3D2F] py-20 text-[#FAF7F2] md:py-28"
        >
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
              <div>
                <p className="mb-4 text-[13px] font-medium uppercase tracking-[0.2em] text-[#E9B894]">
                  Kde nás nájdete
                </p>
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.02em] md:text-[2.75rem]">
                  Otváracie hodiny
                </h2>

                <dl className="mt-8 flex flex-col">
                  {HOURS.map((row) => (
                    <div
                      key={row.day}
                      className="flex items-baseline justify-between gap-6 border-b border-[#FAF7F2]/15 py-3.5"
                    >
                      <dt className="text-[15px] text-[#FAF7F2]/75">{row.day}</dt>
                      <dd className="font-medium">{row.time}</dd>
                    </div>
                  ))}
                </dl>

                <ul className="mt-9 flex flex-col gap-4 text-[15px]">
                  <li className="flex items-start gap-3">
                    <MapPin aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-5 shrink-0 text-[#E9B894]" />
                    <span>
                      Hlavná 14, 811 01 Bratislava
                      <br />
                      <span className="text-[#FAF7F2]/65">Vo dvore, vchod zo Zelenej ulice</span>
                    </span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Phone aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0 text-[#E9B894]" />
                    <span>+421 900 000 000</span>
                  </li>
                  <li className="flex items-center gap-3">
                    <Clock aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0 text-[#E9B894]" />
                    <span>Kuchyňa varí do 21:30</span>
                  </li>
                </ul>

                <div
                  role="img"
                  aria-label="Zástupný blok namiesto mapy"
                  className="mt-9 flex h-52 items-center justify-center rounded-xl border border-dashed border-[#FAF7F2]/25 bg-[#FAF7F2]/5 text-center text-[14px] text-[#FAF7F2]/60"
                >
                  <span className="px-6">
                    Tu by bola mapa.
                    <br />
                    V ukážke ju nevkladáme, aby sme nevyžadovali API kľúč.
                  </span>
                </div>
              </div>

              <div id="rezervacia">
                <ReservationForm />
              </div>
            </div>
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="bg-[#162B21] py-10 text-[#FAF7F2]/60">
          <div className="mx-auto flex max-w-[1200px] flex-col gap-3 px-5 text-[14px] md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold text-[#FAF7F2]">
              Bistro Hĺbka
            </p>
            <p>Vymyslená prevádzka. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
