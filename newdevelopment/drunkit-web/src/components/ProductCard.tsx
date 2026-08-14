import { Link } from "react-router-dom";
import type { ListingCard } from "../types/api";
import { PriceDisplay } from "./PriceDisplay";
import { AvailabilityBadge } from "./AvailabilityBadge";
import { Seal } from "./Seal";

interface Props {
  listing: ListingCard;
  onAdd: (listing: ListingCard) => void;
}

export function ProductCard({ listing, onAdd }: Props) {
  const disabled = !listing.can_add_to_cart;

  return (
    <div className="group flex flex-col rounded-xl border border-ink-700 bg-ink-800/60 overflow-hidden transition-colors hover:border-brass-600/40">
      <Link to={`/product/${listing.listing_id}`} className="block">
        <div className="aspect-square bg-ink-700 flex items-center justify-center overflow-hidden">
          {listing.image_url ? (
            <img
              src={listing.image_url}
              alt={listing.name}
              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <span className="label-eyebrow">{listing.category}</span>
          )}
        </div>
      </Link>

      <div className="flex flex-1 flex-col gap-2 p-3">
        <div>
          <p className="label-eyebrow">{listing.brand}</p>
          <Link to={`/product/${listing.listing_id}`}>
            <h3 className="font-display text-[15px] leading-snug text-parchment hover:text-brass-400 transition-colors">
              {listing.name}
            </h3>
          </Link>
          <p className="text-xs text-parchment/50">{listing.pack_size}</p>
        </div>

        <PriceDisplay price={listing.price} />

        <div className="flex items-center justify-between">
          <AvailabilityBadge status={listing.availability_status} />
          <span className="text-xs text-parchment/50 font-mono">
            {listing.eta_min_minutes}–{listing.eta_max_minutes} min
          </span>
        </div>

        {listing.seller_verified && <Seal label="Verified seller" tone="brass" />}

        <button
          onClick={() => onAdd(listing)}
          disabled={disabled}
          className={`mt-1 w-full rounded-lg py-2 text-sm font-medium transition-colors ${
            disabled
              ? "bg-ink-700 text-parchment/40 cursor-not-allowed"
              : "bg-brass-500 text-ink-950 hover:bg-brass-400"
          }`}
          title={disabled ? listing.eligibility_reason : undefined}
        >
          {disabled ? "View product" : "Add"}
        </button>
      </div>
    </div>
  );
}
