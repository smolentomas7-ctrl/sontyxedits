import type { Metadata } from "next";
import Image from "next/image";
import { Scale, Building2, Users, FileText, Landmark, Briefcase } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { LegalFaq } from "./LegalFaq";
import { ConsultationForm } from "./ConsultationForm";
import { legal } from "@/config/images";

export const metadata: Metadata = {
  title: "Hlavatý & Partners — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#oblasti", label: "Oblasti práva" },
  { href: "#tim", label: "Tím" },
  { href: "#pristup", label: "Prístup" },
  { href: "#otazky", label: "Otázky" },
  { href: "#konzultacia", label: "Konzultácia" },
];

const PRACTICE_AREAS = [
  {
    icon: Building2,
    name: "Obchodné právo",
    body: "Zakladanie a zmeny spoločností, zmluvná agenda, obchodné spory, due diligence pri prevodoch podielov.",
  },
  {
    icon: Landmark,
    name: "Nehnuteľnosti",
    body: "Kúpne a nájomné zmluvy, vecné bremená, zápisy do katastra, developerské projekty.",
  },
  {
    icon: Users,
    name: "Pracovné právo",
    body: "Pracovné zmluvy, skončenie pracovného pomeru, interné smernice, zastupovanie v sporoch.",
  },
  {
    icon: FileText,
    name: "Zmluvné právo",
    body: "Príprava a pripomienkovanie zmlúv, všeobecné obchodné podmienky, zabezpečovacie inštitúty.",
  },
  {
    icon: Scale,
    name: "Súdne spory",
    body: "Zastupovanie pred súdmi všetkých stupňov, rozhodcovské konania, výkon rozhodnutí.",
  },
  {
    icon: Briefcase,
    name: "Insolvencia",
    body: "Reštrukturalizácie, konkurzy, prihlasovanie pohľadávok, oddlženie fyzických osôb.",
  },
];

const ATTORNEYS = [
  {
    name: "JUDr. Pavol Hlavatý",
    role: "Partner",
    specialism: "Obchodné právo, súdne spory",
    bio: "V advokácii od roku 1994. Venuje sa najmä sporovej agende a zastupovaniu spoločností pri väčších transakciách.",
    image: legal.attorney1,
  },
  {
    name: "Mgr. Eva Krajčiová",
    role: "Partnerka",
    specialism: "Nehnuteľnosti, zmluvné právo",
    bio: "Zameriava sa na developerské projekty a prevody nehnuteľností. Prednáša o katastrálnom konaní.",
    image: legal.attorney2,
  },
  {
    name: "JUDr. Martin Bednár",
    role: "Advokát",
    specialism: "Pracovné právo, insolvencia",
    bio: "Rieši pracovnoprávne spory a reštrukturalizácie. Pred advokáciou pôsobil v podnikovej právnej kancelárii.",
    image: legal.attorney3,
  },
];

const VALUES = [
  {
    title: "Vysvetlíme to zrozumiteľne",
    body: "Právnu situáciu opíšeme bez zbytočných latinizmov. Ak niečomu nerozumiete, je to naša chyba, nie vaša.",
  },
  {
    title: "Povieme aj nepríjemné veci",
    body: "Ak je váš prípad slabý, dozviete sa to na prvej konzultácii, nie po roku súdneho konania.",
  },
  {
    title: "Odmena dohodnutá vopred",
    body: "Hodinová sadzba alebo pevná cena za úkon. Pred začiatkom viete, s čím počítať.",
  },
  {
    title: "Spor až ako posledná možnosť",
    body: "Väčšinu vecí sa oplatí vyriešiť dohodou. Súd je drahý a trvá roky.",
  },
];

