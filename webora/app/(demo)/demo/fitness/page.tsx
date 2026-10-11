import type { Metadata } from "next";
import Image from "next/image";
import { Check, Info } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { DemoNav } from "@/components/demo/DemoNav";
import { BookingFlow } from "./BookingFlow";
import { fitness } from "@/config/images";
import { CLASSES, TRAINERS, MEMBERSHIPS, SLOTS_BY_WEEKDAY, WEEKDAYS } from "./data";

export const metadata: Metadata = {
  title: "Pulse Studio — demo",
  robots: { index: false, follow: false },
};

const NAV = [
  { href: "#hodiny", label: "Hodiny" },
  { href: "#rozvrh", label: "Rozvrh" },
  { href: "#treneri", label: "Tréneri" },
  { href: "#clenske", label: "Členské" },
  { href: "#rezervacia", label: "Rezervácia" },
];

export default function FitnessDemo() {
  return (
    <DemoShell pkg="business">
      <div
        id="top"
        className="min-h-screen bg-[#0C0C0E] font-[family-name:var(--font-inter)] text-white antialiased"
      >
        <DemoNav
          brand={
            <span className="font-[family-name:var(--font-space-grotesk)] text-[19px] font-bold uppercase tracking-[0.08em]">
              Pulse<span className="text-[#FF6B1A]">.</span>
            </span>
          }
          links={NAV}
          action={{ href: "#rezervacia", label: "Rezervovať" }}
          bg="rgba(12,12,14,0.92)"
          fg="#FFFFFF"
          border="rgba(255,255,255,0.1)"
          accent="#FF6B1A"
        />

        {/* ---------- HERO ---------- */}
        <section className="relative">
          <div className="relative h-[76vh] min-h-[480px] w-full">
            <Image
              src={fitness.hero.src}
              alt={fitness.hero.alt}
              fill
              priority
              sizes="100vw"
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0C0C0E] via-[#0C0C0E]/70 to-[#0C0C0E]/35" />

            <div className="absolute inset-0 flex items-center">
              <div className="mx-auto w-full max-w-[1200px] px-5 md:px-8">
                <p className="mb-4 text-[12px] font-bold uppercase tracking-[0.26em] text-[#FF6B1A]">
                  Bratislava · Otvorené 6:00 – 22:00
                </p>
                <h1 className="max-w-[13ch] font-[family-name:var(--font-space-grotesk)] text-[2.75rem] font-bold uppercase leading-[0.95] tracking-[-0.03em] md:text-[5.5rem]">
                  Prestaň to odkladať
                </h1>
                <p className="mt-6 max-w-[44ch] text-[17px] leading-relaxed text-white/75">
                  Štyri typy hodín, traja tréneri a rozvrh, ktorý sa dá stihnúť pred prácou aj po
                  nej. Prvá hodina je zadarmo.
                </p>
                <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                  <a
                    href="#rezervacia"
                    className="inline-flex items-center justify-center rounded-lg bg-[#FF6B1A] px-8 py-4 font-bold uppercase tracking-wide text-[#0C0C0E] transition-colors duration-150 hover:bg-[#FF8440]"
                  >
                    Rezervovať hodinu
                  </a>
                  <a
                    href="#rozvrh"
                    className="inline-flex items-center justify-center rounded-lg border border-white/45 bg-[#0C0C0E]/88 px-8 py-4 font-bold uppercase tracking-wide text-white backdrop-blur-sm transition-colors duration-150 hover:bg-[#0C0C0E]"
                  >
                    Pozrieť rozvrh
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ---------- CLASSES ---------- */}
        <section id="hodiny" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
            Hodiny
          </h2>
          <p className="mt-3 max-w-[52ch] text-[16px] text-white/60">
            Žiadne dvadsať druhov lekcií. Štyri, ktoré vieme robiť poriadne.
          </p>

          <ul className="mt-12 grid gap-6 sm:grid-cols-2">
            {CLASSES.map((item) => (
              <li
                key={item.id}
                className="overflow-hidden rounded-2xl border border-white/10 bg-[#141416]"
              >
                <div className="relative aspect-[3/2]">
                  <Image
                    src={item.image.src}
                    alt={item.image.alt}
                    fill
                    loading="lazy"
                    sizes="(max-width: 640px) 100vw, 50vw"
                    className="object-cover"
                  />
                  <span className="absolute left-4 top-4 rounded-full bg-[#FF6B1A] px-3 py-1 text-[12px] font-bold uppercase tracking-wide text-[#0C0C0E]">
                    {item.duration} min
                  </span>
                </div>
                <div className="p-6">
                  <div className="flex items-baseline justify-between gap-4">
                    <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase">
                      {item.name}
                    </h3>
                    <span className="shrink-0 text-[13px] text-white/50">{item.level}</span>
                  </div>
                  <p className="mt-2.5 text-[15px] leading-relaxed text-white/65">
                    {item.description}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* ---------- TIMETABLE ---------- */}
        <section id="rozvrh" className="border-y border-white/10 bg-[#141416] py-20 md:py-28">
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
              Týždenný rozvrh
            </h2>
            <p className="mt-3 flex items-center gap-2 text-[15px] text-white/60">
              <Info aria-hidden="true" strokeWidth={1.5} className="size-4 shrink-0" />
              Vzorový rozvrh — v ukážke sa každý týždeň opakuje rovnako.
            </p>

            {/* Horizontal scroll on narrow screens rather than a cramped grid. */}
            <div className="no-scrollbar mt-10 overflow-x-auto">
              <div className="grid min-w-[840px] grid-cols-7 gap-3">
                {WEEKDAYS.map((day) => {
                  const slots = SLOTS_BY_WEEKDAY[day.index] ?? [];
                  return (
                    <div key={day.index}>
                      <h3 className="mb-3 border-b border-white/12 pb-2.5 text-[13px] font-bold uppercase tracking-[0.1em] text-white/70">
                        {day.label}
                      </h3>
                      <ul className="flex flex-col gap-2">
                        {slots.length === 0 ? (
                          <li className="rounded-lg border border-dashed border-white/10 px-3 py-4 text-center text-[12px] text-white/30">
                            Zatvorené
                          </li>
                        ) : (
                          slots.map((slot) => {
                            const gymClass = CLASSES.find((c) => c.id === slot.classId);
                            return (
                              <li
                                key={`${slot.classId}-${slot.time}`}
                                className="rounded-lg border px-3 py-2.5"
                                style={{
                                  borderColor: slot.full
                                    ? "rgba(255,255,255,0.06)"
                                    : "rgba(255,107,26,0.3)",
                                  background: slot.full
                                    ? "rgba(255,255,255,0.02)"
                                    : "rgba(255,107,26,0.08)",
                                  opacity: slot.full ? 0.5 : 1,
                                }}
                              >
                                <span className="block font-[family-name:var(--font-space-grotesk)] text-[15px] font-bold">
                                  {slot.time}
                                </span>
                                <span className="block text-[12px] text-white/65">
                                  {gymClass?.name}
                                </span>
                                <span className="mt-0.5 block text-[11px] text-white/45">
                                  {slot.full ? "Obsadené" : `${slot.free} voľných`}
                                </span>
                              </li>
                            );
                          })
                        )}
                      </ul>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* ---------- TRAINERS ---------- */}
        <section id="treneri" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
            Tréneri
          </h2>

          <ul className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {TRAINERS.map((trainer) => (
              <li key={trainer.name}>
                <div className="overflow-hidden rounded-2xl">
                  <Image
                    src={trainer.image.src}
                    width={trainer.image.width}
                    height={trainer.image.height}
                    alt={trainer.image.alt}
                    loading="lazy"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    className="aspect-[4/5] w-full object-cover"
                  />
                </div>
                <h3 className="mt-4 font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase">
                  {trainer.name}
                </h3>
                <p className="text-[14px] font-medium text-[#FF6B1A]">{trainer.role}</p>
                <p className="mt-2 text-[15px] leading-relaxed text-white/60">{trainer.bio}</p>
              </li>
            ))}
          </ul>
          <p className="mt-8 text-[13px] text-white/35">
            Tréneri sú vymyslené postavy pre potreby tejto ukážky.
          </p>
        </section>

        {/* ---------- MEMBERSHIPS ---------- */}
        <section id="clenske" className="border-y border-white/10 bg-[#141416] py-20 md:py-28">
          <div className="mx-auto max-w-[1200px] px-5 md:px-8">
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
              Členské
            </h2>

            <ul className="mt-12 grid gap-6 lg:grid-cols-3">
              {MEMBERSHIPS.map((plan) => (
                <li
                  key={plan.name}
                  className="relative flex flex-col rounded-2xl border bg-[#0C0C0E] p-7"
                  style={{
                    borderColor: plan.popular ? "#FF6B1A" : "rgba(255,255,255,0.1)",
                  }}
                >
                  {plan.popular ? (
                    <span className="absolute -top-3 left-7 rounded-full bg-[#FF6B1A] px-3 py-1 text-[11px] font-bold uppercase tracking-wide text-[#0C0C0E]">
                      Najobľúbenejšie
                    </span>
                  ) : null}

                  <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold uppercase">
                    {plan.name}
                  </h3>
                  <p className="mt-3 font-[family-name:var(--font-space-grotesk)] text-4xl font-bold text-[#FF6B1A]">
                    {plan.price}
                  </p>
                  <p className="text-[14px] text-white/50">{plan.period}</p>

                  <ul className="mt-6 flex flex-1 flex-col gap-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2.5 text-[15px] text-white/70">
                        <Check
                          aria-hidden="true"
                          strokeWidth={2}
                          className="mt-0.5 size-4 shrink-0 text-[#FF6B1A]"
                        />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <a
                    href="#rezervacia"
                    className="mt-7 inline-flex h-12 items-center justify-center rounded-lg font-bold uppercase tracking-wide transition-colors duration-150"
                    style={
                      plan.popular
                        ? { background: "#FF6B1A", color: "#0C0C0E" }
                        : { border: "1px solid rgba(255,255,255,0.2)", color: "#FFFFFF" }
                    }
                  >
                    Vybrať
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ---------- BOOKING ---------- */}
        <section id="rezervacia" className="mx-auto max-w-[1200px] px-5 py-20 md:px-8 md:py-28">
          <div className="grid gap-10 lg:grid-cols-[1fr_1.1fr] lg:gap-16">
            <div>
              <h2 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold uppercase tracking-[-0.02em] md:text-[3rem]">
                Rezervácia
              </h2>
              <p className="mt-4 max-w-[44ch] text-[16px] leading-relaxed text-white/65">
                Vyberte hodinu, dátum a čas. Rezervácia trvá menej než minútu a dá sa zrušiť do
                štyroch hodín pred začiatkom.
              </p>
              <div className="mt-7 flex gap-3 rounded-xl border border-white/10 bg-white/4 p-5">
                <Info
                  aria-hidden="true"
                  strokeWidth={1.5}
                  className="mt-0.5 size-5 shrink-0 text-[#FF6B1A]"
                />
                <p className="text-[14px] leading-relaxed text-white/60">
                  Časy pochádzajú zo statických ukážkových dát, nie zo skutočného kalendára.
                  Niektoré sú zámerne označené ako obsadené, aby bolo vidieť, ako sa správajú.
                </p>
              </div>
            </div>

            <BookingFlow />
          </div>
        </section>

        {/* ---------- FOOTER ---------- */}
        <footer className="border-t border-white/10 bg-[#0C0C0E] py-10">
          <div className="mx-auto flex max-w-[1200px] flex-col gap-3 px-5 text-[14px] text-white/45 md:flex-row md:items-center md:justify-between md:px-8">
            <p className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold uppercase tracking-[0.08em] text-white">
              Pulse Studio
            </p>
            <p>Vymyslené štúdio. Ukážkový web vytvorilo štúdio Webora.</p>
          </div>
        </footer>
      </div>
    </DemoShell>
  );
}
