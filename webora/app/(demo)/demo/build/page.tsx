import type { Metadata } from "next";
import Image from "next/image";
import { Phone, Mail } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { BeforeAfter } from "./BeforeAfter";
import { QuoteForm } from "./QuoteForm";
import { build } from "@/config/images";

export const metadata: Metadata = {
  title: "Stavmont — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#sluzby", label: "Služby" },
  { href: "#premeny", label: "Premeny" },
  { href: "#realizacie", label: "Realizácie" },
  { href: "#postup", label: "Postup" },
  { href: "#dopyt", label: "Dopyt" },
];

const SERVICES = [
  {
    name: "Murárske práce",
    body: "Nosné aj priečkové murivo, preklady, omietky. Vlastná partia, nie subdodávka.",
    image: build.serviceMasonry,
  },
  {
    name: "Strechy",
    body: "Škridla, plech aj bridlica. Vrátane klampiarskych prvkov a zateplenia podkrovia.",
    image: build.serviceRoofing,
  },
  {
    name: "Interiéry",
    body: "Kompletné rekonštrukcie bytov vrátane rozvodov, podláh a sadrokartónov.",
    image: build.serviceInteriors,
  },
  {
    name: "Rekonštrukcie",
    body: "Staršie domy a pamiatkovo chránené objekty. Riešime aj povolenia.",
    image: build.serviceRenovations,
  },
];

const PROJECTS = [
  build.project1,
  build.project2,
  build.project3,
  build.project4,
  build.project5,
  build.project6,
];

const PROCESS = [
  { title: "Obhliadka", body: "Prídeme na miesto, odmeriame a vypočujeme si, čo potrebujete. Zadarmo." },
  { title: "Cenová ponuka", body: "Položkový rozpočet do 10 dní. Bez skrytých položiek." },
  { title: "Harmonogram", body: "Dohodneme termíny jednotlivých etáp a kto kedy nastúpi." },
  { title: "Realizácia", body: "Jeden stavbyvedúci na celý projekt, týždenné hlásenia o postupe." },
  { title: "Odovzdanie", body: "Prebierka s vami, zápis o chybách a ich odstránenie do 14 dní." },
];

