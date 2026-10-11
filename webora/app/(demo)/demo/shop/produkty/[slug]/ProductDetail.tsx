"use client";

import { useState } from "react";
import Image from "next/image";
import { Check, Minus, Plus } from "lucide-react";
import { useCart } from "../../CartContext";
import { formatPrice, type Product } from "../../data";

export function ProductDetail({
  product,
  categoryLabel,
}: {
  product: Product;
  categoryLabel: string;
}) {
  const { add } = useCart();
  const [activeImage, setActiveImage] = useState(0);
  const [variant, setVariant] = useState(product.variants?.options[0]);
  const [quantity, setQuantity] = useState(1);
  const [justAdded, setJustAdded] = useState(false);

  function onAdd() {
    add(product.slug, variant, quantity);
    setJustAdded(true);
    window.setTimeout(() => setJustAdded(false), 2000);
  }

  const main = product.gallery[activeImage] ?? product.gallery[0];

  return (
    <div className="mt-8 grid gap-10 lg:grid-cols-2 lg:gap-16">
      {/* ---------- gallery ---------- */}
      <div className="flex flex-col gap-4">
        <div className="aspect-square overflow-hidden rounded-2xl bg-[#F6F5F2]">
          <Image
            key={main.src}
            src={main.src}
            width={main.width}
            height={main.height}
            alt={main.alt}
            priority
            sizes="(max-width: 1024px) 100vw, 50vw"
            className="size-full object-cover"
          />
        </div>

        {product.gallery.length > 1 ? (
          <ul className="grid grid-cols-4 gap-3">
            {product.gallery.map((image, index) => (
              <li key={image.src}>
                <button
                  type="button"
                  onClick={() => setActiveImage(index)}
                  aria-label={`Zobraziť obrázok ${index + 1} z ${product.gallery.length}`}
                  aria-current={index === activeImage}
                  className="block w-full overflow-hidden rounded-lg border-2 transition-colors duration-150"
                  style={{ borderColor: index === activeImage ? "#C2703D" : "transparent" }}
                >
                  <Image
                    src={image.src}
                    width={image.width}
                    height={image.height}
                    alt=""
                    loading="lazy"
                    sizes="140px"
                    className="aspect-square w-full bg-[#F6F5F2] object-cover"
                  />
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </div>

      {/* ---------- details ---------- */}
      <div>
        <p className="text-[13px] font-medium uppercase tracking-[0.16em] text-[#C2703D]">
          {categoryLabel}
        </p>
        <h1 className="mt-3 font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.025em] md:text-[2.5rem]">
          {product.name}
        </h1>
        <p className="mt-3 font-[family-name:var(--font-space-grotesk)] text-2xl font-bold">
          {formatPrice(product.price)}
        </p>

        <p className="mt-6 text-[16px] leading-relaxed text-[#4A4A46]">{product.description}</p>

        {product.variants ? (
          <fieldset className="mt-8">
            <legend className="mb-3 text-[13px] font-medium uppercase tracking-[0.12em] text-[#6E6E68]">
              {product.variants.label}
            </legend>
            <div className="flex flex-wrap gap-2.5">
              {product.variants.options.map((option) => {
                const selected = option === variant;
                return (
                  <label
                    key={option}
                    className="cursor-pointer rounded-lg border px-4 py-2.5 text-[14px] transition-colors duration-150"
                    style={
                      selected
                        ? { borderColor: "#1A1A18", background: "#1A1A18", color: "#FFFFFF" }
                        : { borderColor: "#E5E5E3", background: "#FFFFFF", color: "#4A4A46" }
                    }
                  >
                    <input
                      type="radio"
                      name="variant"
                      value={option}
                      checked={selected}
                      onChange={() => setVariant(option)}
                      className="sr-only"
                    />
                    {option}
                  </label>
                );
              })}
            </div>
          </fieldset>
        ) : null}

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <div className="inline-flex items-center rounded-lg border border-[#E5E5E3]">
            <button
              type="button"
              onClick={() => setQuantity((n) => Math.max(1, n - 1))}
              disabled={quantity <= 1}
              aria-label="Znížiť počet kusov"
              className="inline-flex size-11 items-center justify-center text-[#4A4A46] hover:bg-[#F6F5F2] disabled:opacity-40"
            >
              <Minus aria-hidden="true" strokeWidth={1.5} className="size-4" />
            </button>
            <span className="min-w-10 text-center font-medium tabular-nums">{quantity}</span>
            <button
              type="button"
              onClick={() => setQuantity((n) => Math.min(99, n + 1))}
              aria-label="Zvýšiť počet kusov"
              className="inline-flex size-11 items-center justify-center text-[#4A4A46] hover:bg-[#F6F5F2]"
            >
              <Plus aria-hidden="true" strokeWidth={1.5} className="size-4" />
            </button>
          </div>

          <button
            type="button"
            onClick={onAdd}
            className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-lg bg-[#1A1A18] px-8 font-medium text-white transition-colors duration-150 hover:bg-[#333330] sm:flex-none"
          >
            {justAdded ? (
              <>
                <Check aria-hidden="true" strokeWidth={1.5} className="size-4" />
                Pridané
              </>
            ) : (
              "Pridať do košíka"
            )}
          </button>
        </div>

        <p aria-live="polite" className="sr-only">
          {justAdded ? `${product.name} pridaný do košíka` : ""}
        </p>

        <dl className="mt-10 border-t border-[#E5E5E3] pt-7 text-[15px]">
          <div className="flex justify-between gap-6 border-b border-[#E5E5E3] py-3">
            <dt className="text-[#6E6E68]">Materiál</dt>
            <dd className="text-right font-medium">{product.material}</dd>
          </div>
          <div className="flex justify-between gap-6 border-b border-[#E5E5E3] py-3">
            <dt className="text-[#6E6E68]">Rozmery</dt>
            <dd className="text-right font-medium">{product.dimensions}</dd>
          </div>
          <div className="flex justify-between gap-6 py-3">
            <dt className="text-[#6E6E68]">Dostupnosť</dt>
            <dd className="text-right font-medium text-[#2F7A4F]">Skladom</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
