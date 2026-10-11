"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getProduct, type Product } from "./data";

export type CartLine = {
  /** slug plus the chosen variant, so two variants are separate lines. */
  key: string;
  slug: string;
  variant?: string;
  quantity: number;
};

type CartContextValue = {
  lines: CartLine[];
  /** Lines joined with their product record, skipping anything unresolvable. */
  detailed: { line: CartLine; product: Product }[];
  count: number;
  total: number;
  add: (slug: string, variant?: string, quantity?: number) => void;
  setQuantity: (key: string, quantity: number) => void;
  remove: (key: string) => void;
  clear: () => void;
  isOpen: boolean;
  setOpen: (open: boolean) => void;
};

const CartContext = createContext<CartContextValue | null>(null);

const STORAGE_KEY = "webora-demo-shop-cart";

/** Reads the saved cart. Every access is guarded: storage can throw in a
 *  private window, or hold data written by an older version of this demo. */
function readStorage(): CartLine[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (entry): entry is CartLine =>
        typeof entry === "object" &&
        entry !== null &&
        typeof (entry as CartLine).key === "string" &&
        typeof (entry as CartLine).slug === "string" &&
        typeof (entry as CartLine).quantity === "number",
    );
  } catch {
    return [];
  }
}

function writeStorage(lines: CartLine[]) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(lines));
  } catch {
    // Storage full or blocked — the cart still works for this page view.
  }
}

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [isOpen, setOpen] = useState(false);

  // Hydrate after mount so server and client markup match on first render.
  useEffect(() => {
    setLines(readStorage());
  }, []);

  useEffect(() => {
    writeStorage(lines);
  }, [lines]);

  const add = useCallback((slug: string, variant?: string, quantity = 1) => {
    const key = variant ? `${slug}::${variant}` : slug;
    setLines((current) => {
      const existing = current.find((line) => line.key === key);
      if (existing) {
        return current.map((line) =>
          line.key === key ? { ...line, quantity: line.quantity + quantity } : line,
        );
      }
      return [...current, { key, slug, variant, quantity }];
    });
    setOpen(true);
  }, []);

  const setQuantity = useCallback((key: string, quantity: number) => {
    setLines((current) =>
      quantity <= 0
        ? current.filter((line) => line.key !== key)
        : current.map((line) => (line.key === key ? { ...line, quantity } : line)),
    );
  }, []);

  const remove = useCallback((key: string) => {
    setLines((current) => current.filter((line) => line.key !== key));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const detailed = useMemo(
    () =>
      lines.flatMap((line) => {
        const product = getProduct(line.slug);
        return product ? [{ line, product }] : [];
      }),
    [lines],
  );

  const count = useMemo(
    () => detailed.reduce((sum, { line }) => sum + line.quantity, 0),
    [detailed],
  );

  const total = useMemo(
    () => detailed.reduce((sum, { line, product }) => sum + product.price * line.quantity, 0),
    [detailed],
  );

  const value: CartContextValue = {
    lines,
    detailed,
    count,
    total,
    add,
    setQuantity,
    remove,
    clear,
    isOpen,
    setOpen,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const context = useContext(CartContext);
  if (!context) throw new Error("useCart must be used inside CartProvider");
  return context;
}
