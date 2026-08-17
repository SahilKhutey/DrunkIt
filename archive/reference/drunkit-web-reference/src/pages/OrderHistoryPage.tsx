import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { OrderSummary } from "../types/api";

const STATUS_LABEL: Record<string, string> = {
  CREATED: "Created",
  ELIGIBILITY_REQUIRED: "Verification needed",
  CONFIRMED: "Confirmed",
  PREPARING: "Preparing",
  READY_FOR_PICKUP: "Ready for pickup",
  OUT_FOR_DELIVERY: "Out for delivery",
  DELIVERED: "Delivered",
  CANCELLED: "Cancelled",
  FAILED: "Failed",
};

export function OrderHistoryPage() {
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listOrders()
      .then(setOrders)
      .catch((err) => setError(err instanceof ApiRequestError ? err.message : "Couldn't load orders."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <h1 className="font-display text-2xl text-parchment">Your orders</h1>

      {loading && <p className="mt-6 text-sm text-parchment/50">Loading…</p>}
      {error && <p className="mt-6 text-sm text-rust-400">{error}</p>}

      {!loading && !error && orders.length === 0 && (
        <div className="mt-10 flex flex-col items-center gap-2 text-center">
          <p className="text-parchment/70">No orders yet.</p>
          <Link to="/" className="text-sm text-brass-400 hover:text-brass-300">
            Start browsing →
          </Link>
        </div>
      )}

      <div className="mt-6 flex flex-col gap-2">
        {orders.map((order) => (
          <Link
            key={order.id}
            to={`/orders/${order.id}`}
            className="flex items-center justify-between rounded-lg border border-ink-700 bg-ink-800/50 px-4 py-3 hover:border-brass-600/40 transition-colors"
          >
            <div>
              <p className="text-sm text-parchment">#{order.id.slice(0, 8)}</p>
              <p className="text-xs text-parchment/50">
                {order.item_count} items · {new Date(order.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <p className="font-mono text-sm text-parchment">₹{order.total.toFixed(0)}</p>
              <p className="text-xs text-brass-400">{STATUS_LABEL[order.status] ?? order.status}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
