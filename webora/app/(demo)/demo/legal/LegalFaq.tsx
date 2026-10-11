"use client";

import { useId, useState } from "react";
import { Plus } from "lucide-react";

const FAQ = [
  {
    q: "Koľko stojí prvá konzultácia?",
    a: "45 minút za 60 €. Ak sa následne rozhodnete pre zastupovanie, sumu odrátame z prvej faktúry. Na konzultáciu si prineste všetky dokumenty, ktoré sa veci týkajú — ušetrí to čas aj peniaze.",
  },
  {
    q: "Ako si účtujete odmenu?",
    a: "Buď hodinovou sadzbou, alebo pevnou cenou za konkrétny úkon. Pri sporoch sa niekedy dohodneme na kombinácii nižšej hodinovej sadzby a podielu na úspechu. Spôsob odmeny vždy dohodneme písomne pred začatím práce.",
  },
  {
    q: "Ako dlho trvá súdny spor?",
    a: "Na prvom stupni spravidla 12 až 24 mesiacov, pri zložitejších veciach dlhšie. Ak sa odvolá protistrana, počítajte s ďalším rokom. Preto pri väčšine sporov najprv skúšame dohodu.",
  },
  {
    q: "Zastupujete aj mimo Bratislavy?",
    a: "Áno, pred súdmi po celom Slovensku. Cestovné náklady a čas strávený cestovaním účtujeme zníženou sadzbou a vždy ich uvádzame vopred.",
  },
  {
    q: "Čo si mám priniesť na stretnutie?",
    a: "Zmluvy, faktúry, korešpondenciu s protistranou a akékoľvek rozhodnutia alebo výzvy, ktoré ste dostali. Pokojne aj v neusporiadanom stave — roztriedime to spolu.",
  },
  {
    q: "Je naša komunikácia dôverná?",
    a: "Áno. Advokát je viazaný mlčanlivosťou podľa zákona o advokácii a tejto povinnosti ho môžete zbaviť iba vy. Mlčanlivosť platí aj vtedy, ak sa napokon pre naše služby nerozhodnete.",
  },
];

export function LegalFaq() {
  const [open, setOpen] = useState<number | null>(0);
  const baseId = useId();

  return (
    <div className="border-t border-[#E2DED4]">
      {FAQ.map((item, index) => {
        const isOpen = open === index;
        const buttonId = `${baseId}-t-${index}`;
        const panelId = `${baseId}-p-${index}`;

        return (
          <div key={item.q} className="border-b border-[#E2DED4]">
            <h3>
              <button
                type="button"
                id={buttonId}
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpen(isOpen ? null : index)}
                className="flex w-full items-center justify-between gap-6 py-5 text-left transition-colors duration-150 hover:text-[#B08D4F]"
              >
                <span className="font-[family-name:var(--font-space-grotesk)] text-[17px] font-medium">
                  {item.q}
                </span>
                <Plus
                  aria-hidden="true"
                  strokeWidth={1.25}
                  className="size-5 shrink-0 text-[#B08D4F] transition-transform duration-200"
                  style={{ transform: isOpen ? "rotate(45deg)" : "none" }}
                />
              </button>
            </h3>
            <div
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              className="grid transition-[grid-template-rows,visibility] duration-200 ease-out"
              style={{
                gridTemplateRows: isOpen ? "1fr" : "0fr",
                visibility: isOpen ? "visible" : "hidden",
              }}
            >
              <div className="overflow-hidden">
                <p className="max-w-[68ch] pb-6 pr-8 text-[15px] leading-relaxed text-[#53606F]">
                  {item.a}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
