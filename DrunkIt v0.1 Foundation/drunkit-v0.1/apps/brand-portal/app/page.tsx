"use client";

import React, { useEffect, useState } from "react";

interface BrandSKUMarketShare {
  sku_id: string;
  sku_code: string;
  product_name: string;
  volume_ml: number;
  orders_count: number;
  units_sold: number;
  gross_revenue_minor: number;
  gross_revenue_formatted: string;
}

interface BrandRegionalDistribution {
  state_code: string;
  state_name: string;
  active_retailers_count: number;
  active_locations_count: number;
  in_stock_ratio: number;
  volume_sold_litres: number;
}

interface BrandTasteRadarVisualization {
  product_id: string;
  product_name: string;
  product_slug: string;
  radar_axes: {
    body: number;
    sweetness: number;
    smokiness: number;
    bitterness: number;
    fruitiness: number;
    spiciness: number;
  };
  category_benchmark: {
    body: number;
    sweetness: number;
    smokiness: number;
    bitterness: number;
    fruitiness: number;
    spiciness: number;
  };
  flavor_tags: string[];
}

interface BrandDashboardData {
  brand_id: string;
  brand_name: string;
  brand_slug: string;
  total_products: number;
  total_skus: number;
  total_licensed_stockists: number;
  total_orders: number;
  total_gross_revenue_minor: number;
  total_gross_revenue_formatted: string;
  top_performing_skus: BrandSKUMarketShare[];
  regional_distribution: BrandRegionalDistribution[];
  taste_radars: BrandTasteRadarVisualization[];
}

interface BrandOption {
  id: string;
  name: string;
  slug: string;
}

