"use client";

import React from "react";

export interface ProductItem {
  id: string;
  name: string;
  slug: string;
  brand_name: string | null;
  category_name: string | null;
  product_type: string;
  region: string | null;
  country_of_origin: string;
  abv: string | number | null;
  description?: string;
  taste_profile?: {
    body: number | string | null;
    sweetness: number | string | null;
    smokiness: number | string | null;
    fruitiness: number | string | null;
    spiciness: number | string | null;
  } | null;
}

interface ProductCardProps {
  product: ProductItem;
  onCheckAvailability: (product: ProductItem) => void;
}

export default function ProductCard({ product, onCheckAvailability }: ProductCardProps) {
  return (
    <div
      style={{
        backgroundColor: "var(--bg-card)",
        border: "1px solid var(--border-color)",
        borderRadius: 14,
        padding: 20,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        transition: "transform 0.2s, border-color 0.2s, box-shadow 0.2s",
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.borderColor = "var(--border-gold)";
        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.35)";
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.borderColor = "var(--border-color)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.08em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
            {product.brand_name || product.product_type}
          </span>
          <span style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-color)",
            color: "var(--text-secondary)",
            fontSize: 11,
            fontWeight: 600,
            padding: "2px 8px",
            borderRadius: 12,
          }}>
            {product.abv ? `${product.abv}% ABV` : "40% ABV"}
          </span>
        </div>

        <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 8, lineHeight: 1.3 }}>
          {product.name}
        </h3>

        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
          {product.region && (
            <span style={{ fontSize: 11, color: "var(--text-secondary)", backgroundColor: "var(--bg-surface)", padding: "2px 8px", borderRadius: 4 }}>
              📍 {product.region}
            </span>
          )}
          <span style={{ fontSize: 11, color: "var(--text-secondary)", backgroundColor: "var(--bg-surface)", padding: "2px 8px", borderRadius: 4 }}>
            🏷️ {product.product_type}
          </span>
        </div>

        {/* Mini Taste Bars */}
        {product.taste_profile && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 16, backgroundColor: "var(--bg-surface)", padding: 10, borderRadius: 8 }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)" }}>
                <span>Smoke</span>
                <span>{Math.round(Number(product.taste_profile.smokiness || 0.5) * 100)}%</span>
              </div>
              <div style={{ height: 4, backgroundColor: "var(--bg-card)", borderRadius: 2, overflow: "hidden", marginTop: 2 }}>
                <div style={{ width: `${Number(product.taste_profile.smokiness || 0.5) * 100}%`, height: "100%", backgroundColor: "var(--accent-gold)" }} />
              </div>
            </div>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)" }}>
                <span>Body</span>
                <span>{Math.round(Number(product.taste_profile.body || 0.5) * 100)}%</span>
              </div>
              <div style={{ height: 4, backgroundColor: "var(--bg-card)", borderRadius: 2, overflow: "hidden", marginTop: 2 }}>
                <div style={{ width: `${Number(product.taste_profile.body || 0.5) * 100}%`, height: "100%", backgroundColor: "var(--accent-amber)" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      <button
        onClick={() => onCheckAvailability(product)}
        style={{
          backgroundColor: "var(--bg-surface)",
          color: "var(--text-primary)",
          border: "1px solid var(--border-gold)",
          borderRadius: 8,
          padding: "10px 16px",
          fontWeight: 600,
          fontSize: 13,
          cursor: "pointer",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 6,
          transition: "all 0.2s",
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.backgroundColor = "var(--accent-gold)";
          e.currentTarget.style.color = "#0b0c10";
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.backgroundColor = "var(--bg-surface)";
          e.currentTarget.style.color = "var(--text-primary)";
        }}
      >
        <span>📍</span> Check Store Stock
      </button>
    </div>
  );
}
