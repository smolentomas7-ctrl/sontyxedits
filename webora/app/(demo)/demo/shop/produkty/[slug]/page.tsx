import { notFound } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { ArrowLeft } from "lucide-react";
import { products, getProduct, formatPrice, CATEGORIES } from "../../data";
import { ProductDetail } from "./ProductDetail";

export function generateStaticParams() {
  return products.map((product) => ({ slug: product.slug }));
}

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = getProduct(slug);
  if (!product) notFound();

  const categoryLabel = CATEGORIES.find((c) => c.id === product.category)?.label ?? "";
  const related = products.filter((p) => p.slug !== product.slug).slice(0, 4);

  return (
    <div className="mx-auto max-w-[1240px] px-5 py-10 md:px-8 md:py-16">
      <Link
        href="/demo/shop/produkty"
        className="inline-flex items-center gap-1.5 text-[14px] text-[#6E6E68] transition-colors duration-150 hover:text-[#1A1A18]"
      >
        <ArrowLeft aria-hidden="true" strokeWidth={1.5} className="size-4" />
        Späť na produkty
      </Link>

      <ProductDetail product={product} categoryLabel={categoryLabel} />

      <section className="mt-20 border-t border-[#E5E5E3] pt-12">
        <h2 className="mb-7 font-[family-name:var(--font-space-grotesk)] text-[1.5rem] font-bold tracking-[-0.02em]">
          Mohlo by sa hodiť
        </h2>
        <ul className="grid grid-cols-2 gap-5 lg:grid-cols-4">
          {related.map((item) => (
            <li key={item.slug}>
              <Link href={`/demo/shop/produkty/${item.slug}`} className="group block">
                <div className="aspect-square overflow-hidden rounded-xl bg-[#F6F5F2]">
                  <Image
                    src={item.gallery[0].src}
                    width={item.gallery[0].width}
                    height={item.gallery[0].height}
                    alt={item.gallery[0].alt}
                    loading="lazy"
                    sizes="(max-width: 1024px) 50vw, 25vw"
                    className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                  />
                </div>
                <p className="mt-3 font-medium">{item.name}</p>
                <p className="text-[14px] text-[#6E6E68]">{formatPrice(item.price)}</p>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
