import { useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { OrderView, DeliveryView } from "../types/api";

const TIMELINE_STEPS: { status: DeliveryView["status"]; label: string }[] = [
  { status: "REQUESTED", label: "Order confirmed" },
  { status: "ASSIGNED", label: "Driver assigned" },
  { status: "PICKED_UP", label: "Picked up" },
  { status: "IN_TRANSIT", label: "On the way" },
  { status: "ARRIVING", label: "Arriving" },
  { status: "HANDOFF_VERIFICATION", label: "Verifying handoff" },
  { status: "DELIVERED", label: "Delivered" },
];

function stepIndex(status: DeliveryView["status"] | undefined): number {
  if (!status) return 0;
  const i = TIMELINE_STEPS.findIndex((s) => s.status === status);
  return i === -1 ? 0 : i;
}

export function OrderTrackingPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const [order, setOrder] = useState<OrderView | null>(null);
  const [delivery, setDelivery] = useState<DeliveryView | null>(null);
  const [error, setError] = useState<string | null>(null);
  // The setInterval callback closes over whatever `delivery` was at
  // effect-setup time (always null, since the effect only depends on
  // orderId). A ref stays current across renders without re-running
  // the effect, so the "stop polling once delivered" check actually
  // sees the latest status instead of being permanently stale.
  const deliveryStatusRef = useRef<DeliveryView["status"] | null>(null);

  useEffect(() => {
    deliveryStatusRef.current = delivery?.status ?? null;
  }, [delivery]);

  useEffect(() => {
    if (!orderId) return;
    let cancelled = false;

    async function load() {
      try {
        const [o, d] = await Promise.all([api.getOrder(orderId!), api.getDelivery(orderId!)]);
        if (!cancelled) {
          setOrder(o);
          setDelivery(d);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiRequestError ? err.message : "Couldn't load this order.");
        }
      }
    }

    load();
    // Poll while the delivery is still active — a real deployment
    // would use WebSockets/SSE here; polling is the right tradeoff
    // for an MVP's traffic volume.
    const interval = setInterval(() => {
      const status = deliveryStatusRef.current;
      if (status && ["DELIVERED", "FAILED", "CANCELLED"].includes(status)) {
        clearInterval(interval);
        return;
      }
      load();
    }, 4000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [orderId]);

  if (error) {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <p className="text-parchment/70">{error}</p>
        <Link to="/orders" className="mt-2 inline-block text-sm text-brass-400 hover:text-brass-300">
          View your orders
        </Link>
      </div>
    );
  }

  if (!order || !delivery) {
    return <div className="mx-auto max-w-lg px-4 py-20 text-center text-parchment/50">Loading…</div>;
  }

  const currentStep = stepIndex(delivery.status);
  const failed = delivery.status === "FAILED" || delivery.status === "CANCELLED";

  return (
    <div className="mx-auto max-w-lg px-4 py-6">
      <p className="label-eyebrow">Order</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">#{order.id.slice(0, 8)}</h1>
      <p className="mt-1 text-sm text-parchment/50">
        {order.items.reduce((n, i) => n + i.quantity, 0)} items · ₹{order.total.toFixed(0)}
      </p>

      {failed ? (
        <div className="mt-6 rounded-lg border border-rust-600/30 bg-rust-500/5 px-4 py-3">
          <p className="text-sm text-rust-400">
            {delivery.failure_reason ?? "This delivery could not be completed."}
          </p>
        </div>
      ) : (
        <div className="mt-8 flex flex-col gap-1">
          {TIMELINE_STEPS.map((step, i) => {
            const done = i <= currentStep;
            return (
              <div key={step.status} className="flex items-center gap-3">
                <div className="flex flex-col items-center">
                  <div
                    className={`h-3 w-3 rounded-full border-2 ${
                      done ? "border-brass-500 bg-brass-500" : "border-ink-600 bg-ink-800"
                    }`}
                  />
                  {i < TIMELINE_STEPS.length - 1 && (
                    <div className={`h-8 w-0.5 ${done ? "bg-brass-500/50" : "bg-ink-700"}`} />
                  )}
                </div>
                <span className={`pb-8 text-sm ${done ? "text-parchment" : "text-parchment/40"}`}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {!failed && delivery.status !== "DELIVERED" && delivery.eta_min_minutes !== null && (
        <p className="text-sm text-parchment/50 font-mono">
          Arriving in {delivery.eta_min_minutes}–{delivery.eta_max_minutes} min
        </p>
      )}

      <div className="mt-6 rounded-xl border border-ink-700 bg-ink-800/50 p-4">
        <p className="label-eyebrow mb-2">Items</p>
        {order.items.map((item) => (
          <div key={item.product_id} className="flex justify-between py-1 text-sm">
            <span className="text-parchment/80">
              {item.product_name} × {item.quantity}
            </span>
            <span className="font-mono text-parchment/60">
              ₹{(item.unit_price * item.quantity).toFixed(0)}
            </span>
          </div>
        ))}
        <div className="mt-2 flex justify-between border-t border-ink-700 pt-2 text-sm font-mono">
          <span className="text-parchment/60">Delivery fee</span>
          <span className="text-parchment/60">₹{order.delivery_fee.toFixed(0)}</span>
        </div>
        <div className="flex justify-between text-sm font-mono text-parchment">
          <span>Total</span>
          <span>₹{order.total.toFixed(0)}</span>
        </div>
      </div>

      <Link to="/orders" className="mt-4 inline-block text-sm text-brass-400 hover:text-brass-300">
        ← All orders
      </Link>
    </div>
  );
}
