import { useEffect, useState } from "react";
import { api, ApiRequestError } from "../api/client";
import type { ListingCard as ListingCardType } from "../types/api";
import { ProductCard } from "../components/ProductCard";
import { EligibilityBanner } from "../components/EligibilityBanner";
import { SkeletonCardGrid } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { useToast } from "../components/ui/Toast";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

// Placeholder coordinates (Mumbai) used until real geolocation/address
// entry is wired in — the backend's serviceability query already
// takes lat/lng, this just needs a real location source later.
const DEFAULT_LAT = 19.076;
const DEFAULT_LNG = 72.8777;

const CATEGORIES = ["all", "beer", "wine", "whisky", "rum", "vodka"];

export function HomePage() {
  const { me, deliveryState } = useAuth();
  const { addItem } = useCart();
  const { showToast } = useToast();
  const [listings, setListings] = useState<ListingCardType[]>([]);
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deliveryState) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .listListings(DEFAULT_LAT, DEFAULT_LNG, deliveryState, category === "all" ? undefined : category)
      .then(setListings)
      .catch((err) => setError(err instanceof ApiRequestError ? err.message : "Couldn't load products."))
      .finally(() => setLoading(false));
  }, [deliveryState, category]);

  function handleAdd(listing: ListingCardType) {
    const result = addItem(listing);
    showToast(
      result.ok ? `Added ${listing.name}` : result.reason ?? "Couldn't add this item.",
      result.ok ? "success" : "error"
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <div className="mb-6 flex flex-col gap-3">
        <div>
          <p className="label-eyebrow">Quick commerce · Trust commerce</p>
          <h1 className="mt-1 font-display text-3xl text-parchment">
            Verified delivery, on your terms.
          </h1>
        </div>
        <EligibilityBanner me={me} />
      </div>

      {!deliveryState ? (
        <EmptyState
          title="Set your delivery location"
          body="Verify your age and state to see what's available near you."
        />
      ) : (
        <>
          <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
            {CATEGORIES.map((c) => (
              <button
                key={c}
                onClick={() => setCategory(c)}
                className={`shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                  category === c
                    ? "border-brass-500 bg-brass-500/10 text-brass-400"
                    : "border-ink-700 text-parchment/60 hover:text-parchment"
                }`}
              >
                {c}
              </button>
            ))}
          </div>

          {loading && <SkeletonCardGrid />}

          {!loading && error && <EmptyState title="Couldn't load products" body={error} />}

          {!loading && !error && listings.length === 0 && (
            <EmptyState
              title="Nothing available here yet"
              body="No stores are currently serviceable for your state and category."
            />
          )}

          {!loading && !error && listings.length > 0 && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {listings.map((listing) => (
                <ProductCard key={listing.listing_id} listing={listing} onAdd={handleAdd} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
