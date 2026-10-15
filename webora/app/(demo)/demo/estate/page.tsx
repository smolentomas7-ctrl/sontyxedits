import type { Metadata } from "next";
import Image from "next/image";
import { Phone, Mail } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { PropertySearch } from "./PropertySearch";
import { MortgageCalculator } from "./MortgageCalculator";
import { ViewingForm } from "./ViewingForm";
import { estate } from "@/config/images";
import { AGENTS } from "./data";

export const metadata: Metadata = {
  title: "Domov Reality — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#ponuka", label: "Ponuka" },
  { href: "#kalkulacka", label: "Kalkulačka" },
  { href: "#makleri", label: "Makléri" },
  { href: "#kontakt", label: "Kontakt" },
];

export default function EstateDemo() {
  return (
    <DemoShell kind="info">
      <div
        id="top"
        className="min-h-screen bg-[#F7F9FB] font-[family-name:var(--font-inter)] text-[#0E2A47] antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[19px] font-bold tracking-[-0.01em]">
              Domov<span className="text-[#1F9D64]"> Reality</span>
            </span>
          }
          links={NAV}
          action={{ href: "#kontakt", label: "Kontaktovať" }}
          bg="rgba(247,249,251,0.94)"
          fg="#0E2A47"
          border="#D9E0E8"
          accent="#17457A"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[56vh] min-h-[380px] w-full">
            <Image
              src={estate.hero.src}
              alt={estate.hero.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-[#0E2A47]/68" />
            <div className="absolute inset-0 flex items-center">
              <div className="mx-auto w-full max-w-[1240px] px-5 md:px-8">
                <h1 className="max-w-[18ch] font-[family-name:var(--font-space-grotesk)] text-[2.25rem] font-bold leading-[1.08] tracking-[-0.025em] text-white md:text-[3.5rem]">
                  Nájdite dom, v ktorom zostanete
                </h1>
                <p className="mt-5 max-w-[46ch] text-[17px] leading-relaxed text-white/80">
                  Šesť aktuálnych ponúk v Bratislave a okolí. Bez provízie pre kupujúceho.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- LISTINGS + SEARCH ---------- */}
        <section id="ponuka" className="mx-auto max-w-[1240px] px-5 py-16 md:px-8 md:py-24">
          <h2 className="mb-7 font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
            Ponuka nehnuteľností
          </h2>
          <PropertySearch />
        </section>

        {/* ---------- MAP + CALCULATOR ---------- */}
        <section
          id="kalkulacka"
          className="border-y border-[#D9E0E8] bg-white py-16 md:py-24"
        >
          <div className="mx-auto max-w-[1240px] px-5 md:px-8">
            <div className="grid gap-10 lg:grid-cols-2 lg:gap-14">
              <div>
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
                  Kde pôsobíme
                </h2>
                <p className="mt-3 max-w-[48ch] text-[16px] text-[#5B6977]">
                  Bratislava a okolie do 40 km. Pre nehnuteľnosti mimo tejto oblasti vieme
                  odporučiť kolegov.
                </p>

                <div
                  role="img"
                  aria-label="Zástupný blok namiesto interaktívnej mapy"
                  className="mt-7 flex h-[320px] items-center justify-center rounded-xl border-2 border-dashed border-[#C6D2DE] bg-[#EEF3F8] text-center"
                >
                  <div className="px-8">
                    <p className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold text-[#17457A]">
                      Miesto pre mapu
                    </p>
                    <p className="mx-auto mt-2 max-w-[38ch] text-[14px] leading-relaxed text-[#5B6977]">
                      V ukážke mapu nevkladáme. Google Maps vyžaduje API kľúč a fakturačný
                      účet, ktoré by sme do demo webu nedávali. V ostrej verzii sem príde
                      interaktívna mapa so všetkými ponukami.
                    </p>
                  </div>
                </div>
              </div>

              <MortgageCalculator />
            </div>
          </div>
        </section>

        {/* ---------- AGENTS ---------- */}
        <section id="makleri" className="mx-auto max-w-[1240px] px-5 py-16 md:px-8 md:py-24">
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
            Naši makléri
          </h2>

          <ul className="mt-10 grid gap-6 sm:grid-cols-2">
            {AGENTS.map((agent) => (
              <li
                key={agent.name}
                className="flex gap-5 rounded-xl border border-[#D9E0E8] bg-white p-5"
              >
                <Image
                  src={agent.image.src}
                  width={agent.image.width}
                  height={agent.image.height}
                  alt={agent.image.alt}
                  loading="lazy"
                  sizes="140px"
                  className="h-[170px] w-[136px] shrink-0 rounded-lg object-cover"
                />
                <div className="min-w-0">
                  <h3 className="font-[family-name:var(--font-space-grotesk)] text-[18px] font-bold">
                    {agent.name}
                  </h3>
                  <p className="mt-1 text-[14px] text-[#1F9D64]">{agent.role}</p>
                  <ul className="mt-4 flex flex-col gap-2 text-[14px] text-[#5B6977]">
                    <li className="flex items-center gap-2">
                      <Phone aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
                      {agent.phone}
                    </li>
                    <li className="flex items-start gap-2">
                      <Mail aria-hidden="true" strokeWidth={1.5} className="mt-0.5 size-4 shrink-0" />
                      <span className="break-all">{agent.email}</span>
                    </li>
                  </ul>
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-6 text-[13px] text-[#8A98A6]">
            Makléri sú vymyslené postavy pre potreby tejto ukážky.
          </p>
        </section>

        {/* ---------- CONTACT ---------- */}
        <section id="kontakt" className="border-t border-[#D9E0E8] bg-white py-16 md:py-24">
          <div className="mx-auto max-w-[1240px] px-5 md:px-8">
            <div className="grid gap-10 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
              <div>
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
                  Máte otázku?
                </h2>
                <p className="mt-4 max-w-[44ch] text-[16px] leading-relaxed text-[#5B6977]">
                  Napíšte nám, aj keď si nie ste istí, či je pre vás daná nehnuteľnosť vhodná.
                  Obhliadka je nezáväzná a nič vás nestojí.
                </p>

                <dl className="mt-9 flex flex-col gap-5 text-[15px]">
                  {[
                    { k: "Kancelária", v: "Štúrova 8, 811 02 Bratislava" },
                    { k: "Telefón", v: "+421 900 000 000" },
                    { k: "E-mail", v: "info@domovreality.example" },
                    { k: "Otvorené", v: "Pondelok – Piatok, 9:00 – 18:00" },
                  ].map((row) => (
                    <div key={row.k} className="border-b border-[#EDF1F5] pb-4">
                      <dt className="text-[13px] uppercase tracking-[0.1em] text-[#8A98A6]">
                        {row.k}
                      </dt>
                      <dd className="mt-1">{row.v}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <ViewingForm />
            </div>
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="border-t border-[#D9E0E8] bg-[#0E2A47] py-10 text-white/55">
          <div className="mx-auto flex max-w-[1240px] flex-col gap-3 px-5 text-[14px] md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold text-white">
              Domov Reality
            </p>
            <p>Vymyslená kancelária. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