export default function BrandPortalHome() {
  const [brands, setBrands] = useState<BrandOption[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<BrandOption | null>(null);
  const [dashboard, setDashboard] = useState<BrandDashboardData | null>(null);
  const [selectedRadarIdx, setSelectedRadarIdx] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);

  // Authenticate as brand manager and load brand dashboard
  useEffect(() => {
    async function initBrandPortal() {
      try {
        // 1. Auto register/login brand manager
        await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "indri.manager@piccadily.in", password: "BrandPassword123!", role: "BRAND_MANAGER" }),
        });
        const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "indri.manager@piccadily.in", password: "BrandPassword123!" }),
        });
        const tok = (await loginRes.json()).access_token;
        setToken(tok);

        // 2. Fetch brands
        const brandsRes = await fetch("http://127.0.0.1:8000/api/v1/brands");
        const brandsData = await brandsRes.json();
        if (Array.isArray(brandsData) && brandsData.length > 0) {
          setBrands(brandsData);
          const defaultBrand = brandsData.find((b: any) => b.slug === "indri-single-malt") || brandsData[0];
          setSelectedBrand(defaultBrand);
          await loadBrandDashboard(defaultBrand.id, tok);
        }
      } catch (err) {
        console.error("Brand Portal initialization error:", err);
      } finally {
        setLoading(false);
      }
    }

    initBrandPortal();
  }, []);

  const loadBrandDashboard = async (brandId: string, tok: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/brand-portal/brands/${brandId}/dashboard`, {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDashboard(data);
      }
    } catch (err) {
      console.error("Error loading brand dashboard:", err);
    }
  };

  const handleBrandChange = async (brandId: string) => {
    const brand = brands.find((b) => b.id === brandId);
    if (brand && token) {
      setSelectedBrand(brand);
      setSelectedRadarIdx(0);
      await loadBrandDashboard(brand.id, token);
    }
  };

  // SVG Radar Visualizer Calculations
  const currentRadar = dashboard?.taste_radars[selectedRadarIdx];
  const center = 120;
  const radius = 90;
  const dimensions = ["body", "sweetness", "smokiness", "bitterness", "fruitiness", "spiciness"];
  const axes = dimensions.map((dim, idx) => ({
    label: dim.charAt(0).toUpperCase() + dim.slice(1),
    key: dim,
    angle: idx * 60,
    spiritVal: currentRadar ? (currentRadar.radar_axes as any)[dim] || 0.5 : 0.5,
    benchVal: currentRadar ? (currentRadar.category_benchmark as any)[dim] || 0.5 : 0.5,
  }));

  const spiritPoints = axes
    .map((a) => {
      const rad = ((a.angle - 90) * Math.PI) / 180;
      const r = radius * a.spiritVal;
      return `${center + r * Math.cos(rad)},${center + r * Math.sin(rad)}`;
    })
    .join(" ");

  const benchPoints = axes
    .map((a) => {
      const rad = ((a.angle - 90) * Math.PI) / 180;
      const r = radius * a.benchVal;
      return `${center + r * Math.cos(rad)},${center + r * Math.sin(rad)}`;
    })
    .join(" ");

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-primary)" }}>
      {/* ────────────────────────────────────────────────────────── */}
      {/* Header */}
      {/* ────────────────────────────────────────────────────────── */}
      <header
        style={{
          backgroundColor: "rgba(20, 23, 33, 0.95)",
          backdropFilter: "blur(8px)",
          borderBottom: "1px solid var(--border-color)",
          padding: "16px 28px",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: 1280,
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 16,
          }}
        >
          {/* Brand Identity */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 24 }}>🥃</span>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 20, fontWeight: 900, color: "var(--text-primary)" }}>
                  Drunk<span style={{ color: "var(--accent-gold)" }}>It</span>
                </span>
                <span
                  style={{
                    backgroundColor: "rgba(229, 169, 60, 0.15)",
                    color: "var(--accent-gold)",
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    textTransform: "uppercase",
                  }}
                >
                  Brand Intelligence
                </span>
              </div>
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                Distillery Analytics & Semantic Radar Benchmarking
              </span>
            </div>
          </div>

          {/* Brand Switcher */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Brand House:</span>
            <select
              value={selectedBrand?.id || ""}
              onChange={(e) => handleBrandChange(e.target.value)}
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px solid var(--border-gold)",
                color: "var(--text-primary)",
                padding: "8px 14px",
                borderRadius: 8,
                fontSize: 13,
                fontWeight: 700,
              }}
            >
              {brands.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────── */}
      {/* KPI Overview Cards */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "28px 28px 0" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 16 }}>
          {/* Gross Revenue */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Total Gross Revenue</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-gold)", marginTop: 6 }}>
              {dashboard?.total_gross_revenue_formatted || "₹0.00"}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              Direct statutory sales volume
            </span>
          </div>

          {/* Customer Orders */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Consumer Orders</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--text-primary)", marginTop: 6 }}>
              {dashboard?.total_orders || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--accent-emerald)", marginTop: 4, display: "block" }}>
              Across active jurisdictions
            </span>
          </div>

          {/* Licensed Stockist Doors */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Licensed Stockists</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-emerald)", marginTop: 6 }}>
              {dashboard?.total_licensed_stockists || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              Store locations carrying SKUs
            </span>
          </div>

          {/* Active SKUs */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Active Portfolio SKUs</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-amber)", marginTop: 6 }}>
              {dashboard?.total_skus || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              Across {dashboard?.total_products || 0} expressions
            </span>
          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* 6-Axis Taste Radar Benchmarking Canvas */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "28px" }}>
        <div
          style={{
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-color)",
            borderRadius: 16,
            padding: 28,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16, marginBottom: 20 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
                Semantic Sensory Intelligence
              </span>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", marginTop: 4 }}>
                6-Axis Taste Radar & Category Benchmarking
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 4 }}>
                Comparing brand expression flavor profiles against peer category benchmark averages.
              </p>
            </div>

            {/* Expression Selector Tabs */}
            {dashboard && dashboard.taste_radars.length > 0 && (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {dashboard.taste_radars.map((r, idx) => (
                  <button
                    key={r.product_id}
                    onClick={() => setSelectedRadarIdx(idx)}
                    style={{
                      backgroundColor: selectedRadarIdx === idx ? "var(--accent-gold)" : "var(--bg-surface)",
                      color: selectedRadarIdx === idx ? "#0b0c10" : "var(--text-secondary)",
                      border: "1px solid",
                      borderColor: selectedRadarIdx === idx ? "var(--accent-gold)" : "var(--border-color)",
                      padding: "8px 16px",
                      borderRadius: 20,
                      fontSize: 13,
                      fontWeight: 700,
                      cursor: "pointer",
                      transition: "all 0.2s",
                    }}
                  >
                    {r.product_name}
                  </button>
                ))}
              </div>
            )}
          </div>

          {currentRadar && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 32, alignItems: "center" }}>
              {/* Radar Graph */}
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <svg width={240} height={240} viewBox="0 0 240 240" style={{ overflow: "visible" }}>
                  {/* Concentric grid */}
                  {[0.25, 0.5, 0.75, 1.0].map((lvl) => (
                    <polygon
                      key={lvl}
                      points={axes
                        .map((a) => {
                          const rad = ((a.angle - 90) * Math.PI) / 180;
                          const r = radius * lvl;
                          return `${center + r * Math.cos(rad)},${center + r * Math.sin(rad)}`;
                        })
                        .join(" ")}
                      fill="none"
                      stroke="var(--border-color)"
                      strokeWidth={1}
                      strokeDasharray={lvl < 1.0 ? "3,3" : "none"}
                    />
                  ))}

                  {/* Spokes and Labels */}
                  {axes.map((a) => {
                    const rad = ((a.angle - 90) * Math.PI) / 180;
                    const x2 = center + radius * Math.cos(rad);
                    const y2 = center + radius * Math.sin(rad);
                    const textX = center + (radius + 20) * Math.cos(rad);
                    const textY = center + (radius + 20) * Math.sin(rad) + 4;
                    return (
                      <g key={a.label}>
                        <line x1={center} y1={center} x2={x2} y2={y2} stroke="var(--border-color)" strokeWidth={1} />
                        <text
                          x={textX}
                          y={textY}
                          fontSize={11}
                          fill="var(--text-secondary)"
                          textAnchor="middle"
                          fontWeight={600}
                        >
                          {a.label}
                        </text>
                      </g>
                    );
                  })}

                  {/* Category Benchmark Polygon (Dashed Blue) */}
                  <polygon
                    points={benchPoints}
                    fill="rgba(59, 130, 246, 0.15)"
                    stroke="var(--accent-blue, #3b82f6)"
                    strokeWidth={1.5}
                    strokeDasharray="4,4"
                  />

                  {/* Spirit Polygon (Gold) */}
                  <polygon
                    points={spiritPoints}
                    fill="rgba(229, 169, 60, 0.35)"
                    stroke="var(--accent-gold)"
                    strokeWidth={2.5}
                  />

                  {/* Spirit Points */}
                  {axes.map((a) => {
                    const rad = ((a.angle - 90) * Math.PI) / 180;
                    const r = radius * a.spiritVal;
                    return (
                      <circle
                        key={a.label}
                        cx={center + r * Math.cos(rad)}
                        cy={center + r * Math.sin(rad)}
                        r={4.5}
                        fill="var(--accent-gold)"
                        stroke="#0b0c10"
                        strokeWidth={1.5}
                      />
                    );
                  })}
                </svg>

                {/* Legend */}
                <div style={{ display: "flex", gap: 20, marginTop: 16, fontSize: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 12, height: 12, backgroundColor: "var(--accent-gold)", borderRadius: 2 }} />
                    <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{currentRadar.product_name}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span style={{ width: 12, height: 2, backgroundColor: "var(--accent-blue, #3b82f6)" }} />
                    <span style={{ color: "var(--text-secondary)" }}>Category Benchmark Average</span>
                  </div>
                </div>
              </div>

              {/* Radar Table Breakdown */}
              <div>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
                  {currentRadar.flavor_tags.map((tag) => (
                    <span
                      key={tag}
                      style={{
                        backgroundColor: "rgba(229, 169, 60, 0.15)",
                        color: "var(--accent-gold)",
                        fontSize: 11,
                        fontWeight: 700,
                        padding: "3px 10px",
                        borderRadius: 12,
                        textTransform: "uppercase",
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {axes.map((a) => {
                    const diff = Math.round((a.spiritVal - a.benchVal) * 100);
                    return (
                      <div
                        key={a.label}
                        style={{
                          backgroundColor: "var(--bg-surface)",
                          borderRadius: 8,
                          padding: "8px 14px",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          fontSize: 13,
                        }}
                      >
                        <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{a.label}</span>
                        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                          <span style={{ color: "var(--accent-gold)", fontWeight: 700 }}>
                            {Math.round(a.spiritVal * 100)}%
                          </span>
                          <span style={{ color: "var(--text-muted)", fontSize: 12 }}>
                            vs benchmark {Math.round(a.benchVal * 100)}%
                          </span>
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              color: diff >= 0 ? "var(--accent-emerald)" : "var(--accent-ruby)",
                            }}
                          >
                            {diff >= 0 ? `+${diff}%` : `${diff}%`}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Top Performing SKUs & Regional Distribution */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "0 28px 60px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: 24 }}>
          {/* Top SKUs */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 14, padding: 24 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 16 }}>
              Top Performing SKUs by Revenue
            </h3>
            {dashboard && dashboard.top_performing_skus.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {dashboard.top_performing_skus.map((sku) => (
                  <div
                    key={sku.sku_id}
                    style={{
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: 10,
                      padding: 14,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>
                        {sku.product_name} ({sku.volume_ml}ml)
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                        Code: {sku.sku_code} • {sku.units_sold} units sold
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 15, fontWeight: 800, color: "var(--accent-gold)" }}>
                        {sku.gross_revenue_formatted}
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        {sku.orders_count} orders
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: "var(--text-muted)", fontSize: 13 }}>No SKU revenue recorded yet.</div>
            )}
          </div>

          {/* Regional Distribution */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 14, padding: 24 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 16 }}>
              Regional Penetration & Stockist Matrix
            </h3>
            {dashboard && dashboard.regional_distribution.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {dashboard.regional_distribution.map((reg) => (
                  <div
                    key={reg.state_code}
                    style={{
                      backgroundColor: "var(--bg-surface)",
                      borderRadius: 10,
                      padding: 14,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>
                        📍 {reg.state_code} ({reg.state_name})
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                        {reg.active_locations_count} licensed doors • In-stock ratio: {Math.round(reg.in_stock_ratio * 100)}%
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 14, fontWeight: 800, color: "var(--accent-emerald)" }}>
                        {reg.volume_sold_litres} L
                      </div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                        Volume Delivered
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: "var(--text-muted)", fontSize: 13 }}>No regional data available.</div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
