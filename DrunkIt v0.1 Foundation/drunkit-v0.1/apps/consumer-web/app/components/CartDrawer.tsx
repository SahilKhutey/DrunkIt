"use client";

import React, { useState } from "react";

export interface CartItemData {
  id: string;
  sku_id: string;
  canonical_code: string;
  product_name: string;
  volume_ml: number;
  retailer_location_id: string;
  retailer_name: string;
  quantity: number;
  unit_price_minor: number;
  unit_price_formatted: string;
  total_price_minor: number;
  total_price_formatted: string;
}

export interface CartData {
  id: string;
  items: CartItemData[];
  item_count: number;
  subtotal_minor: number;
  subtotal_formatted: string;
  total_volume_ml: number;
}

interface CartDrawerProps {
  isOpen: boolean;
  cart: CartData | null;
  onClose: () => void;
  onRemoveItem: (itemId: string) => Promise<void>;
  onCheckoutSuccess: (order: any) => void;
}

export default function CartDrawer({
  isOpen,
  cart,
  onClose,
  onRemoveItem,
  onCheckoutSuccess,
}: CartDrawerProps) {
  const [ageVerified, setAgeVerified] = useState(false);
  const [channel, setChannel] = useState("ONLINE_ORDER");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [placedOrder, setPlacedOrder] = useState<any | null>(null);

  if (!isOpen) return null;

  const handleCheckout = async () => {
    if (!ageVerified) {
      setError("You must verify that you meet the statutory legal drinking age (21+) before checking out.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // First ensure consumer auth token
      const authRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "shopper@drunkit.in", password: "ShopperPassword123!" }),
      });
      const token = (await authRes.json()).access_token;

      const idempotencyKey = `web-checkout-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const checkoutRes = await fetch("http://127.0.0.1:8000/api/v1/cart/checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          idempotency_key: idempotencyKey,
          channel: channel,
          consumer_age: 25,
          is_age_verified: true,
        }),
      });

      const orderData = await checkoutRes.json();
      if (!checkoutRes.ok) {
        throw new Error(orderData?.error?.message || "Checkout failed due to compliance validation.");
      }

      setPlacedOrder(orderData);
      onCheckoutSuccess(orderData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(4px)",
        display: "flex",
        justifyContent: "flex-end",
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "var(--bg-card)",
          borderLeft: "1px solid var(--border-color)",
          width: "100%",
          maxWidth: 480,
          height: "100%",
          overflowY: "auto",
          padding: 28,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div>
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
                Active Basket
              </span>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)" }}>
                Shopping Cart
              </h2>
            </div>
            <button
              onClick={onClose}
              style={{ background: "none", border: "none", color: "var(--text-secondary)", fontSize: 24, cursor: "pointer" }}
            >
              ✕
            </button>
          </div>

          {/* Success State */}
          {placedOrder ? (
            <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--accent-emerald)", borderRadius: 12, padding: 24, textAlign: "center" }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎉</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--accent-emerald)", marginBottom: 6 }}>
                Order Confirmed!
              </h3>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
                Your order has passed deterministic compliance verification and has been sent to {placedOrder.retailer_name}.
              </p>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 20, textAlign: "left", backgroundColor: "var(--bg-card)", padding: 12, borderRadius: 8 }}>
                <div><strong>Order ID:</strong> {placedOrder.id}</div>
                <div><strong>Total:</strong> {placedOrder.total_formatted}</div>
                <div><strong>Compliance Ref:</strong> {placedOrder.compliance_decision_id}</div>
              </div>
              <button
                onClick={() => {
                  setPlacedOrder(null);
                  onClose();
                }}
                style={{
                  backgroundColor: "var(--accent-gold)",
                  color: "#0b0c10",
                  fontWeight: 700,
                  fontSize: 14,
                  padding: "10px 20px",
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                }}
              >
                Back to Spirits
              </button>
            </div>
          ) : !cart || cart.items.length === 0 ? (
            <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-secondary)" }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>🛍️</div>
              <p style={{ fontSize: 16, fontWeight: 600 }}>Your basket is empty</p>
              <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
                Explore the catalog and select nearby store stock.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {/* Items List */}
              {cart.items.map((item) => (
                <div
                  key={item.id}
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    border: "1px solid var(--border-color)",
                    borderRadius: 10,
                    padding: 14,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)" }}>
                      {item.product_name}
                    </h4>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 2 }}>
                      <span>{item.quantity} × {item.volume_ml}ml</span> • <span>📍 {item.retailer_name}</span>
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "var(--accent-gold)", marginTop: 4 }}>
                      {item.total_price_formatted}
                    </div>
                  </div>

                  <button
                    onClick={() => onRemoveItem(item.id)}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--accent-ruby)",
                      cursor: "pointer",
                      fontSize: 16,
                      padding: 6,
                    }}
                    title="Remove item"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer / Compliance Gate */}
        {!placedOrder && cart && cart.items.length > 0 && (
          <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: 20, marginTop: 24 }}>
            {/* Totals */}
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontSize: 13, color: "var(--text-secondary)" }}>
              <span>Total Volume</span>
              <span>{cart.total_volume_ml} ml</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16, fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>
              <span>Subtotal (MRP)</span>
              <span style={{ color: "var(--accent-gold)" }}>{cart.subtotal_formatted}</span>
            </div>

            {/* Error Banner */}
            {error && (
              <div style={{ backgroundColor: "rgba(239, 68, 68, 0.15)", border: "1px solid var(--accent-ruby)", borderRadius: 8, padding: 10, color: "var(--accent-ruby)", fontSize: 12, marginBottom: 14 }}>
                ⚠️ {error}
              </div>
            )}

            {/* Compliance Gate Controls */}
            <div style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border-color)", borderRadius: 10, padding: 14, marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--accent-gold)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>
                Statutory Compliance Gate
              </div>

              {/* Age Check */}
              <label style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12, color: "var(--text-primary)", cursor: "pointer", marginBottom: 10 }}>
                <input
                  type="checkbox"
                  checked={ageVerified}
                  onChange={(e) => setAgeVerified(e.target.checked)}
                  style={{ marginTop: 2, accentColor: "var(--accent-gold)" }}
                />
                <span>I certify that I am 21+ years of age and comply with state excise laws.</span>
              </label>

              {/* Channel Selector */}
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 4 }}>Fulfilment Channel</div>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                style={{
                  width: "100%",
                  backgroundColor: "var(--bg-card)",
                  border: "1px solid var(--border-color)",
                  color: "var(--text-primary)",
                  padding: "6px 10px",
                  borderRadius: 6,
                  fontSize: 13,
                }}
              >
                <option value="ONLINE_ORDER">Online Ordering (Licensed Retailer Counter)</option>
                <option value="HOME_DELIVERY">Home Delivery (Where Permitted by State Law)</option>
                <option value="IN_STORE">In-Store Reserve & Pickup</option>
              </select>
            </div>

            {/* Checkout Button */}
            <button
              onClick={handleCheckout}
              disabled={loading}
              style={{
                width: "100%",
                backgroundColor: "var(--accent-gold)",
                color: "#0b0c10",
                fontWeight: 700,
                fontSize: 15,
                padding: "14px",
                borderRadius: 10,
                border: "none",
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: "0 4px 14px rgba(229, 169, 60, 0.35)",
                transition: "all 0.2s",
              }}
            >
              {loading ? "Verifying Compliance..." : `Place Order • ${cart.subtotal_formatted}`}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
