import type { Price } from "../types/api";

export function PriceDisplay({ price }: { price: Price }) {
  const hasDiscount = price.discount_percentage > 0.5;
  return (
    <div className="flex items-baseline gap-2 font-mono tabular-nums">
      <span className="text-lg text-parchment">₹{price.selling_price.toFixed(0)}</span>
      {hasDiscount && (
        <>
          <span className="text-xs text-parchment/40 line-through">₹{price.mrp.toFixed(0)}</span>
          <span className="text-xs text-copper-400">{price.discount_percentage.toFixed(0)}% off</span>
        </>
      )}
    </div>
  );
}
