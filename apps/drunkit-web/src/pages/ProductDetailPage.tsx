import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { ListingCard as ListingCardType } from "../types/api";
import { PriceDisplay } from "../components/PriceDisplay";
import { AvailabilityBadge } from "../components/AvailabilityBadge";
import { Seal } from "../components/Seal";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

export function ProductDetailPage() {
  const { listingId } = useParams<{ listingId: string }>();
  const [listing, setListing] = useState<ListingCardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const { addItem } = useCart();
  const { me } = useAuth();

  useEffect(() => {
    if (!listingId) return;
    setLoading(true);
    api
      .getListing(listingId)
      .then(setListing)
      .catch((err) =>
        setError(err instanceof ApiRequestError ? err.message : "Couldn't load this product.")
      )
      .finally(() => setLoading(false));
  }, [listingId]);

  if (loading) {
    return <div className="mx-auto max-w-4xl px-4 py-10 text-parchment/50">Loading…</div>;
  }

  if (error || !listing) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-parchment/70">{error ?? "Product not found."}</p>
        <Link to="/" className="mt-3 inline-block text-sm text-brass-400 hover:text-brass-300">
          ← Back to browsing
        </Link>
      </div>
    );
  }

  function handleAdd() {
    if (!listing) return;
    const result = addItem(listing);
    setToast(result.ok ? `Added ${listing.name}` : result.reason ?? "Couldn't add this item.");
    setTimeout(() => setToast(null), 3000);
  }

  const disabled = !listing.can_add_to_cart;

  return (
    <div className="mx-auto max-w-4xl px-4 py-6">
      <Link to="/" className="text-xs text-parchment/40 hover:text-parchment/70">
        ← Back
      </Link>

      <div className="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2">
        <div className="aspect-square rounded-xl bg-ink-800 flex items-center justify-center overflow-hidden border border-ink-700">
          {listing.image_url ? (
            <img src={listing.image_url} alt={listing.name} className="h-full w-full object-cover" />
          ) : (
            <span className="label-eyebrow">{listing.category}</span>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div>
            <p className="label-eyebrow">{listing.brand}</p>
            <h1 className="mt-1 font-display text-2xl text-parchment">{listing.name}</h1>
            <p className="mt-1 text-sm text-parchment/50">
              {listing.pack_size}
              {listing.variant ? ` · ${listing.variant}` : ""}
            </p>
          </div>

          <PriceDisplay price={listing.price} />

          <div className="flex items-center gap-4">
            <AvailabilityBadge status={listing.availability_status} />
            <span className="text-xs font-mono text-parchment/50">
              Delivery in {listing.eta_min_minutes}–{listing.eta_max_minutes} min
            </span>
          </div>

          <div className="flex flex-col gap-2 rounded-lg border border-ink-700 bg-ink-800/50 p-3">
            {listing.seller_verified && <Seal label="Verified seller" tone="brass" />}
            <p className="text-xs text-parchment/50">Sold and delivered by {listing.store_name}</p>
          </div>

          {disabled && (
            <p className="rounded-lg border border-brass-600/30 bg-brass-500/5 px-3 py-2 text-sm text-brass-400">
              {listing.eligibility_reason}
              {!me && (
                <>
                  {" "}
                  <Link to="/login" className="underline hover:text-brass-300">
                    Log in
                  </Link>{" "}
                  to continue.
                </>
              )}
              {me && me.eligibility_state !== "VERIFIED" && (
                <>
                  {" "}
                  <Link to="/eligibility" className="underline hover:text-brass-300">
                    Verify eligibility
                  </Link>
                  .
                </>
              )}
            </p>
          )}

          <button
            onClick={handleAdd}
            disabled={disabled}
            className={`rounded-lg py-3 text-sm font-medium transition-colors ${
              disabled
                ? "bg-ink-700 text-parchment/40 cursor-not-allowed"
                : "bg-brass-500 text-ink-950 hover:bg-brass-400"
            }`}
          >
            Add to cart
          </button>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-lg bg-ink-700 px-4 py-2 text-sm text-parchment shadow-seal">
          {toast}
        </div>
      )}
    </div>
  );
}
