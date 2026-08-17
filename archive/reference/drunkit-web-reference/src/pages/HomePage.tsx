import { useEffect, useState } from "react";
import { api, ApiRequestError } from "../api/client";
import type { ListingCard as ListingCardType } from "../types/api";
import { ProductCard } from "../components/ProductCard";
import { EligibilityBanner } from "../components/EligibilityBanner";
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
  const [listings, setListings] = useState<ListingCardType[]>([]);
  const [category, setCategory] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

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
    if (!result.ok) {
      setToast(result.reason ?? "Couldn't add this item.");
      setTimeout(() => setToast(null), 3500);
    } else {
      setToast(`Added ${listing.name}`);
      setTimeout(() => setToast(null), 1500);
    }
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

          {loading && <SkeletonGrid />}

          {!loading && error && (
            <EmptyState title="Couldn't load products" body={error} />
          )}

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

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-lg bg-ink-700 px-4 py-2 text-sm text-parchment shadow-seal">
          {toast}
        </div>
      )}
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="animate-pulse overflow-hidden rounded-xl border border-ink-700">
          <div className="aspect-square bg-ink-800" />
          <div className="space-y-2 p-3">
            <div className="h-3 w-2/3 rounded bg-ink-800" />
            <div className="h-4 w-full rounded bg-ink-800" />
            <div className="h-8 w-full rounded bg-ink-800" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-ink-700 py-16 text-center">
      <p className="font-display text-lg text-parchment">{title}</p>
      <p className="max-w-sm text-sm text-parchment/50">{body}</p>
    </div>
  );
}
