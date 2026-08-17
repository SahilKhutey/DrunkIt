import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { CartLine, ListingCard } from "../types/api";

interface CartContextValue {
  lines: CartLine[];
  addItem: (listing: ListingCard, quantity?: number) => { ok: boolean; reason?: string };
  removeItem: (productId: string) => void;
  setQuantity: (productId: string, quantity: number) => void;
  clear: () => void;
  subtotal: number;
  itemCount: number;
  storeId: string | null;
  storeName: string | null;
}

const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);

  const addItem = useCallback(
    (listing: ListingCard, quantity = 1): { ok: boolean; reason?: string } => {
      let result: { ok: boolean; reason?: string } = { ok: true };
      setLines((prev) => {
        // A quick-commerce cart is fulfilled from one store — adding
        // from a second store would silently split fulfilment, so we
        // block it with a clear reason instead.
        if (prev.length > 0 && prev[0].store_id !== listing.store_id) {
          result = {
            ok: false,
            reason: `Your cart has items from ${prev[0].store_name}. Clear it first to order from ${listing.store_name}.`,
          };
          return prev;
        }
        const existing = prev.find((l) => l.product_id === listing.product_id);
        if (existing) {
          return prev.map((l) =>
            l.product_id === listing.product_id ? { ...l, quantity: l.quantity + quantity } : l
          );
        }
        return [
          ...prev,
          {
            product_id: listing.product_id,
            quantity,
            name: listing.name,
            unit_price: listing.price.selling_price,
            pack_size: listing.pack_size,
            store_id: listing.store_id,
            store_name: listing.store_name,
          },
        ];
      });
      return result;
    },
    []
  );

  const removeItem = useCallback((productId: string) => {
    setLines((prev) => prev.filter((l) => l.product_id !== productId));
  }, []);

  const setQuantity = useCallback((productId: string, quantity: number) => {
    setLines((prev) =>
      quantity <= 0
        ? prev.filter((l) => l.product_id !== productId)
        : prev.map((l) => (l.product_id === productId ? { ...l, quantity } : l))
    );
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const subtotal = useMemo(() => lines.reduce((sum, l) => sum + l.unit_price * l.quantity, 0), [lines]);
  const itemCount = useMemo(() => lines.reduce((sum, l) => sum + l.quantity, 0), [lines]);

  return (
    <CartContext.Provider
      value={{
        lines,
        addItem,
        removeItem,
        setQuantity,
        clear,
        subtotal,
        itemCount,
        storeId: lines[0]?.store_id ?? null,
        storeName: lines[0]?.store_name ?? null,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
