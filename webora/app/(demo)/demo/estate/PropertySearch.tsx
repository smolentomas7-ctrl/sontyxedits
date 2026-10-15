"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { BedDouble, Maximize, MapPin, Search } from "lucide-react";
import {
  properties,
  TYPE_LABELS,
  DEAL_LABELS,
  priceLabel,
  type Deal,
  type PropertyType,
} from "./data";

type SortKey = "newest" | "price-asc" | "price-desc" | "area-desc";

const SORTS: { id: SortKey; label: string }[] = [
  { id: "newest", label: "Najnovšie" },
  { id: "price-asc", label: "Cena: od najnižšej" },
  { id: "price-desc", label: "Cena: od najvyššej" },
  { id: "area-desc", label: "Najväčšia plocha" },
];

const MAX_PRICE = 900000;

export function PropertySearch() {
  const [query, setQuery] = useState("");
  const [deal, setDeal] = useState<Deal | "all">("all");
  const [type, setType] = useState<PropertyType | "all">("all");
  const [minRooms, setMinRooms] = useState(0);
  const [maxPrice, setMaxPrice] = useState(MAX_PRICE);
  const [sort, setSort] = useState<SortKey>("newest");

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();

    const filtered = properties.filter((property) => {
      const matchesQuery =
        needle === "" ||
        property.city.toLowerCase().includes(needle) ||
        property.location.toLowerCase().includes(needle) ||
        property.title.toLowerCase().includes(needle);
      const matchesDeal = deal === "all" || property.deal === deal;
      const matchesType = type === "all" || property.type === type;
      const matchesRooms = property.rooms >= minRooms;
      // Rentals are priced per month, so the price ceiling only gates sales.
      const matchesPrice = property.deal === "prenajom" || property.price <= maxPrice;
      return matchesQuery && matchesDeal && matchesType && matchesRooms && matchesPrice;
    });

    const sorted = [...filtered];
    if (sort === "price-asc") sorted.sort((a, b) => a.price - b.price);
    if (sort === "price-desc") sorted.sort((a, b) => b.price - a.price);
    if (sort === "area-desc") sorted.sort((a, b) => b.area - a.area);
    if (sort === "newest") sorted.sort((a, b) => b.year - a.year);
    return sorted;
  }, [query, deal, type, minRooms, maxPrice, sort]);

  function reset() {
    setQuery("");
    setDeal("all");
    setType("all");
    setMinRooms(0);
    setMaxPrice(MAX_PRICE);
  }

  const hasFilters =
    query !== "" || deal !== "all" || type !== "all" || minRooms > 0 || maxPrice < MAX_PRICE;

  return (
    <>
      {/* ---------- search bar ---------- */}
      <div className="rounded-xl border border-[#D9E0E8] bg-white p-5 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-[1.6fr_1fr_1fr_auto]">
          <div>
            <label htmlFor="q" className="mb-1.5 block text-[13px] font-medium text-[#5B6977]">
              Lokalita
            </label>
            <div className="relative">
              <Search
                aria-hidden="true"
                strokeWidth={1.5}
                className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-[#637383]"
              />
              <input
                id="q"
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Mesto alebo štvrť"
                className="h-11 w-full rounded-lg border border-[#D9E0E8] pl-10 pr-3 text-[15px] focus:border-[#17457A] focus:outline-none focus:ring-2 focus:ring-[#17457A]/20"
              />
            </div>
          </div>

          <div>
            <label htmlFor="deal" className="mb-1.5 block text-[13px] font-medium text-[#5B6977]">
              Typ ponuky
            </label>
            <select
              id="deal"
              value={deal}
              onChange={(event) => setDeal(event.target.value as Deal | "all")}
              className="h-11 w-full rounded-lg border border-[#D9E0E8] px-3 text-[15px] focus:border-[#17457A] focus:outline-none"
            >
              <option value="all">Všetko</option>
              <option value="predaj">Na predaj</option>
              <option value="prenajom">Na prenájom</option>
            </select>
          </div>

          <div>
            <label htmlFor="type" className="mb-1.5 block text-[13px] font-medium text-[#5B6977]">
              Druh
            </label>
            <select
              id="type"
              value={type}
              onChange={(event) => setType(event.target.value as PropertyType | "all")}
              className="h-11 w-full rounded-lg border border-[#D9E0E8] px-3 text-[15px] focus:border-[#17457A] focus:outline-none"
            >
              <option value="all">Všetko</option>
              <option value="dom">Dom</option>
              <option value="byt">Byt</option>
              <option value="chata">Chata</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={reset}
              disabled={!hasFilters}
              className="h-11 rounded-lg border border-[#D9E0E8] px-5 text-[14px] font-medium text-[#17457A] transition-colors duration-150 hover:bg-[#F3F7FB] disabled:opacity-40"
            >
              Zrušiť
            </button>
          </div>
        </div>

        <div className="mt-5 grid gap-5 border-t border-[#EDF1F5] pt-5 sm:grid-cols-2">
          <div>
            <label
              htmlFor="rooms"
              className="mb-1.5 flex items-baseline justify-between text-[13px] font-medium text-[#5B6977]"
            >
              Izby od
              <span className="font-bold text-[#17457A]">{minRooms === 0 ? "ľubovoľne" : `${minRooms}+`}</span>
            </label>
            <input
              id="rooms"
              type="range"
              min={0}
              max={6}
              step={1}
              value={minRooms}
              onChange={(event) => setMinRooms(Number(event.target.value))}
              className="w-full accent-[#1A8152]"
            />
          </div>

          <div>
            <label
              htmlFor="price"
              className="mb-1.5 flex items-baseline justify-between text-[13px] font-medium text-[#5B6977]"
            >
              Cena do (predaj)
              <span className="font-bold text-[#17457A]">
                {maxPrice >= MAX_PRICE
                  ? "bez limitu"
                  : new Intl.NumberFormat("sk-SK").format(maxPrice) + " €"}
              </span>
            </label>
            <input
              id="price"
              type="range"
              min={100000}
              max={MAX_PRICE}
              step={25000}
              value={maxPrice}
              onChange={(event) => setMaxPrice(Number(event.target.value))}
              className="w-full accent-[#1A8152]"
            />
          </div>
        </div>
      </div>

      {/* ---------- results ---------- */}
      <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
        <p aria-live="polite" className="text-[15px] text-[#5B6977]">
          Nájdených {visible.length}{" "}
          {visible.length === 1 ? "nehnuteľnosť" : visible.length < 5 ? "nehnuteľnosti" : "nehnuteľností"}
        </p>
        <div className="flex items-center gap-2.5">
          <label htmlFor="sort" className="text-[14px] text-[#5B6977]">
            Zoradiť
          </label>
          <select
            id="sort"
            value={sort}
            onChange={(event) => setSort(event.target.value as SortKey)}
            className="h-10 rounded-lg border border-[#D9E0E8] bg-white px-3 text-[14px] focus:border-[#17457A] focus:outline-none"
          >
            {SORTS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {visible.length === 0 ? (
        <div className="mt-8 rounded-xl border border-[#D9E0E8] bg-white px-6 py-16 text-center">
          <p className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#0E2A47]">
            Žiadna nehnuteľnosť nevyhovuje
          </p>
          <p className="mx-auto mt-2 max-w-[44ch] text-[15px] text-[#5B6977]">
            Skúste uvoľniť filtre — napríklad zvýšiť cenový strop alebo znížiť počet izieb.
          </p>
          <button
            type="button"
            onClick={reset}
            className="mt-6 rounded-lg bg-[#17457A] px-5 py-2.5 text-[14px] font-medium text-white"
          >
            Zrušiť filtre
          </button>
        </div>
      ) : (
        <ul className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {visible.map((property) => (
            <li key={property.slug}>
              <Link
                href={`/demo/estate/nehnutelnost/${property.slug}`}
                className="group flex h-full flex-col overflow-hidden rounded-xl border border-[#D9E0E8] bg-white transition-shadow duration-200 hover:shadow-lg"
              >
                <div className="relative aspect-[3/2] overflow-hidden">
                  <Image
                    src={property.main.src}
                    alt={property.main.alt}
                    fill
                    loading="lazy"
                    sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    className="object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                  />
                  <span
                    className="absolute left-3 top-3 rounded px-2.5 py-1 text-[12px] font-bold text-white"
                    style={{ background: property.deal === "predaj" ? "#17457A" : "#1A8152" }}
                  >
                    {DEAL_LABELS[property.deal]}
                  </span>
                </div>

                <div className="flex flex-1 flex-col p-5">
                  <p className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#0E2A47]">
                    {priceLabel(property)}
                  </p>
                  <h3 className="mt-1.5 font-medium text-[#0E2A47]">{property.title}</h3>
                  <p className="mt-1 flex items-center gap-1.5 text-[14px] text-[#5B6977]">
                    <MapPin aria-hidden="true" strokeWidth={1.5} className="size-3.5 shrink-0" />
                    {property.city}
                  </p>

                  <dl className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-[#EDF1F5] pt-4 text-[14px] text-[#5B6977]">
                    <div className="flex items-center gap-1.5">
                      <BedDouble aria-hidden="true" strokeWidth={1.5} className="size-4" />
                      <dt className="sr-only">Izby</dt>
                      <dd>{property.rooms} izby</dd>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Maximize aria-hidden="true" strokeWidth={1.5} className="size-4" />
                      <dt className="sr-only">Plocha</dt>
                      <dd>{property.area} m²</dd>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <dt className="sr-only">Druh</dt>
                      <dd>{TYPE_LABELS[property.type]}</dd>
                    </div>
                  </dl>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
