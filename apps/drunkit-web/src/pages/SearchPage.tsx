import { useEffect, useMemo, useState } from "react";
import { api, ApiRequestError } from "../api/client";
import type { ListingCard as ListingCardType } from "../types/api";
import { ProductCard } from "../components/ProductCard";
import { SkeletonCardGrid } from "../components/ui/Skeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { Input } from "../components/ui/Input";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useToast } from "../components/ui/Toast";

// Same placeholder coordinates as HomePage — see the comment there.
const DEFAULT_LAT = 19.076;
const DEFAULT_LNG = 72.8777;

export function SearchPage() {
  const { deliveryState } = useAuth();
  const { addItem } = useCart();
  const { showToast } = useToast();
  const [query, setQuery] = useState("");
  const [listings, setListings] = useState<ListingCardType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!deliveryState) return;
    setLoading(true);
    setError(null);
    // NOTE: there is no backend text-search endpoint yet — this loads
    // every listing for the delivery state and filters client-side.
    // Fine at MVP catalog size; replace with a real `GET
    // /v1/search/listings?q=` once the catalog is large enough that
    // shipping the whole thing to the client stops being reasonable.
    api
      .listListings(DEFAULT_LAT, DEFAULT_LNG, deliveryState)
      .then(setListings)
      .catch((err) => setError(err instanceof ApiRequestError ? err.message : "Couldn't load products."))
      .finally(() => setLoading(false));
  }, [deliveryState]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return listings;
    return listings.filter(
      (l) => l.name.toLowerCase().includes(q) || l.brand.toLowerCase().includes(q) || l.category.toLowerCase().includes(q)
    );
  }, [listings, query]);

  function handleAdd(listing: ListingCardType) {
    const result = addItem(listing);
    showToast(result.ok ? `Added ${listing.name}` : result.reason ?? "Couldn't add this item.", result.ok ? "success" : "error");
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <p className="label-eyebrow">Search</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">Find something specific</h1>

      <div className="mt-4 max-w-md">
        <Input
          type="search"
          placeholder="Search by name, brand, or category…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
      </div>

      <div className="mt-6">
        {!deliveryState && (
          <EmptyState title="Set your delivery location" body="Verify your state to search what's available near you." />
        )}

        {deliveryState && loading && <SkeletonCardGrid />}

        {deliveryState && !loading && error && <EmptyState title="Couldn't load products" body={error} />}

        {deliveryState && !loading && !error && filtered.length === 0 && (
          <EmptyState
            title={query ? "No matches" : "Nothing available here yet"}
            body={query ? `Nothing matched "${query}".` : "No stores are currently serviceable for your state."}
          />
        )}

        {deliveryState && !loading && !error && filtered.length > 0 && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {filtered.map((listing) => (
              <ProductCard key={listing.listing_id} listing={listing} onAdd={handleAdd} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
