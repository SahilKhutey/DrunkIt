"use client";

import React, { useEffect, useState } from "react";
import AvailabilityModal from "./components/AvailabilityModal";
import CartDrawer, { CartData } from "./components/CartDrawer";
import ProductCard, { ProductItem } from "./components/ProductCard";
import TasteRadarWidget from "./components/TasteRadarWidget";

interface Occasion {
  slug: string;
  title: string;
  subtitle: string;
  hero_tag: string;
  item_count: number;
}

export default function Home() {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [occasions, setOccasions] = useState<Occasion[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(null);
  const [cart, setCart] = useState<CartData | null>(null);
  const [isCartOpen, setIsCartOpen] = useState<boolean>(false);
  const [selectedState, setSelectedState] = useState<string>("IN-WB");
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize consumer auth & fetch data
  useEffect(() => {
    async function initData() {
      try {
        // 1. Auto-login or register demo consumer
        const regRes = await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "shopper@drunkit.in", password: "ShopperPassword123!", role: "CONSUMER" }),
        });
        const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "shopper@drunkit.in", password: "ShopperPassword123!" }),
        });
        const token = (await loginRes.json()).access_token;

        // 2. Fetch Products
        const prodRes = await fetch("http://127.0.0.1:8000/api/v1/products?limit=20");
        const prodData = await prodRes.json();
        if (prodData.items) {
          setProducts(prodData.items);
        }

        // 3. Fetch Occasions
        const occRes = await fetch("http://127.0.0.1:8000/api/v1/discovery/occasions");
        const occData = await occRes.json();
        if (Array.isArray(occData)) {
          setOccasions(occData);
        }

        // 4. Fetch Cart
        const cartRes = await fetch("http://127.0.0.1:8000/api/v1/cart", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (cartRes.ok) {
          const cartData = await cartRes.json();
          setCart(cartData);
        }
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setLoading(false);
      }
    }

    initData();
  }, []);

  const handleAddToCart = async (skuId: string, locationId: string) => {
    try {
      const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "shopper@drunkit.in", password: "ShopperPassword123!" }),
      });
      const token = (await loginRes.json()).access_token;

      const res = await fetch("http://127.0.0.1:8000/api/v1/cart/items", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sku_id: skuId,
          retailer_location_id: locationId,
          quantity: 1,
        }),
      });

      if (res.ok) {
        const updatedCart = await res.json();
        setCart(updatedCart);
        setSelectedProduct(null);
        setIsCartOpen(true);
      }
    } catch (err) {
      console.error("Failed to add to cart:", err);
    }
  };

  const handleRemoveFromCart = async (itemId: string) => {
    try {
      const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "shopper@drunkit.in", password: "ShopperPassword123!" }),
      });
      const token = (await loginRes.json()).access_token;

      const res = await fetch(`http://127.0.0.1:8000/api/v1/cart/items/${itemId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const updatedCart = await res.json();
        setCart(updatedCart);
      }
    } catch (err) {
      console.error("Failed to remove item:", err);
    }
  };

  const handleSelectProductBySlug = (slug: string) => {
    const prod = products.find((p) => p.slug === slug);
    if (prod) {
      setSelectedProduct(prod);
    }
  };

  // Filter products
  const filteredProducts = products.filter((p) => {
    const matchesCategory =
      selectedCategory === "ALL" ||
      p.product_type.toUpperCase() === selectedCategory.toUpperCase();
    const matchesSearch =
      searchQuery === "" ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.brand_name && p.brand_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-primary)" }}>
      {/* ────────────────────────────────────────────────────────── */}
      {/* Navigation Bar */}
      {/* ────────────────────────────────────────────────────────── */}
      <header
        style={{
          backgroundColor: "rgba(20, 22, 29, 0.92)",
          backdropFilter: "blur(8px)",
          borderBottom: "1px solid var(--border-color)",
          position: "sticky",
          top: 0,
          zIndex: 100,
          padding: "14px 28px",
        }}
      >
        <div
          style={{
            maxWidth: 1200,
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 24 }}>🥃</span>
            <div>
              <span style={{ fontSize: 20, fontWeight: 900, letterSpacing: "-0.02em", color: "var(--text-primary)" }}>
                Drunk<span style={{ color: "var(--accent-gold)" }}>It</span>
              </span>
              <span style={{ fontSize: 10, display: "block", color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Commerce & Intelligence
              </span>
            </div>
          </div>

          {/* Location & Cart */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            {/* Jurisdiction Picker */}
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px solid var(--border-color)",
                color: "var(--text-primary)",
                padding: "6px 12px",
                borderRadius: 8,
                fontSize: 13,
                fontWeight: 600,
              }}
            >
              <option value="IN-WB">📍 Kolkata (WB)</option>
              <option value="IN-MH">📍 Mumbai (MH)</option>
              <option value="IN-KA">📍 Bengaluru (KA)</option>
              <option value="IN-DL">📍 Delhi NCT (DL)</option>
              <option value="IN-GA">📍 Goa (GA)</option>
            </select>

            {/* Cart Button */}
            <button
              onClick={() => setIsCartOpen(true)}
              style={{
                backgroundColor: "var(--bg-surface)",
                border: "1px solid var(--border-color)",
                color: "var(--text-primary)",
                padding: "8px 16px",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "border-color 0.2s",
              }}
              onMouseOver={(e) => (e.currentTarget.style.borderColor = "var(--accent-gold)")}
              onMouseOut={(e) => (e.currentTarget.style.borderColor = "var(--border-color)")}
            >
              <span>🛒</span>
              <span>Basket</span>
              {cart && cart.item_count > 0 && (
                <span
                  style={{
                    backgroundColor: "var(--accent-gold)",
                    color: "#0b0c10",
                    fontSize: 11,
                    fontWeight: 900,
                    padding: "2px 6px",
                    borderRadius: 10,
                  }}
                >
                  {cart.item_count}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Hero Section */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ padding: "48px 24px 24px", maxWidth: 1200, margin: "0 auto", textAlign: "center" }}>
        <span
          style={{
            backgroundColor: "rgba(229, 169, 60, 0.12)",
            border: "1px solid var(--border-gold)",
            color: "var(--accent-gold)",
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.1em",
            padding: "4px 14px",
            borderRadius: 20,
            textTransform: "uppercase",
          }}
        >
          100% Regulated Alcohol Platform
        </span>

        <h1
          style={{
            fontSize: "clamp(32px, 5vw, 48px)",
            fontWeight: 900,
            letterSpacing: "-0.03em",
            color: "var(--text-primary)",
            marginTop: 16,
            marginBottom: 12,
          }}
        >
          Discover Premier Spirits & Live Local Availability
        </h1>

        <p style={{ color: "var(--text-secondary)", fontSize: 16, maxWidth: 640, margin: "0 auto 32px" }}>
          Connecting consumers, independent craft distilleries, and licensed neighborhood cellars with deterministic statutory compliance.
        </p>

        {/* Search Bar */}
        <div style={{ maxWidth: 540, margin: "0 auto 36px", position: "relative" }}>
          <input
            type="text"
            placeholder="Search single malts, botanical gins, distilleries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-color)",
              color: "var(--text-primary)",
              padding: "14px 20px 14px 44px",
              borderRadius: 12,
              fontSize: 15,
              outline: "none",
              boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
            }}
          />
          <span style={{ position: "absolute", left: 16, top: 14, fontSize: 18, color: "var(--text-muted)" }}>
            🔍
          </span>
        </div>

        {/* Category Filter Pills */}
        <div style={{ display: "flex", justifyContent: "center", gap: 10, flexWrap: "wrap" }}>
          {["ALL", "WHISKY", "GIN", "TEQUILA", "VODKA"].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                backgroundColor: selectedCategory === cat ? "var(--accent-gold)" : "var(--bg-surface)",
                color: selectedCategory === cat ? "#0b0c10" : "var(--text-secondary)",
                border: "1px solid",
                borderColor: selectedCategory === cat ? "var(--accent-gold)" : "var(--border-color)",
                padding: "8px 20px",
                borderRadius: 24,
                fontSize: 13,
                fontWeight: 700,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              {cat === "ALL" ? "All Spirits" : cat}
            </button>
          ))}
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Curated Occasions Carousel */}
      {/* ────────────────────────────────────────────────────────── */}
      {occasions.length > 0 && (
        <section style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px 32px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 16 }}>
            <div>
              <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
                Curated Collections
              </span>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)" }}>
                Occasion Discovery
              </h2>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 16,
            }}
          >
            {occasions.map((occ) => (
              <div
                key={occ.slug}
                style={{
                  backgroundColor: "var(--bg-surface)",
                  border: "1px solid var(--border-color)",
                  borderRadius: 12,
                  padding: 18,
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
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    backgroundColor: "rgba(229, 169, 60, 0.15)",
                    color: "var(--accent-gold)",
                    padding: "2px 6px",
                    borderRadius: 4,
                    textTransform: "uppercase",
                  }}
                >
                  {occ.hero_tag}
                </span>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", marginTop: 8, marginBottom: 4 }}>
                  {occ.title}
                </h3>
                <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.4 }}>
                  {occ.subtitle}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ────────────────────────────────────────────────────────── */}
      {/* 6-Axis Semantic Taste Radar Widget */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <TasteRadarWidget onSelectProduct={handleSelectProductBySlug} />
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Master Catalog Spirits Grid */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 24px 80px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", color: "var(--accent-gold)", textTransform: "uppercase" }}>
              Explore Collection
            </span>
            <h2 style={{ fontSize: 24, fontWeight: 700, color: "var(--text-primary)" }}>
              Premier Spirits Catalog
            </h2>
          </div>
          <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            Showing {filteredProducts.length} expressions
          </span>
        </div>

        {loading ? (
          <div style={{ padding: "80px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            Loading spirits catalog...
          </div>
        ) : filteredProducts.length === 0 ? (
          <div style={{ padding: "60px 0", textAlign: "center", color: "var(--text-secondary)" }}>
            No spirits found matching your filter criteria.
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
              gap: 24,
            }}
          >
            {filteredProducts.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                onCheckAvailability={(product) => setSelectedProduct(product)}
              />
            ))}
          </div>
        )}
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Live Store Availability Modal */}
      {/* ────────────────────────────────────────────────────────── */}
      <AvailabilityModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAddToCart={handleAddToCart}
      />

      {/* ────────────────────────────────────────────────────────── */}
      {/* Compliance-Gated Cart Drawer */}
      {/* ────────────────────────────────────────────────────────── */}
      <CartDrawer
        isOpen={isCartOpen}
        cart={cart}
        onClose={() => setIsCartOpen(false)}
        onRemoveItem={handleRemoveFromCart}
        onCheckoutSuccess={(order) => {
          // Re-fetch cart after checkout
          setCart(null);
        }}
      />
    </div>
  );
}
