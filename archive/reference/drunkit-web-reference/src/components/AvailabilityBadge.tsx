import type { ListingCard } from "../types/api";

export function AvailabilityBadge({ status }: { status: ListingCard["availability_status"] }) {
  const config = {
    IN_STOCK: { label: "In stock", className: "text-sage-400" },
    LOW_STOCK: { label: "Low stock", className: "text-copper-400" },
    OUT_OF_STOCK: { label: "Out of stock", className: "text-rust-400" },
  }[status];

  return <span className={`text-xs font-medium ${config.className}`}>{config.label}</span>;
}
