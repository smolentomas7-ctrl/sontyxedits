import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Check } from "lucide-react";
import { DemoShell } from "@/components/demo/DemoShell";
import { PropertyGallery } from "./PropertyGallery";
import { ViewingForm } from "../../ViewingForm";
import { MortgageCalculator } from "../../MortgageCalculator";
import {
  properties,
  getProperty,
  priceLabel,
  TYPE_LABELS,
  DEAL_LABELS,
  AGENTS,
} from "../../data";

export const metadata: Metadata = {
  title: "Nehnuteľnosť — Domov Reality demo",
  robots: { index: false, follow: false },
};

export function generateStaticParams() {
  return properties.map((property) => ({ slug: property.slug }));
}

export default async function PropertyPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const property = getProperty(slug);
  if (!property) notFound();

  const images = [property.main, ...property.gallery];
  const agent = AGENTS[0];

  const specs: { k: string; v: string }[] = [
    { k: "Druh", v: TYPE_LABELS[property.type] },
    { k: "Typ ponuky", v: DEAL_LABELS[property.deal] },
    { k: "Počet izieb", v: String(property.rooms) },
    { k: "Úžitková plocha", v: `${property.area} m²` },
    ...(property.landArea ? [{ k: "Pozemok", v: `${property.landArea} m²` }] : []),
    { k: "Rok výstavby", v: String(property.year) },
    { k: "Energetická trieda", v: property.energy },
    { k: "Lokalita", v: `${property.location}, ${property.city}` },
  ];

  return (
    <DemoShell kind="info">
      <div className="min-h-screen bg-[#F7F9FB] font-[family-name:var(--font-inter)] text-[#0E2A47] antialiased">
        <div className="mx-auto max-w-[1240px] px-5 py-10 md:px-8 md:py-14">
          <Link
            href="/demo/estate#ponuka"
            className="inline-flex items-center gap-1.5 text-[14px] text-[#5B6977] transition-colors duration-150 hover:text-[#17457A]"
          >
            <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-4" />
            Späť na ponuku
          </Link>

          <header className="mt-6 flex flex-wrap items-start justify-between gap-5">
            <div>
              <span
                className="inline-block rounded px-2.5 py-1 text-[12px] font-bold text-white"
                style={{ background: property.deal === "predaj" ? "#17457A" : "#1F9D64" }}
              >
                {DEAL_LABELS[property.deal]}
              </span>
              <h1 className="mt-3 font-[family-name:var(--font-space-grotesk)] text-[1.875rem] font-bold tracking-[-0.025em] md:text-[2.5rem]">
                {property.title}
              </h1>
              <p className="mt-1.5 text-[16px] text-[#5B6977]">
                {property.location}, {property.city}
              </p>
            </div>

            <p className="font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold text-[#17457A] md:text-[2.25rem]">
              {priceLabel(property)}
            </p>
          </header>

          <div className="mt-8">
            <PropertyGallery images={images} title={property.title} />
          </div>

          <div className="mt-12 grid gap-10 lg:grid-cols-[1.4fr_1fr] lg:gap-14">
            <div>
              <section>
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                  Popis
                </h2>
                <p className="mt-3 max-w-[68ch] text-[16px] leading-relaxed text-[#4A5A69]">
                  {property.description}
                </p>
              </section>

              <section className="mt-10">
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                  Parametre
                </h2>
                <dl className="mt-4 grid gap-px overflow-hidden rounded-xl border border-[#D9E0E8] bg-[#D9E0E8] sm:grid-cols-2">
                  {specs.map((spec) => (
                    <div
                      key={spec.k}
                      className="flex items-baseline justify-between gap-4 bg-white px-5 py-3.5"
                    >
                      <dt className="text-[14px] text-[#5B6977]">{spec.k}</dt>
                      <dd className="text-right text-[15px] font-medium">{spec.v}</dd>
                    </div>
                  ))}
                </dl>
              </section>

              <section className="mt-10">
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                  Čo nehnuteľnosť ponúka
                </h2>
                <ul className="mt-4 grid gap-2.5 sm:grid-cols-2">
                  {property.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-start gap-2.5 text-[15px] text-[#4A5A69]"
                    >
                      <Check
                        aria-hidden="true"
                        strokeWidth={2}
                        className="mt-0.5 size-4 shrink-0 text-[#1F9D64]"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </section>

              <section className="mt-10">
                <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
                  Poloha
                </h2>
                <div
                  role="img"
                  aria-label="Zástupný blok namiesto mapy s polohou nehnuteľnosti"
                  className="mt-4 flex h-[260px] items-center justify-center rounded-xl border-2 border-dashed border-[#C6D2DE] bg-[#EEF3F8] text-center"
                >
                  <p className="max-w-[40ch] px-6 text-[14px] leading-relaxed text-[#5B6977]">
                    Miesto pre mapu. V ukážke ju nevkladáme, pretože Google Maps vyžaduje
                    API kľúč a fakturačný účet.
                  </p>
                </div>
              </section>
            </div>

            <aside className="flex flex-col gap-8 lg:sticky lg:top-40 lg:self-start">
              <div className="rounded-xl border border-[#D9E0E8] bg-white p-6">
                <p className="text-[13px] uppercase tracking-[0.1em] text-[#8A98A6]">
                  Kontaktná osoba
                </p>
                <p className="mt-2 font-[family-name:var(--font-space-grotesk)] text-lg font-bold">
                  {agent.name}
                </p>
                <p className="text-[14px] text-[#1F9D64]">{agent.role}</p>
                <p className="mt-3 text-[14px] text-[#5B6977]">{agent.phone}</p>
                <p className="break-all text-[14px] text-[#5B6977]">{agent.email}</p>
              </div>

              <ViewingForm propertyTitle={property.title} />
            </aside>
          </div>

          <section className="mt-16">
            <MortgageCalculator
              defaultPrice={property.deal === "prenajom" ? 450000 : property.price}
            />
          </section>
        </div>

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
