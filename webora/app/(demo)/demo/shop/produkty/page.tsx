import { Suspense } from "react";
import { ProductBrowser } from "./ProductBrowser";

export default function ProductsPage() {
  return (
    <div className="mx-auto max-w-[1240px] px-5 py-14 md:px-8 md:py-20">
      <header className="mb-10">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-[2rem] font-bold tracking-[-0.025em] md:text-[2.75rem]">
          Produkty
        </h1>
        <p className="mt-3 max-w-[52ch] text-[16px] text-[#4A4A46]">
          Deväť kusov, ktoré máme stále na sklade. Filtrovanie aj zoraďovanie beží priamo
          v prehliadači.
        </p>
      </header>

      <Suspense fallback={<div className="h-96" />}>
        <ProductBrowser />
      </Suspense>
    </div>
  );
}
