"use client";

import React, { useState } from "react";

interface TasteVector {
  body: number;
  sweetness: number;
  smokiness: number;
  bitterness: number;
  fruitiness: number;
  spiciness: number;
}

interface MatchedSpirit {
  product: {
    id: string;
    name: string;
    slug: string;
    brand_name: string | null;
    product_type: string;
    abv: string | number | null;
  };
  similarity_score: number;
  match_reasons: string[];
}

interface TasteRadarWidgetProps {
  onSelectProduct: (slug: string) => void;
}

const PRESETS: Record<string, TasteVector> = {
  "Peat & Smoke": { body: 0.90, sweetness: 0.65, smokiness: 0.85, bitterness: 0.25, fruitiness: 0.70, spiciness: 0.80 },
  "Smooth & Silky": { body: 0.60, sweetness: 0.75, smokiness: 0.15, bitterness: 0.15, fruitiness: 0.70, spiciness: 0.40 },
  "Botanical Gin": { body: 0.70, sweetness: 0.40, smokiness: 0.10, bitterness: 0.35, fruitiness: 0.85, spiciness: 0.80 },
  "Bold Agave": { body: 0.80, sweetness: 0.50, smokiness: 0.25, bitterness: 0.20, fruitiness: 0.65, spiciness: 0.70 },
};

