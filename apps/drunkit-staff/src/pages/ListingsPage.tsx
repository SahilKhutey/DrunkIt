import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { AdminListingView, StoreView, ProductView } from "../types/api";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Modal } from "../components/ui/Modal";
import { Badge } from "../components/ui/Badge";
import { useToast } from "../components/ui/Toast";
import { useAuth } from "../context/AuthContext";

const AVAILABILITY_TONE = { IN_STOCK: "sage", LOW_STOCK: "copper", OUT_OF_STOCK: "rust" } as const;

export function ListingsPage() {
  const { showToast } = useToast();
  const { isPlatformAdmin } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const storeId = searchParams.get("store_id") ?? "";

  const [stores, setStores] = useState<StoreView[]>([]);
  const [products, setProducts] = useState<ProductView[]>([]);
  const [listings, setListings] = useState<AdminListingView[]>([]);
  const [loading, setLoading] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [newProductOpen, setNewProductOpen] = useState(false);

  function loadProducts() {
    api.listProducts().then(setProducts).catch(() => {});
  }

  useEffect(() => {
    api.listStores().then(setStores).catch(() => {});
    loadProducts();
  }, []);

  function loadListings(id: string) {
    if (!id) return;
    setLoading(true);
    api
      .listListings(id)
      .then(setListings)
      .catch((err) => showToast(err instanceof ApiRequestError ? err.message : "Couldn't load listings.", "error"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    if (storeId) loadListings(storeId);
  }, [storeId]);

  return (
    <div>
      <p className="label-eyebrow">Listings</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">Store catalog</h1>

      <div className="mt-4 flex items-end justify-between gap-4">
        <div className="max-w-xs flex-1">
          <Select
            label="Store"
            value={storeId}
            onChange={(e) => setSearchParams(e.target.value ? { store_id: e.target.value } : {})}
          >
            <option value="">Select a store</option>
            {stores.map((s) => (
              <option key={s.id} value={s.id}>{s.name} — {s.city}</option>
            ))}
          </Select>
        </div>
        {isPlatformAdmin && (
          <Button variant="secondary" size="sm" onClick={() => setNewProductOpen(true)}>
            New product
          </Button>
        )}
      </div>

      {storeId && (
        <>
          <div className="mt-6 flex justify-end">
            <Button onClick={() => setEditOpen(true)}>Add / update listing</Button>
          </div>

          <div className="mt-3 overflow-x-auto rounded-xl border border-ink-700">
            <table className="data-table w-full">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Pack size</th>
                  <th>MRP</th>
                  <th>Selling price</th>
                  <th>Stock</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={6} className="text-center text-parchment/40">Loading…</td></tr>
                )}
                {!loading && listings.length === 0 && (
                  <tr><td colSpan={6} className="text-center text-parchment/40">No listings at this store yet.</td></tr>
                )}
                {listings.map((l) => {
                  const availability = l.quantity == null ? null : l.quantity <= 0 ? "OUT_OF_STOCK" : l.quantity <= 5 ? "LOW_STOCK" : "IN_STOCK";
                  return (
                    <tr key={l.listing_id}>
                      <td className="font-medium text-parchment">{l.brand} — {l.product_name}</td>
                      <td className="text-parchment/60">{l.pack_size}</td>
                      <td className="font-mono text-parchment/60">{l.mrp != null ? `₹${l.mrp.toFixed(0)}` : "—"}</td>
                      <td className="font-mono text-brass-400">{l.selling_price != null ? `₹${l.selling_price.toFixed(0)}` : "—"}</td>
                      <td className="font-mono text-parchment/60">{l.quantity ?? "—"}</td>
                      <td>{availability && <Badge tone={AVAILABILITY_TONE[availability]}>{availability.replace("_", " ")}</Badge>}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {editOpen && (
        <ListingFormModal
          storeId={storeId}
          products={products}
          onClose={() => setEditOpen(false)}
          onSaved={() => loadListings(storeId)}
        />
      )}

      {newProductOpen && (
        <NewProductModal
          onClose={() => setNewProductOpen(false)}
          onCreated={loadProducts}
        />
      )}
    </div>
  );
}

function NewProductModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [category, setCategory] = useState("");
  const [variant, setVariant] = useState("");
  const [packSize, setPackSize] = useState("");
  const [abv, setAbv] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.createProduct({
        name,
        brand,
        category,
        variant: variant || undefined,
        pack_size: packSize,
        abv_percent: abv ? parseFloat(abv) : undefined,
      });
      showToast("Product added to catalog", "success");
      onCreated();
      onClose();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't create product.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="New product">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <p className="text-xs text-parchment/50">
          Added to the shared platform catalog — every retailer can then list it at their own
          stores with their own price and stock.
        </p>
        <div className="grid grid-cols-2 gap-3">
          <Input label="Brand" required value={brand} onChange={(e) => setBrand(e.target.value)} />
          <Input label="Category" required value={category} onChange={(e) => setCategory(e.target.value)} placeholder="beer, whisky, wine…" />
        </div>
        <Input label="Product name" required value={name} onChange={(e) => setName(e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Input label="Pack size" required value={packSize} onChange={(e) => setPackSize(e.target.value)} placeholder="750 ml" />
          <Input label="Variant (optional)" value={variant} onChange={(e) => setVariant(e.target.value)} />
        </div>
        <Input label="ABV % (optional)" type="number" step="0.1" value={abv} onChange={(e) => setAbv(e.target.value)} />
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={busy}>Add to catalog</Button>
        </div>
      </form>
    </Modal>
  );
}

function ListingFormModal({
  storeId,
  products,
  onClose,
  onSaved,
}: {
  storeId: string;
  products: ProductView[];
  onClose: () => void;
  onSaved: () => void;
}) {
  const { showToast } = useToast();
  const [productId, setProductId] = useState("");
  const [mrp, setMrp] = useState("");
  const [sellingPrice, setSellingPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.upsertListing({
        store_id: storeId,
        product_id: productId,
        mrp: parseFloat(mrp),
        selling_price: parseFloat(sellingPrice),
        quantity: parseInt(quantity, 10),
      });
      showToast("Listing saved", "success");
      onClose();
      onSaved();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't save listing.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Add / update listing">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <Select label="Product" required value={productId} onChange={(e) => setProductId(e.target.value)}>
          <option value="" disabled>Select a product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>{p.brand} — {p.name} ({p.pack_size})</option>
          ))}
        </Select>
        <div className="grid grid-cols-2 gap-3">
          <Input label="MRP (₹)" type="number" step="0.01" required value={mrp} onChange={(e) => setMrp(e.target.value)} />
          <Input label="Selling price (₹)" type="number" step="0.01" required value={sellingPrice} onChange={(e) => setSellingPrice(e.target.value)} />
        </div>
        <Input label="Stock quantity" type="number" required value={quantity} onChange={(e) => setQuantity(e.target.value)} />
        <p className="text-xs text-parchment/40">
          Re-submitting for a product already listed at this store updates its price and stock —
          it doesn't create a duplicate.
        </p>
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={busy}>Save</Button>
        </div>
      </form>
    </Modal>
  );
}
