"use client";

import React, { useEffect, useState } from "react";
import { ProductItem } from "./ProductCard";

interface StoreAvailabilityItem {
  retailer_sku_id: string;
  sku_id: string;
  sku_code: string;
  volume_ml: number;
  location_id: string;
  location_name: string;
  city: string;
  state_code: string;
  distance_km: number | null;
  availability_status: string;
  quantity: number;
  amount_minor: number;
  currency: string;
  price_formatted: string;
}

interface AvailabilityModalProps {
  product: ProductItem | null;
  onClose: () => void;
  onAddToCart: (skuId: string, locationId: string) => Promise<void>;
}

export default function AvailabilityModal({ product, onClose, onAddToCart }: AvailabilityModalProps) {
  const [stores, setStores] = useState<StoreAvailabilityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingSku, setAddingSku] = useState<string | null>(null);

  useEffect(() => {
    if (!product) return;
    setLoading(true);

    fetch(`http://127.0.0.1:8000/api/v1/products/${product.slug}/availability?latitude=22.5516&longitude=88.3524`)
      .then((res) => res.json())
      .then((data) => {
        if (data.stores) {
          setStores(data.stores);
        }
      })
      .catch((err) => console.error("Failed to load store availability:", err))
      .finally(() => setLoading(false));
  }, [product]);

  if (!product) return null;

  const handleAdd = async (skuId: string, locId: string) => {
    setAddingSku(skuId);
    try {
      await onAddToCart(skuId, locId);
    } finally {
      setAddingSku(null);
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
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
        padding: 20,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border-color)",
          borderRadius: 16,
          width: "100%",
          maxWidth: 640,
          maxHeight: "85vh",
          overflowY: "auto",
          padding: 28,
          position: "relative",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
              Live Retail Inventory
            </span>
            <h2 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", marginTop: 2 }}>
              {product.name}
            </h2>
            <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 4 }}>
              Statutory MRP prices and real-time stock at licensed off-shops nearby.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-secondary)",
              fontSize: 24,
              cursor: "pointer",
            }}
          >
            ✕
          </button>
        </div>

        {loading ? (
          <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            Checking nearby licensed stores...
          </div>
        ) : stores.length === 0 ? (
          <div style={{ padding: "30px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            No licensed stores currently have stock mapped in this jurisdiction.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {stores.map((s) => {
              const inStock = s.availability_status === "IN_STOCK";
              const isAdding = addingSku === s.sku_id;

              return (
                <div
                  key={`${s.location_id}-${s.sku_id}`}
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    border: "1px solid var(--border-color)",
                    borderRadius: 12,
                    padding: 16,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 12,
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <h4 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>
                        {s.location_name}
                      </h4>
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: 4,
                          backgroundColor: inStock ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                          color: inStock ? "var(--accent-emerald)" : "var(--accent-ruby)",
                        }}
                      >
                        {inStock ? `${s.quantity} in stock` : "Out of stock"}
                      </span>
                    </div>

                    <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", gap: 12 }}>
                      <span>📍 {s.city}, {s.state_code}</span>
                      {s.distance_km !== null && (
                        <span>🚗 {s.distance_km < 1 ? `${Math.round(s.distance_km * 1000)}m away` : `${s.distance_km} km`}</span>
                      )}
                      <span>📦 {s.volume_ml}ml</span>
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: 11, color: "var(--text-muted)", display: "block" }}>Statutory MRP</span>
                      <span style={{ fontSize: 17, fontWeight: 700, color: "var(--accent-gold)" }}>
                        {s.price_formatted}
                      </span>
                    </div>

                    <button
                      onClick={() => handleAdd(s.sku_id, s.location_id)}
                      disabled={!inStock || isAdding}
                      style={{
                        backgroundColor: inStock ? "var(--accent-gold)" : "var(--bg-card)",
                        color: inStock ? "#0b0c10" : "var(--text-muted)",
                        border: "none",
                        borderRadius: 8,
                        padding: "8px 16px",
                        fontWeight: 700,
                        fontSize: 13,
                        cursor: inStock ? "pointer" : "not-allowed",
                        transition: "all 0.2s",
                      }}
                    >
                      {isAdding ? "Adding..." : inStock ? "Add to Basket" : "Unavailable"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