export default function TasteRadarWidget({ onSelectProduct }: TasteRadarWidgetProps) {
  const [taste, setTaste] = useState<TasteVector>({
    body: 0.85,
    sweetness: 0.60,
    smokiness: 0.75,
    bitterness: 0.25,
    fruitiness: 0.70,
    spiciness: 0.75,
  });

  const [matches, setMatches] = useState<MatchedSpirit[]>([]);
  const [loading, setLoading] = useState(false);

  const updateDimension = (key: keyof TasteVector, val: number) => {
    setTaste((prev) => ({ ...prev, [key]: val }));
  };

  const applyPreset = (presetName: string) => {
    if (PRESETS[presetName]) {
      setTaste(PRESETS[presetName]);
    }
  };

  const handleMatch = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/discovery/taste-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          body: taste.body,
          sweetness: taste.sweetness,
          smokiness: taste.smokiness,
          bitterness: taste.bitterness,
          fruitiness: taste.fruitiness,
          spiciness: taste.spiciness,
          limit: 4,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setMatches(data);
      }
    } catch (err) {
      console.error("Failed to match taste profile:", err);
    } finally {
      setLoading(false);
    }
  };

  // SVG Radar Visualizer Points Calculation
  const center = 110;
  const radius = 80;
  const axes = [
    { label: "Body", val: taste.body, angle: 0 },
    { label: "Sweetness", val: taste.sweetness, angle: 60 },
    { label: "Smokiness", val: taste.smokiness, angle: 120 },
    { label: "Bitterness", val: taste.bitterness, angle: 180 },
    { label: "Fruitiness", val: taste.fruitiness, angle: 240 },
    { label: "Spiciness", val: taste.spiciness, angle: 300 },
  ];

  const polygonPoints = axes
    .map((a) => {
      const rad = ((a.angle - 90) * Math.PI) / 180;
      const r = radius * a.val;
      const x = center + r * Math.cos(rad);
      const y = center + r * Math.sin(rad);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div style={{
      backgroundColor: "var(--bg-card)",
      border: "1px solid var(--border-color)",
      borderRadius: 16,
      padding: "28px",
      margin: "32px 0",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16, marginBottom: 24 }}>
        <div>
          <span style={{ fontSize: 12, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
            Semantic Taste Intelligence
          </span>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: "var(--text-primary)", marginTop: 4 }}>
            6-Axis Flavor Radar Matcher
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, marginTop: 4 }}>
            Adjust your flavor preferences to compute real-time vector affinity against our master spirit catalog.
          </p>
        </div>

        {/* Quick Presets */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {Object.keys(PRESETS).map((p) => (
            <button
              key={p}
              onClick={() => applyPreset(p)}
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px solid var(--border-color)",
                color: "var(--text-secondary)",
                padding: "6px 14px",
                borderRadius: 20,
                fontSize: 13,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseOver={(e) => (e.currentTarget.style.borderColor = "var(--accent-gold)")}
              onMouseOut={(e) => (e.currentTarget.style.borderColor = "var(--border-color)")}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 32, alignItems: "center" }}>
        {/* Radar Graphic */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <svg width={220} height={220} viewBox="0 0 220 220" style={{ overflow: "visible" }}>
            {/* Background concentric polygons */}
            {[0.25, 0.5, 0.75, 1.0].map((level) => (
              <polygon
                key={level}
                points={axes
                  .map((a) => {
                    const rad = ((a.angle - 90) * Math.PI) / 180;
                    const r = radius * level;
                    return `${center + r * Math.cos(rad)},${center + r * Math.sin(rad)}`;
                  })
                  .join(" ")}
                fill="none"
                stroke="var(--border-color)"
                strokeWidth={1}
                strokeDasharray={level < 1.0 ? "3,3" : "none"}
              />
            ))}

            {/* Axis spokes */}
            {axes.map((a) => {
              const rad = ((a.angle - 90) * Math.PI) / 180;
              const x2 = center + radius * Math.cos(rad);
              const y2 = center + radius * Math.sin(rad);
              const textX = center + (radius + 18) * Math.cos(rad);
              const textY = center + (radius + 18) * Math.sin(rad) + 4;
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

            {/* Active taste polygon */}
            <polygon
              points={polygonPoints}
              fill="rgba(229, 169, 60, 0.35)"
              stroke="var(--accent-gold)"
              strokeWidth={2.5}
            />

            {/* Points */}
            {axes.map((a) => {
              const rad = ((a.angle - 90) * Math.PI) / 180;
              const r = radius * a.val;
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
        </div>

        {/* Sliders */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {axes.map((a) => (
            <div key={a.label}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 4 }}>
                <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{a.label}</span>
                <span style={{ color: "var(--accent-gold)", fontWeight: 700 }}>
                  {Math.round(a.val * 100)}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={Math.round(a.val * 100)}
                onChange={(e) => updateDimension(a.label.toLowerCase() as keyof TasteVector, Number(e.target.value) / 100)}
                style={{ width: "100%", cursor: "pointer" }}
              />
            </div>
          ))}

          <button
            onClick={handleMatch}
            disabled={loading}
            style={{
              backgroundColor: "var(--accent-gold)",
              color: "#0b0c10",
              fontWeight: 700,
              fontSize: 15,
              padding: "12px 24px",
              borderRadius: 10,
              border: "none",
              cursor: "pointer",
              marginTop: 10,
              boxShadow: "0 4px 14px rgba(229, 169, 60, 0.3)",
              transition: "all 0.2s",
            }}
          >
            {loading ? "Matching Vectors..." : "Compute Taste Matches"}
          </button>
        </div>
      </div>

      {/* Results Carousel */}
      {matches.length > 0 && (
        <div style={{ marginTop: 28, borderTop: "1px solid var(--border-color)", paddingTop: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", marginBottom: 16 }}>
            Top Semantic Matches
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
            {matches.map((m) => (
              <div
                key={m.product.id}
                onClick={() => onSelectProduct(m.product.slug)}
                style={{
                  backgroundColor: "var(--bg-surface)",
                  border: "1px solid var(--border-color)",
                  borderRadius: 12,
                  padding: 16,
                  cursor: "pointer",
                  transition: "transform 0.2s, border-color 0.2s",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = "translateY(-3px)";
                  e.currentTarget.style.borderColor = "var(--accent-gold)";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "var(--border-color)";
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: "var(--accent-gold)", textTransform: "uppercase" }}>
                    {m.product.brand_name || m.product.product_type}
                  </span>
                  <span style={{
                    backgroundColor: "rgba(16, 185, 129, 0.15)",
                    color: "var(--accent-emerald)",
                    fontSize: 12,
                    fontWeight: 700,
                    padding: "3px 8px",
                    borderRadius: 6,
                  }}>
                    {Math.round(m.similarity_score * 100)}% Match
                  </span>
                </div>
                <h4 style={{ fontSize: 15, fontWeight: 700, color: "var(--text-primary)", marginBottom: 6 }}>
                  {m.product.name}
                </h4>
                {m.match_reasons.length > 0 && (
                  <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                    {m.match_reasons[0]}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