export default function BuildDemo() {
  return (
    <DemoShell pkg="business">
      <div
        id="top"
        className="min-h-screen bg-[#F2F2EF] font-[family-name:var(--font-inter)] text-[#1C1C1A] antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[20px] font-bold uppercase tracking-[0.04em]">
              Stav<span className="text-[#C9A227]">mont</span>
            </span>
          }
          links={NAV}
          action={{ href: "#dopyt", label: "Dopyt na cenu" }}
          bg="rgba(242,242,239,0.94)"
          fg="#1C1C1A"
          border="#D4D4D0"
          accent="#F5C518"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[66vh] min-h-[420px] w-full">
            <Image
              src={build.hero.src}
              alt={build.hero.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-[#1C1C1A]/92 via-[#1C1C1A]/70 to-[#1C1C1A]/30" />
            <div className="absolute inset-0 flex items-center">
              <div className="mx-auto w-full max-w-[1200px] px-5 md:px-8">
                <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
                <h1 className="max-w-[15ch] font-[family-name:var(--font-space-grotesk)] text-[2.5rem] font-bold uppercase leading-[1] tracking-[-0.02em] text-white md:text-[4.5rem]">
                  Staviame od roku 2008
                </h1>
                <p className="mt-6 max-w-[46ch] text-[17px] leading-relaxed text-white/80">
                  Rekonštrukcie, prístavby a strechy v Bratislave a okolí. Pevná cena,
                  jeden stavbyvedúci a termín, ktorý platí.
                </p>
                <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                  <a
                    href="#dopyt"
                    className="inline-flex h-12 items-center justify-center bg-[#F5C518] px-8 font-bold uppercase tracking-wide text-[#1C1C1A] transition-colors duration-150 hover:bg-[#E0B30C]"
                  >
                    Nezáväzný dopyt
                  </a>
                  <a
                    href="#realizacie"
                    className="inline-flex h-12 items-center justify-center border-2 border-white/70 bg-[#141413]/90 px-8 font-bold uppercase tracking-wide text-white backdrop-blur-sm transition-colors duration-150 hover:bg-[#141413]"
                  >
                    Naše realizácie
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- SERVICES ---------- */}
        <section id="sluzby" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
            Čo robíme
          </h2>

          <ul className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {SERVICES.map((service) => (
              <li key={service.name} className="bg-white">
                <Image
                  src={service.image.src}
                  width={service.image.width}
                  height={service.image.height}
                  alt={service.image.alt}
                  loading="lazy"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                  className="aspect-square w-full object-cover"
                />
                <div className="p-5">
                  <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-bold uppercase">
                    {service.name}
                  </h3>
                  <p className="mt-2 text-[14px] leading-relaxed text-[#6B6B66]">{service.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* ---------- BEFORE / AFTER ---------- */}
        <section id="premeny" className="border-y border-[#D4D4D0] bg-[#E4E4DF] py-20 md:py-28">
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
              Pred a po
            </h2>
            <p className="mt-3 max-w-[56ch] text-[16px] text-[#5A5A55]">
              Posúvajte deliacu čiaru myšou, prstom alebo šípkami na klávesnici.
            </p>

            <div className="mt-12 grid gap-10 lg:grid-cols-2">
              <div>
                <BeforeAfter
                  before={build.ba1Before}
                  after={build.ba1After}
                  label="Porovnanie: podkrovie pred a po rekonštrukcii"
                />
                <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase">
                  Podkrovie, Ružinov
                </h3>
                <p className="mt-1.5 text-[15px] text-[#6B6B66]">
                  Z nevyužitého pôjdu spálňa s kúpeľňou. Zateplenie, nové krovné výmeny,
                  strešné okná. 9 týždňov.
                </p>
              </div>

              <div>
                <BeforeAfter
                  before={build.ba2Before}
                  after={build.ba2After}
                  label="Porovnanie: kuchyňa pred a po rekonštrukcii"
                />
                <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase">
                  Kuchyňa, Petržalka
                </h3>
                <p className="mt-1.5 text-[15px] text-[#6B6B66]">
                  Kompletná výmena vrátane rozvodov vody a elektriky. Nová linka na mieru.
                  5 týždňov.
                </p>
              </div>
            </div>

            <p className="mt-10 border-l-4 border-[#C9A227] bg-white/60 px-5 py-4 text-[14px] text-[#5A5A55]">
              Pre tretiu dvojicu sme nedostali zodpovedajúcu fotografiu „po“, takže ju tu
              neukazujeme. Fotka pôvodného stavu je v galérii realizácií nižšie.
            </p>
          </div>
        </section>

        {/* ---------- PROJECTS ---------- */}
        <section id="realizacie" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
            Realizácie
          </h2>

          <ul className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...PROJECTS, build.derelict].map((image) => (
              <li key={image.src} className="overflow-hidden">
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

        {/* ---------- PROCESS ---------- */}
        <section id="postup" className="border-y border-[#D4D4D0] bg-[#1C1C1A] py-20 text-white md:py-28">
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
              Ako postupujeme
            </h2>

            <ol className="mt-12 grid gap-8 md:grid-cols-5">
              {PROCESS.map((step, index) => (
                <li key={step.title}>
                  <span className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold text-[#F5C518]">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <h3 className="mt-3 font-[family-name:var(--font-space-grotesk)] text-[17px] font-bold uppercase">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-[14px] leading-relaxed text-white/60">{step.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        {/* ---------- QUOTE ---------- */}
        <section id="dopyt" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="grid gap-10 lg:grid-cols-[1fr_1.2fr] lg:gap-16">
            <div>
              <div className="mb-5 h-1 w-16 bg-[#F5C518]" />
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
                Napíšte nám
              </h2>
              <p className="mt-4 max-w-[42ch] text-[16px] leading-relaxed text-[#5A5A55]">
                Obhliadka je zadarmo a nezáväzná. Ak projekt nevieme zobrať, povieme to hneď
                a odporučíme niekoho iného.
              </p>

              <ul className="mt-8 flex flex-col gap-4 text-[16px]">
                <li className="flex items-center gap-3">
                  <Phone aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0 text-[#C9A227]" />
                  <span>+421 900 000 000</span>
                </li>
                <li className="flex items-center gap-3">
                  <Mail aria-hidden="true" strokeWidth={1.5} className="size-5 shrink-0 text-[#C9A227]" />
                  <span>dopyt@stavmont.example</span>
                </li>
              </ul>

              <dl className="mt-10 grid grid-cols-3 gap-4 border-t-2 border-[#D4D4D0] pt-7">
                {[
                  { k: "Na trhu", v: "od 2008" },
                  { k: "Stála partia", v: "14 ľudí" },
                  { k: "Záruka", v: "5 rokov" },
                ].map((stat) => (
                  <div key={stat.k}>
                    <dt className="text-[13px] uppercase tracking-wide text-[#6B6B66]">{stat.k}</dt>
                    <dd className="mt-1 font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                      {stat.v}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>

            <QuoteForm />
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="border-t border-[#D4D4D0] bg-[#E4E4DF] py-10">
          <div className="mx-auto flex max-w-[1200px] flex-col gap-3 px-5 text-[14px] text-[#6B6B66] md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold uppercase text-[#1C1C1A]">
              Stavmont
            </p>
            <p>Vymyslená firma. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
