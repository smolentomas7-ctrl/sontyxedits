"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import { Lightbox, type LightboxItem } from "@/components/ui/Lightbox";
import { lens } from "@/config/images";
import type { ImageSlot } from "@/config/images";

type CategoryId = "all" | "portret" | "svadba" | "produkt" | "krajina";

const CATEGORIES: { id: CategoryId; label: string }[] = [
  { id: "all", label: "Všetko" },
  { id: "portret", label: "Portrét" },
  { id: "svadba", label: "Svadba" },
  { id: "produkt", label: "Produkt" },
  { id: "krajina", label: "Krajina" },
];

type Shot = { image: ImageSlot; category: Exclude<CategoryId, "all">; caption: string };

const SHOTS: Shot[] = [
  { image: lens.portrait1, category: "portret", caption: "Editoriál — Metal" },
  { image: lens.portrait2, category: "portret", caption: "Štúdia charakteru" },
  { image: lens.portrait3, category: "portret", caption: "Leto na lúke" },
  { image: lens.wedding1, category: "svadba", caption: "Hostina — Anna a Tomáš" },
  { image: lens.wedding2, category: "svadba", caption: "Obrad v katedrále" },
  { image: lens.wedding3, category: "svadba", caption: "Detail — prstene" },
  { image: lens.product1, category: "produkt", caption: "Hodinky — skeleton" },
  { image: lens.product2, category: "produkt", caption: "Audio — betón a tieň" },
  { image: lens.product3, category: "produkt", caption: "Patisserie" },
  { image: lens.landscape1, category: "krajina", caption: "Pobrežie za súmraku" },
  { image: lens.landscape2, category: "krajina", caption: "Duny" },
  { image: lens.landscape3, category: "krajina", caption: "Hmla v bukovom lese" },
];

export function Gallery() {
  const [filter, setFilter] = useState<CategoryId>("all");
  const [index, setIndex] = useState<number | null>(null);

  const visible = useMemo(
    () => (filter === "all" ? SHOTS : SHOTS.filter((shot) => shot.category === filter)),
    [filter],
  );

  /** The lightbox walks the currently filtered set, so prev/next match what
   *  the visitor can see in the grid. */
  const items: LightboxItem[] = useMemo(
    () =>
      visible.map((shot) => ({
        src: shot.image.src,
        width: shot.image.width,
        height: shot.image.height,
        alt: shot.image.alt,
        title: shot.caption,
      })),
    [visible],
  );

  return (
    <>
      <div role="group" aria-label="Filtrovať podľa kategórie" className="flex flex-wrap gap-6">
        {CATEGORIES.map((category) => {
          const active = category.id === filter;
          return (
            <button
              key={category.id}
              type="button"
              onClick={() => {
                setFilter(category.id);
                setIndex(null);
              }}
              aria-pressed={active}
              className="border-b pb-1 text-[13px] uppercase tracking-[0.2em] transition-colors duration-150"
              style={{
                // 0.55 rather than 0.4: the inactive filters are still text
                // a visitor has to read to choose one.
                color: active ? "#FFFFFF" : "rgba(255,255,255,0.55)",
                borderColor: active ? "#FFFFFF" : "transparent",
              }}
            >
              {category.label}
            </button>
          );
        })}
      </div>

      {/* CSS columns give a true masonry flow for mixed orientations without
          measuring anything in JS. */}
      <div className="mt-12 gap-4 [column-count:1] sm:[column-count:2] lg:[column-count:3]">
        {visible.map((shot, position) => (
          <button
            key={shot.image.src}
            type="button"
            onClick={() => setIndex(position)}
            aria-label={`Zväčšiť: ${shot.caption}`}
            className="group mb-4 block w-full break-inside-avoid overflow-hidden"
          >
            <span className="relative block overflow-hidden">
              <Image
                src={shot.image.src}
                width={shot.image.width}
                height={shot.image.height}
                alt={shot.image.alt}
                loading="lazy"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
              />
              <span className="absolute inset-0 bg-black/0 transition-colors duration-300 group-hover:bg-black/25" />
              <span className="absolute bottom-0 left-0 right-0 translate-y-2 p-4 text-left text-[13px] uppercase tracking-[0.14em] text-white opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100">
                {shot.caption}
              </span>
            </span>
          </button>
        ))}
      </div>

      {visible.length === 0 ? (
        <p className="mt-12 text-center text-white/55">V tejto kategórii zatiaľ nič nie je.</p>
      ) : null}

      <Lightbox
        items={items}
        index={index}
        onClose={() => setIndex(null)}
        onIndexChange={setIndex}
        label="Fotografia"
        counterWord="z"
        closeLabel="Zavrieť"
        prevLabel="Predchádzajúca"
        nextLabel="Ďalšia"
      />
    </>
  );
}