export default function LegalDemo() {
  return (
    <DemoShell kind="info">
      <div
        id="top"
        className="min-h-screen bg-[#FBFAF7] font-[family-name:var(--font-inter)] text-[#0F1B2D] antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[18px] font-medium tracking-[0.02em]">
              Hlavatý <span className="text-[#B08D4F]">&amp;</span> Partners
            </span>
          }
          links={NAV}
          action={{ href: "#konzultacia", label: "Konzultácia" }}
          bg="rgba(251,250,247,0.95)"
          fg="#0F1B2D"
          border="#E2DED4"
          accent="#0F1B2D"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[60vh] min-h-[400px] w-full">
            <Image
              src={legal.hero.src}
              alt={legal.hero.alt}
              fill
              priority
              sizes="100vw"
              /* The supplied photo carries another firm's signage low in the
                 frame; object-position keeps the upper facade in view. */
              style={{ objectPosition: "50% 22%" }}
              className="object-cover"
            />
            <div className="absolute inset-0 bg-[#0F1B2D]/72" />
            <div className="absolute inset-0 flex items-center">
              <div className="mx-auto w-full max-w-[1120px] px-5 md:px-8">
                <p className="mb-5 text-[12px] uppercase tracking-[0.3em] text-[#C9A96A]">
                  Advokátska kancelária · Bratislava
                </p>
                <h1 className="max-w-[18ch] font-[family-name:var(--font-space-grotesk)] text-[2.25rem] font-medium leading-[1.12] tracking-[-0.015em] text-[#FBFAF7] md:text-[3.75rem]">
                  Právne poradenstvo bez prekvapení
                </h1>
                <p className="mt-6 max-w-[48ch] text-[17px] leading-relaxed text-[#FBFAF7]/75">
                  Zastupujeme podnikateľov a súkromné osoby od roku 1998. Zrozumiteľne,
                  s odmenou dohodnutou vopred.
                </p>
                <a
                  href="#konzultacia"
                  className="mt-9 inline-flex h-12 items-center border border-[#C9A96A] bg-[#C9A96A] px-8 text-[15px] font-medium text-[#0F1B2D] transition-colors duration-150 hover:bg-transparent hover:text-[#C9A96A]"
                >
                  Dohodnúť konzultáciu
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- PRACTICE AREAS ---------- */}
        <section id="oblasti" className="mx-auto max-w-[1120px] px-5 py-20 md:px-8 md:py-28">
          <p className="text-[12px] uppercase tracking-[0.26em] text-[#B08D4F]">Špecializácia</p>
          <h2 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-medium tracking-[-0.015em] md:text-[2.5rem]">
            Oblasti práva
          </h2>

          <ul className="mt-12 grid gap-px overflow-hidden border border-[#E2DED4] bg-[#E2DED4] sm:grid-cols-2 lg:grid-cols-3">
            {PRACTICE_AREAS.map((area) => {
              const Icon = area.icon;
              return (
                <li key={area.name} className="bg-[#FBFAF7] p-7">
                  <Icon aria-hidden="true" strokeWidth={1.25} className="size-6 text-[#B08D4F]" />
                  <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[18px] font-medium">
                    {area.name}
                  </h3>
                  <p className="mt-2.5 text-[15px] leading-relaxed text-[#53606F]">{area.body}</p>
                </li>
              );
            })}
          </ul>
        </section>

        {/* ---------- TEAM ---------- */}
        <section id="tim" className="border-y border-[#E2DED4] bg-white py-20 md:py-28">
          <div className="mx-auto max-w-[1120px] px-5 md:px-8">
            <p className="text-[12px] uppercase tracking-[0.26em] text-[#B08D4F]">Tím</p>
            <h2 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-medium tracking-[-0.015em] md:text-[2.5rem]">
              Kto vás bude zastupovať
            </h2>

            <ul className="mt-12 grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
              {ATTORNEYS.map((attorney) => (
                <li key={attorney.name}>
                  <Image
                    src={attorney.image.src}
                    width={attorney.image.width}
                    height={attorney.image.height}
                    alt={attorney.image.alt}
                    loading="lazy"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    className="aspect-[4/5] w-full object-cover grayscale"
                  />
                  <h3 className="mt-5 font-[family-name:var(--font-space-grotesk)] text-[18px] font-medium">
                    {attorney.name}
                  </h3>
                  <p className="text-[14px] text-[#B08D4F]">{attorney.role}</p>
                  <p className="mt-1 text-[14px] text-[#53606F]">{attorney.specialism}</p>
                  <p className="mt-3 text-[15px] leading-relaxed text-[#53606F]">{attorney.bio}</p>
                </li>
              ))}
            </ul>

            <p className="mt-10 text-[13px] text-[#8A94A0]">
              Uvedení advokáti sú vymyslené postavy pre potreby tejto ukážky.
            </p>
          </div>
        </section>

        {/* ---------- APPROACH ---------- */}
        <section id="pristup" className="mx-auto max-w-[1120px] px-5 py-20 md:px-8 md:py-28">
          <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:gap-16">
            <div>
              <Image
                src={legal.office1.src}
                width={legal.office1.width}
                height={legal.office1.height}
                alt={legal.office1.alt}
                loading="lazy"
                sizes="(max-width: 1024px) 100vw, 45vw"
                className="w-full object-cover"
              />
            </div>

            <div>
              <p className="text-[12px] uppercase tracking-[0.26em] text-[#B08D4F]">Prístup</p>
              <h2 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-medium tracking-[-0.015em] md:text-[2.5rem]">
                Ako pracujeme
              </h2>

              <ul className="mt-9 flex flex-col">
                {VALUES.map((value) => (
                  <li key={value.title} className="border-b border-[#E2DED4] py-5 first:pt-0">
                    <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-medium">
                      {value.title}
                    </h3>
                    <p className="mt-1.5 text-[15px] leading-relaxed text-[#53606F]">
                      {value.body}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-14">
            <Image
              src={legal.office2.src}
              width={legal.office2.width}
              height={legal.office2.height}
              alt={legal.office2.alt}
              loading="lazy"
              sizes="100vw"
              className="w-full object-cover"
            />
          </div>
        </section>

        {/* ---------- FAQ ---------- */}
        <section id="otazky" className="border-y border-[#E2DED4] bg-white py-20 md:py-28">
          <div className="mx-auto max-w-[840px] px-5 md:px-8">
            <p className="text-[12px] uppercase tracking-[0.26em] text-[#B08D4F]">Otázky</p>
            <h2 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-medium tracking-[-0.015em] md:text-[2.5rem]">
              Časté otázky
            </h2>
            <div className="mt-10">
              <LegalFaq />
            </div>
          </div>
        </section>

        {/* ---------- CONSULTATION ---------- */}
        <section id="konzultacia" className="bg-[#0F1B2D] py-20 text-[#FBFAF7] md:py-28">
          <div className="mx-auto max-w-[1120px] px-5 md:px-8">
            <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
              <div>
                <p className="text-[12px] uppercase tracking-[0.26em] text-[#C9A96A]">Kontakt</p>
                <h2 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-medium tracking-[-0.015em] md:text-[2.5rem]">
                  Dohodnite si konzultáciu
                </h2>
                <p className="mt-5 max-w-[46ch] text-[16px] leading-relaxed text-[#FBFAF7]/70">
                  Prvá konzultácia trvá 45 minút a stojí 60 €. Ak sa následne rozhodnete pre
                  zastupovanie, túto sumu odrátame z prvej faktúry.
                </p>

                <dl className="mt-10 flex flex-col gap-5 text-[15px]">
                  {[
                    { k: "Adresa", v: "Panská 21, 811 01 Bratislava" },
                    { k: "Telefón", v: "+421 900 000 000" },
                    { k: "E-mail", v: "kancelaria@hlavatypartners.example" },
                    { k: "Úradné hodiny", v: "Pondelok – Piatok, 9:00 – 17:00" },
                  ].map((row) => (
                    <div key={row.k} className="border-b border-[#FBFAF7]/12 pb-4">
                      <dt className="text-[12px] uppercase tracking-[0.16em] text-[#C9A96A]">
                        {row.k}
                      </dt>
                      <dd className="mt-1">{row.v}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <ConsultationForm areas={PRACTICE_AREAS.map((area) => area.name)} />
            </div>
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="bg-[#0A1422] py-10 text-[#FBFAF7]/50">
          <div className="mx-auto flex max-w-[1120px] flex-col gap-3 px-5 text-[14px] md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[15px] text-[#FBFAF7]">
              Hlavatý &amp; Partners
            </p>
            <p>Vymyslená kancelária. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
