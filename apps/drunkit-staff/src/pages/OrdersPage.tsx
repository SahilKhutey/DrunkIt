import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { AdminOrderView, StoreView } from "../types/api";
import { Select } from "../components/ui/Select";
import { Badge } from "../components/ui/Badge";
import { useToast } from "../components/ui/Toast";

const STATUS_TONE: Record<string, "neutral" | "brass" | "sage" | "rust" | "copper"> = {
  CREATED: "neutral",
  CONFIRMED: "brass",
  PREPARING: "copper",
  READY_FOR_PICKUP: "copper",
  OUT_FOR_DELIVERY: "brass",
  DELIVERED: "sage",
  CANCELLED: "neutral",
  FAILED: "rust",
};

export function OrdersPage() {
  const { showToast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  const storeId = searchParams.get("store_id") ?? "";

  const [stores, setStores] = useState<StoreView[]>([]);
  const [orders, setOrders] = useState<AdminOrderView[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.listStores().then(setStores).catch(() => {});
  }, []);

  useEffect(() => {
    if (!storeId) return;
    setLoading(true);
    api
      .listOrders(storeId)
      .then(setOrders)
      .catch((err) => showToast(err instanceof ApiRequestError ? err.message : "Couldn't load orders.", "error"))
      .finally(() => setLoading(false));
  }, [storeId]);

  return (
    <div>
      <p className="label-eyebrow">Orders</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">Order fulfillment</h1>

      <div className="mt-4 max-w-xs">
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

      {storeId && (
        <div className="mt-6 flex flex-col gap-3">
          {loading && <p className="text-sm text-parchment/40">Loading…</p>}
          {!loading && orders.length === 0 && (
            <p className="text-sm text-parchment/40">No orders at this store yet.</p>
          )}
          {orders.map((o) => (
            <div key={o.id} className="rounded-xl border border-ink-700 bg-ink-800/60 p-4">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-parchment/50">#{o.id.slice(0, 8)}</span>
                <Badge tone={STATUS_TONE[o.status] ?? "neutral"}>{o.status.replace(/_/g, " ")}</Badge>
              </div>
              <p className="mt-2 text-sm text-parchment/70">{o.delivery_address}</p>
              <ul className="mt-2 flex flex-col gap-1">
                {o.items.map((item, i) => (
                  <li key={i} className="flex justify-between text-xs text-parchment/60">
                    <span>{item.quantity}× {item.product_name}</span>
                    <span className="font-mono">₹{(item.unit_price * item.quantity).toFixed(0)}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-2 flex justify-between border-t border-ink-700 pt-2 text-sm">
                <span className="text-parchment/50">{new Date(o.created_at).toLocaleString()}</span>
                <span className="font-mono text-brass-400">₹{o.total.toFixed(0)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
