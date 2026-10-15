"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { products, CATEGORIES, PRICE_BOUNDS, formatPrice, type Category } from "../data";

type SortKey = "featured" | "price-asc" | "price-desc" | "name";

const SORTS: { id: SortKey; label: string }[] = [
  { id: "featured", label: "Odporúčané" },
  { id: "price-asc", label: "Cena: od najnižšej" },
  { id: "price-desc", label: "Cena: od najvyššej" },
  { id: "name", label: "Názov A–Z" },
];

export function ProductBrowser() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get("kategoria");

  const [categories, setCategories] = useState<Category[]>(() =>
    CATEGORIES.some((c) => c.id === initialCategory) ? [initialCategory as Category] : [],
  );
  const [maxPrice, setMaxPrice] = useState(PRICE_BOUNDS.max);
  const [sort, setSort] = useState<SortKey>("featured");

  const visible = useMemo(() => {
    const filtered = products.filter((product) => {
      const categoryOk = categories.length === 0 || categories.includes(product.category);
      const priceOk = product.price <= maxPrice;
      return categoryOk && priceOk;
    });

    const sorted = [...filtered];
    if (sort === "price-asc") sorted.sort((a, b) => a.price - b.price);
    if (sort === "price-desc") sorted.sort((a, b) => b.price - a.price);
    if (sort === "name") sorted.sort((a, b) => a.name.localeCompare(b.name, "sk"));
    return sorted;
  }, [categories, maxPrice, sort]);

  function toggleCategory(id: Category) {
    setCategories((current) =>
      current.includes(id) ? current.filter((c) => c !== id) : [...current, id],
    );
  }

  const hasFilters = categories.length > 0 || maxPrice < PRICE_BOUNDS.max;

  return (
    <div className="grid gap-10 lg:grid-cols-[250px_1fr] lg:gap-12">
      {/* ---------- filters ---------- */}
      <aside className="lg:sticky lg:top-40 lg:self-start">
        <h2 className="mb-5 font-[family-name:var(--font-space-grotesk)] text-[17px] font-bold">
          Filtre
        </h2>

        <fieldset className="border-b border-[#E5E5E3] pb-6">
          <legend className="mb-3 text-[13px] font-medium uppercase tracking-[0.12em] text-[#6E6E68]">
            Kategória
          </legend>
          <div className="flex flex-col gap-2.5">
            {CATEGORIES.map((category) => (
              <label key={category.id} className="flex cursor-pointer items-center gap-2.5">
                <input
                  type="checkbox"
                  checked={categories.includes(category.id)}
                  onChange={() => toggleCategory(category.id)}
                  className="size-4 rounded accent-[#A15D33]"
                />
                <span className="text-[15px] text-[#4A4A46]">{category.label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <div className="border-b border-[#E5E5E3] py-6">
          <label
            htmlFor="price-filter"
            className="mb-3 flex items-baseline justify-between text-[13px] font-medium uppercase tracking-[0.12em] text-[#6E6E68]"
          >
            Cena do
            <span className="font-[family-name:var(--font-space-grotesk)] text-[15px] font-bold normal-case tracking-normal text-[#1A1A18]">
              {maxPrice} €
            </span>
          </label>
          <input
            id="price-filter"
            type="range"
            min={PRICE_BOUNDS.min}
            max={PRICE_BOUNDS.max}
            step={10}
            value={maxPrice}
            onChange={(event) => setMaxPrice(Number(event.target.value))}
            className="w-full accent-[#A15D33]"
          />
        </div>

        {hasFilters ? (
          <button
            type="button"
            onClick={() => {
              setCategories([]);
              setMaxPrice(PRICE_BOUNDS.max);
            }}
            className="mt-5 text-[14px] font-medium text-[#A15D33] hover:underline"
          >
            Zrušiť filtre
          </button>
        ) : null}
      </aside>

      {/* ---------- results ---------- */}
      <div>
        <div className="mb-7 flex flex-wrap items-center justify-between gap-4">
          <p aria-live="polite" className="text-[15px] text-[#6E6E68]">
            {visible.length} {visible.length === 1 ? "produkt" : visible.length < 5 ? "produkty" : "produktov"}
          </p>

          <div className="flex items-center gap-2.5">
            <label htmlFor="sort" className="text-[14px] text-[#6E6E68]">
              Zoradiť
            </label>
            <select
              id="sort"
              value={sort}
              onChange={(event) => setSort(event.target.value as SortKey)}
              className="h-10 rounded-lg border border-[#E5E5E3] bg-white px-3 text-[14px] focus:outline-none focus:ring-2 focus:ring-[#A15D33]/40"
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
          <div className="rounded-xl border border-[#E5E5E3] bg-[#F6F5F2] px-6 py-16 text-center">
            <p className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold">
              Nič nevyhovuje zvoleným filtrom
            </p>
            <p className="mx-auto mt-2 max-w-[40ch] text-[15px] text-[#6E6E68]">
              Skúste zvýšiť cenový strop alebo vybrať inú kategóriu.
            </p>
          </div>
        ) : (
          <ul className="grid grid-cols-2 gap-5 lg:grid-cols-3">
            {visible.map((product) => (
              <li key={product.slug}>
                <Link href={`/demo/shop/produkty/${product.slug}`} className="group block">
                  <div className="aspect-square overflow-hidden rounded-xl bg-[#F6F5F2]">
                    <Image
                      src={product.gallery[0].src}
                      width={product.gallery[0].width}
                      height={product.gallery[0].height}
                      alt={product.gallery[0].alt}
                      loading="lazy"
                      sizes="(max-width: 1024px) 50vw, 33vw"
                      className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                    />
                  </div>
                  <p className="mt-3 font-medium text-[#1A1A18]">{product.name}</p>
                  <p className="text-[14px] text-[#6E6E68]">{product.short}</p>
                  <p className="mt-1 font-medium text-[#1A1A18]">{formatPrice(product.price)}</p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
