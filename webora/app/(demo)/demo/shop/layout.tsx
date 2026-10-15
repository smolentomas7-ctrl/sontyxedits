import type { Metadata } from "next";
import { DemoShell } from "@/components/demo/DemoShell";
import { CartProvider } from "./CartContext";
import { ShopHeader, CartDrawer, ShopFooter } from "./ShopChrome";

export const metadata: Metadata = {
  title: "Nordik — demo e-shop",
  robots: { index: false, follow: false },
};

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return (
    <DemoShell kind="eshop">
      <CartProvider>
        <div className="min-h-screen bg-white font-[family-name:var(--font-inter)] text-[#1A1A18] antialiased">
          <ShopHeader />
          <main>{children}</main>
          <ShopFooter />
          <CartDrawer />
        </div>
      </CartProvider>
    </DemoShell>
  );
}
