"use client";

import { useState } from "react";
import Image from "next/image";
import { bistro } from "@/config/images";

type Item = { name: string; description: string; price: string; image?: typeof bistro.menu1 };

const CATEGORIES = [
  { id: "predjedla", label: "Predjedlá" },
  { id: "hlavne", label: "Hlavné jedlá" },
  { id: "dezerty", label: "Dezerty" },
  { id: "napoje", label: "Nápoje" },
] as const;

type CategoryId = (typeof CATEGORIES)[number]["id"];

const MENU: Record<CategoryId, Item[]> = {
  predjedla: [
    {
      name: "Avokádový toast",
      description: "Kváskový chlieb, zastreté vajce, reďkovka, chilli vločky",
      price: "8,90 €",
      image: bistro.menu2,
    },
    {
      name: "Šalát z pečenej zeleniny",
      description: "Cvikla, mrkva, cícer, tahini dresing, granátové jablko",
      price: "9,50 €",
      image: bistro.menu3,
    },
    {
      name: "Polievka dňa",
      description: "Pýtajte sa obsluhy. Vždy jedna mäsová a jedna vegánska",
      price: "5,20 €",
    },
    {
      name: "Domáca paštéta",
      description: "Kuracia pečeň, cibuľový džem, hrianka",
      price: "7,40 €",
    },
  ],
  hlavne: [
    {
      name: "Pečený losos",
      description: "Hráškové pyré, chrumkavá zelenina, citrónové maslo",
      price: "18,90 €",
      image: bistro.menu4,
    },
    {
      name: "Hovädzí burger",
      description: "180 g, zrejúci čedar, karamelizovaná cibuľa, hranolky",
      price: "14,50 €",
    },
    {
      name: "Hubové rizoto",
      description: "Sezónne huby, parmezán, petržlenový olej",
      price: "13,20 €",
    },
    {
      name: "Konfitované kačacie stehno",
      description: "Dusená kapusta, zemiakový knedlík",
      price: "17,80 €",
    },
  ],
  dezerty: [
    {
      name: "Lístkové pečivo s lesným ovocím",
      description: "Pečené ráno, kým sa neminie",
      price: "4,60 €",
      image: bistro.menu1,
    },
    {
      name: "Čokoládový fondant",
      description: "Horká čokoláda 70 %, vanilková zmrzlina",
      price: "6,80 €",
    },
    {
      name: "Tvarohový koláč",
      description: "Podľa receptu, ktorý sme nezmenili od otvorenia",
      price: "5,40 €",
    },
  ],
  napoje: [
    {
      name: "Cappuccino",
      description: "Vlastná praženica, mlieko z rodinnej farmy",
      price: "3,20 €",
      image: bistro.menu5,
    },
    {
      name: "Filtrovaná káva",
      description: "Jednodruhová, ponuka sa mení týždenne",
      price: "3,60 €",
    },
    {
      name: "Negroni",
      description: "Gin, Campari, červený vermút, pomarančová kôra",
      price: "9,00 €",
      image: bistro.menu6,
    },
    {
      name: "Domáca limonáda",
      description: "Bazový kvet alebo zázvor a limetka",
      price: "4,20 €",
    },
  ],
};

export function BistroMenu() {
  const [active, setActive] = useState<CategoryId>("predjedla");

  return (
    <div>
      {/* Tab list follows the WAI-ARIA tabs pattern: arrow keys are handled by
          the browser's default focus order here, and each tab controls one panel. */}
      <div role="tablist" aria-label="Kategórie menu" className="flex flex-wrap justify-center gap-2">
        {CATEGORIES.map((category) => {
          const selected = category.id === active;
          return (
            <button
              key={category.id}
              role="tab"
              id={`tab-${category.id}`}
              aria-selected={selected}
              aria-controls={`panel-${category.id}`}
              tabIndex={selected ? 0 : -1}
              onClick={() => setActive(category.id)}
              onKeyDown={(event) => {
                const index = CATEGORIES.findIndex((c) => c.id === active);
                if (event.key === "ArrowRight") {
                  event.preventDefault();
                  const next = CATEGORIES[(index + 1) % CATEGORIES.length];
                  setActive(next.id);
                  document.getElementById(`tab-${next.id}`)?.focus();
                }
                if (event.key === "ArrowLeft") {
                  event.preventDefault();
                  const prev = CATEGORIES[(index - 1 + CATEGORIES.length) % CATEGORIES.length];
                  setActive(prev.id);
                  document.getElementById(`tab-${prev.id}`)?.focus();
                }
              }}
              className="rounded-full border px-5 py-2.5 text-[15px] transition-colors duration-150"
              style={
                selected
                  ? { background: "#1F3D2F", borderColor: "#1F3D2F", color: "#FAF7F2" }
                  : { background: "transparent", borderColor: "#D9CFBE", color: "#4A5D52" }
              }
            >
              {category.label}
            </button>
          );
        })}
      </div>

      {CATEGORIES.map((category) => (
        <div
          key={category.id}
          role="tabpanel"
          id={`panel-${category.id}`}
          aria-labelledby={`tab-${category.id}`}
          hidden={category.id !== active}
          className="mt-10"
        >
          <ul className="grid gap-5 md:grid-cols-2">
            {MENU[category.id].map((item) => (
              <li
                key={item.name}
                className="flex items-center gap-4 rounded-xl border border-[#E3DACB] bg-[#FAF7F2] p-4"
              >
                {item.image ? (
                  <Image
                    src={item.image.src}
                    width={item.image.width}
                    height={item.image.height}
                    alt={item.image.alt}
                    loading="lazy"
                    sizes="88px"
                    className="size-[88px] shrink-0 rounded-lg object-cover"
                  />
                ) : (
                  <div
                    aria-hidden="true"
                    className="flex size-[88px] shrink-0 items-center justify-center rounded-lg bg-[#EFE7DA] font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#C4653A]"
                  >
                    {item.name.charAt(0)}
                  </div>
                )}

                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline justify-between gap-3">
                    <h3 className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-bold text-[#1F3D2F]">
                      {item.name}
                    </h3>
                    <span className="shrink-0 font-medium text-[#C4653A]">{item.price}</span>
                  </div>
                  <p className="mt-1 text-[14px] leading-relaxed text-[#6B7A71]">
                    {item.description}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
