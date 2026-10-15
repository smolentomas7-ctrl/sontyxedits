import Image from "next/image";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { shop } from "@/config/images";
import { products, formatPrice, CATEGORIES } from "./data";

const CATEGORY_TILES = [
  { id: "vazy", image: shop.category1 },
  { id: "textil", image: shop.category2 },
  { id: "kuchyna", image: shop.category3 },
  { id: "nabytok", image: shop.category4 },
] as const;

export default function ShopHome() {
  const featured = products.slice(0, 4);

  return (
    <>
      {/* ---------- HERO ---------- */}
      <section className="relative">
        <div className="relative h-[58vh] min-h-[380px] w-full md:h-[64vh]">
          <Image
            src={shop.hero.src}
            alt={shop.hero.alt}
            fill
            priority
            sizes="100vw"
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-white/92 via-white/55 to-transparent" />
          <div className="absolute inset-0 flex items-center">
            <div className="mx-auto w-full max-w-[1240px] px-5 md:px-8">
              <p className="mb-4 text-[12px] font-medium uppercase tracking-[0.24em] text-[#A15D33]">
                Nová kolekcia
              </p>
              <h1 className="max-w-[14ch] font-[family-name:var(--font-space-grotesk)] text-[2.5rem] font-bold leading-[1.04] tracking-[-0.03em] text-[#1A1A18] md:text-[4rem]">
                Veci, ktoré vydržia dlhšie než trend
              </h1>
              <p className="mt-5 max-w-[42ch] text-[17px] leading-relaxed text-[#4A4A46]">
                Keramika, textil a nábytok od malých európskych dielní. Žiadne limitované edície,
                ktoré o rok nedokúpite.
              </p>
              <Link
                href="/demo/shop/produkty"
                className="mt-8 inline-flex h-12 items-center gap-2 rounded-lg bg-[#1A1A18] px-7 font-medium text-white transition-colors duration-150 hover:bg-[#333330]"
              >
                Zobraziť produkty
                <ArrowRight aria-hidden="true" strokeWidth={1.5} className="size-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ---------- CATEGORY TILES ---------- */}
      <section className="mx-auto max-w-[1240px] px-5 py-16 md:px-8 md:py-24">
        <h2 className="mb-9 font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
          Kategórie
        </h2>
        <ul className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {CATEGORY_TILES.map((tile) => {
            const label = CATEGORIES.find((c) => c.id === tile.id)?.label ?? tile.id;
            return (
              <li key={tile.id}>
                <Link
                  href={`/demo/shop/produkty?kategoria=${tile.id}`}
                  className="group block overflow-hidden rounded-xl"
                >
                  <div className="relative aspect-[4/5] overflow-hidden bg-[#F6F5F2]">
                    <Image
                      src={tile.image.src}
                      alt={tile.image.alt}
                      fill
                      loading="lazy"
                      sizes="(max-width: 1024px) 50vw, 25vw"
                      className="object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/55 to-transparent" />
                    <span className="absolute bottom-4 left-4 font-[family-name:var(--font-space-grotesk)] text-[17px] font-bold text-white">
                      {label}
                    </span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </section>

      {/* ---------- FEATURED ---------- */}
      <section className="border-t border-[#E5E5E3] bg-[#F6F5F2] py-16 md:py-24">
        <div className="mx-auto max-w-[1240px] px-5 md:px-8">
          <div className="mb-9 flex items-end justify-between gap-6">
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-[1.75rem] font-bold tracking-[-0.02em] md:text-[2.25rem]">
              Vybrané kusy
            </h2>
            <Link
              href="/demo/shop/produkty"
              className="shrink-0 text-[15px] font-medium text-[#A15D33] hover:underline"
            >
              Všetky produkty
            </Link>
          </div>

          <ul className="grid grid-cols-2 gap-5 lg:grid-cols-4">
            {featured.map((product) => (
              <li key={product.slug}>
                <Link href={`/demo/shop/produkty/${product.slug}`} className="group block">
                  <div className="aspect-square overflow-hidden rounded-xl bg-white">
                    <Image
                      src={product.gallery[0].src}
                      width={product.gallery[0].width}
                      height={product.gallery[0].height}
                      alt={product.gallery[0].alt}
                      loading="lazy"
                      sizes="(max-width: 1024px) 50vw, 25vw"
                      className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                    />
                  </div>
                  <p className="mt-3 font-medium text-[#1A1A18]">{product.name}</p>
                  <p className="text-[14px] text-[#6E6E68]">{formatPrice(product.price)}</p>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}
