"use client";

import { useEffect, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import { ShoppingBag, X, Minus, Plus, Trash2 } from "lucide-react";
import { DEMO_BAR_HEIGHT } from "@/components/demo/DemoBar";
import { useCart } from "./CartContext";
import { formatPrice } from "./data";

const NAV = [
  { href: "/demo/shop", label: "Domov" },
  { href: "/demo/shop/produkty", label: "Produkty" },
  { href: "/demo/shop/produkty?kategoria=nabytok", label: "Nábytok" },
  { href: "/demo/shop/produkty?kategoria=textil", label: "Textil" },
];

export function ShopHeader() {
  const { count, setOpen } = useCart();

  return (
    <header
      className="sticky z-40 border-b border-[#E5E5E3] bg-white/92 backdrop-blur"
      style={{ top: DEMO_BAR_HEIGHT }}
    >
      <div className="mx-auto flex h-16 max-w-[1240px] items-center justify-between gap-6 px-5 md:h-20 md:px-8">
        <Link
          href="/demo/shop"
          className="font-[family-name:var(--font-space-grotesk)] text-[20px] font-bold tracking-[0.14em] text-[#1A1A18]"
        >
          NORDIK
        </Link>

        <nav aria-label="Hlavné menu" className="hidden md:block">
          <ul className="flex items-center gap-7">
            {NAV.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-[15px] text-[#4A4A46] transition-colors duration-150 hover:text-[#1A1A18]"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <button
          type="button"
          onClick={() => setOpen(true)}
          className="relative inline-flex size-11 items-center justify-center rounded-lg border border-[#E5E5E3] text-[#1A1A18] transition-colors duration-150 hover:bg-[#F6F5F2]"
          aria-label={`Otvoriť košík, ${count} ${count === 1 ? "položka" : "položiek"}`}
        >
          <ShoppingBag aria-hidden="true" strokeWidth={1.5} className="size-5" />
          {count > 0 ? (
            <span className="absolute -right-1.5 -top-1.5 inline-flex min-w-5 items-center justify-center rounded-full bg-[#A15D33] px-1 text-[11px] font-bold text-white">
              {count}
            </span>
          ) : null}
        </button>
      </div>

      {/* Mobile nav is a simple scroll strip — fewer taps than an overlay for
          a catalogue this small. */}
      <nav aria-label="Kategórie" className="border-t border-[#E5E5E3] md:hidden">
        <ul className="no-scrollbar flex gap-5 overflow-x-auto px-5 py-3">
          {NAV.map((link) => (
            <li key={link.href} className="shrink-0">
              <Link href={link.href} className="text-[14px] text-[#4A4A46]">
                {link.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}

export function CartDrawer() {
  const { detailed, total, setQuantity, remove, isOpen, setOpen, count } = useCart();
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    closeRef.current?.focus();

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [isOpen, setOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[95] bg-black/40"
      onClick={(event) => {
        if (event.target === event.currentTarget) setOpen(false);
      }}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label="Košík"
        className="absolute right-0 top-0 flex h-full w-full max-w-[420px] flex-col bg-white shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-[#E5E5E3] px-6 py-5">
          <h2 className="font-[family-name:var(--font-space-grotesk)] text-xl font-bold text-[#1A1A18]">
            Košík {count > 0 ? `(${count})` : ""}
          </h2>
          <button
            ref={closeRef}
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Zavrieť košík"
            className="inline-flex size-10 items-center justify-center rounded-lg text-[#4A4A46] transition-colors duration-150 hover:bg-[#F6F5F2]"
          >
            <X aria-hidden="true" strokeWidth={1.5} className="size-5" />
          </button>
        </div>

        {detailed.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
            <ShoppingBag aria-hidden="true" strokeWidth={1.5} className="size-10 text-[#C9C9C4]" />
            <p className="text-[#4A4A46]">Košík je zatiaľ prázdny.</p>
            <Link
              href="/demo/shop/produkty"
              onClick={() => setOpen(false)}
              className="rounded-lg bg-[#1A1A18] px-5 py-2.5 text-[14px] font-medium text-white"
            >
              Prejsť na produkty
            </Link>
          </div>
        ) : (
          <>
            <ul className="flex-1 divide-y divide-[#E5E5E3] overflow-y-auto">
              {detailed.map(({ line, product }) => (
                <li key={line.key} className="flex gap-4 p-5">
                  <Image
                    src={product.gallery[0].src}
                    width={product.gallery[0].width}
                    height={product.gallery[0].height}
                    alt={product.gallery[0].alt}
                    sizes="80px"
                    className="size-20 shrink-0 rounded-lg bg-[#F6F5F2] object-cover"
                  />

                  <div className="flex min-w-0 flex-1 flex-col gap-2">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate font-medium text-[#1A1A18]">{product.name}</p>
                        {line.variant ? (
                          <p className="text-[13px] text-[#6E6E68]">{line.variant}</p>
                        ) : null}
                      </div>
                      <button
                        type="button"
                        onClick={() => remove(line.key)}
                        aria-label={`Odstrániť ${product.name} z košíka`}
                        className="shrink-0 text-[#9A9A94] transition-colors duration-150 hover:text-[#A15D33]"
                      >
                        <Trash2 aria-hidden="true" strokeWidth={1.5} className="size-4" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between gap-3">
                      <div className="inline-flex items-center rounded-lg border border-[#E5E5E3]">
                        <button
                          type="button"
                          onClick={() => setQuantity(line.key, line.quantity - 1)}
                          aria-label={`Znížiť počet kusov: ${product.name}`}
                          className="inline-flex size-8 items-center justify-center text-[#4A4A46] hover:bg-[#F6F5F2]"
                        >
                          <Minus aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
                        </button>
                        <span className="min-w-8 text-center text-[14px] font-medium tabular-nums">
                          {line.quantity}
                        </span>
                        <button
                          type="button"
                          onClick={() => setQuantity(line.key, line.quantity + 1)}
                          aria-label={`Zvýšiť počet kusov: ${product.name}`}
                          className="inline-flex size-8 items-center justify-center text-[#4A4A46] hover:bg-[#F6F5F2]"
                        >
                          <Plus aria-hidden="true" strokeWidth={1.5} className="size-3.5" />
                        </button>
                      </div>

                      <p className="font-medium text-[#1A1A18]">
                        {formatPrice(product.price * line.quantity)}
                      </p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            <div className="border-t border-[#E5E5E3] p-6">
              <div className="flex items-baseline justify-between">
                <span className="text-[#4A4A46]">Spolu</span>
                <span
                  aria-live="polite"
                  className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold text-[#1A1A18]"
                >
                  {formatPrice(total)}
                </span>
              </div>
              <p className="mt-1 text-[13px] text-[#6E6E68]">Doprava sa vypočíta v pokladni.</p>
              <Link
                href="/demo/shop/pokladna"
                onClick={() => setOpen(false)}
                className="mt-5 flex h-12 items-center justify-center rounded-lg bg-[#1A1A18] font-medium text-white transition-colors duration-150 hover:bg-[#333330]"
              >
                Prejsť do pokladne
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export function ShopFooter() {
  return (
    <footer className="border-t border-[#E5E5E3] bg-[#F6F5F2] py-12">
      <div className="mx-auto flex max-w-[1240px] flex-col gap-3 px-5 text-[14px] text-[#6E6E68] md:flex-row md:items-center md:justify-between md:px-8">
        <p className="font-[family-name:var(--font-space-grotesk)] text-[16px] font-bold tracking-[0.14em] text-[#1A1A18]">
          NORDIK
        </p>
        <p>Vymyslený obchod. Ukážkový web vytvorilo štúdio Webora.</p>
      </div>
    </footer>
  );
}
