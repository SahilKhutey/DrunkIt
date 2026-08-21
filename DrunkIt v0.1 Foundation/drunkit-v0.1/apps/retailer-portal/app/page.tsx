"use client";

import React, { useEffect, useState } from "react";

interface DashboardData {
  location_id: string;
  location_name: string;
  active_skus_count: number;
  in_stock_skus_count: number;
  low_stock_skus_count: number;
  out_of_stock_skus_count: number;
  total_orders_count: number;
  total_gmv_minor: number;
  total_gmv_formatted: string;
}

interface OrderItem {
  id: string;
  sku_id: string;
  canonical_code: string;
  product_name: string;
  volume_ml: number;
  quantity: number;
  unit_price_formatted: string;
  total_price_formatted: string;
}

interface StoreOrder {
  id: string;
  consumer_id: string;
  status: "PENDING" | "CONFIRMED" | "PREPARING" | "READY_FOR_PICKUP" | "OUT_FOR_DELIVERY" | "FULFILLED" | "CANCELLED";
  total_formatted: string;
  compliance_decision_id: string | null;
  items: OrderItem[];
  created_at: string;
}

interface LocationOption {
  id: string;
  name: string;
  city: string;
  state_code: string;
  licence_number: string;
}

const DEMO_LOCATIONS: LocationOption[] = [
  {
    id: "park-street-location-id",
    name: "Park Street Premium Off-Shop",
    city: "Kolkata",
    state_code: "WB",
    licence_number: "WB-EXC-KOL-2024-9843",
  },
  {
    id: "salt-lake-location-id",
    name: "Salt Lake Sector V Cellar",
    city: "Kolkata",
    state_code: "WB",
    licence_number: "WB-EXC-KOL-2024-9844",
  },
];

export default function RetailerPortalHome() {
  const [activeTab, setActiveTab] = useState<"orders" | "pos_sync" | "licence">("orders");
  const [selectedLocation, setSelectedLocation] = useState<LocationOption>(DEMO_LOCATIONS[0]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [orders, setOrders] = useState<StoreOrder[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);

  // POS Sync Form State
  const [posPayload, setPosPayload] = useState<string>(
    JSON.stringify(
      {
        source: "POS_CSV_SYNC",
        items: [
          { external_sku: "POS_PS_INDRI-750", quantity: 48, price_minor: 420000 },
          { external_sku: "POS_PS_INDRI-375", quantity: 24, price_minor: 220000 },
          { external_sku: "POS_PS_AMRUT-750", quantity: 18, price_minor: 510000 },
          { external_sku: "POS_PS_STRANGER-750", quantity: 30, price_minor: 270000 },
        ],
      },
      null,
      2
    )
  );
  const [syncResult, setSyncResult] = useState<any | null>(null);
  const [syncing, setSyncing] = useState<boolean>(false);

  // Authenticate as retailer and load store data
  useEffect(() => {
    async function initRetailer() {
      try {
        // 1. Auto register/login retailer manager
        await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "pos.manager@drunkit.in", password: "ManagerPassword123!", role: "RETAILER" }),
        });
        const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "pos.manager@drunkit.in", password: "ManagerPassword123!" }),
        });
        const tok = (await loginRes.json()).access_token;
        setToken(tok);

        // 2. Fetch pilot store locations to get real UUID
        const availRes = await fetch("http://127.0.0.1:8000/api/v1/products/indri-trini-three-wood/availability");
        const availData = await availRes.json();
        if (availData.stores && availData.stores.length > 0) {
          const firstStore = availData.stores[0];
          const updatedLoc: LocationOption = {
            id: firstStore.location_id,
            name: firstStore.location_name,
            city: firstStore.city,
            state_code: firstStore.state_code,
            licence_number: "WB-EXC-KOL-2024-9843",
          };
          setSelectedLocation(updatedLoc);
          await loadStoreData(firstStore.location_id, tok);
        }
      } catch (err) {
        console.error("Retailer Portal initialization error:", err);
      } finally {
        setLoading(false);
      }
    }

    initRetailer();
  }, []);

  const loadStoreData = async (locationId: string, tok: string) => {
    try {
      // 1. Load Dashboard
      const dashRes = await fetch(`http://127.0.0.1:8000/api/v1/retailer/locations/${locationId}/dashboard`, {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (dashRes.ok) {
        const dashData = await dashRes.json();
        setDashboard(dashData);
      }

      // 2. Load Orders Queue
      const ordersRes = await fetch(`http://127.0.0.1:8000/api/v1/retailer/locations/${locationId}/orders`, {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (ordersRes.ok) {
        const ordersData = await ordersRes.json();
        if (ordersData.orders) {
          setOrders(ordersData.orders);
        }
      }
    } catch (err) {
      console.error("Error loading store data:", err);
    }
  };

  const handleTransitionStatus = async (orderId: string, nextStatus: string) => {
    if (!token) return;
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/retailer/locations/${selectedLocation.id}/orders/${orderId}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status: nextStatus }),
        }
      );

      if (res.ok) {
        await loadStoreData(selectedLocation.id, token);
      }
    } catch (err) {
      console.error("Failed to transition order status:", err);
    }
  };

  const handleSyncPOS = async () => {
    if (!token) return;
    setSyncing(true);
    setSyncResult(null);

    try {
      const payload = JSON.parse(posPayload);
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/retailer/locations/${selectedLocation.id}/inventory/bulk`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await res.json();
      setSyncResult(data);
      await loadStoreData(selectedLocation.id, token);
    } catch (err: any) {
      setSyncResult({ error: err.message || "Failed to parse POS sync payload." });
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-primary)" }}>
      {/* ────────────────────────────────────────────────────────── */}
      {/* Navigation Header */}
      {/* ────────────────────────────────────────────────────────── */}
      <header
        style={{
          backgroundColor: "rgba(18, 21, 29, 0.95)",
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
          {/* Brand */}
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 24 }}>🏪</span>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 20, fontWeight: 900, color: "var(--text-primary)" }}>
                  Drunk<span style={{ color: "var(--accent-blue)" }}>It</span>
                </span>
                <span
                  style={{
                    backgroundColor: "rgba(59, 130, 246, 0.15)",
                    color: "var(--accent-blue)",
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    textTransform: "uppercase",
                  }}
                >
                  Retailer Portal
                </span>
              </div>
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                Licensed Store POS Sync & Fulfillment Station
              </span>
            </div>
          </div>

          {/* Location & Manager Info */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)" }}>
                {selectedLocation.name}
              </div>
              <div style={{ fontSize: 11, color: "var(--accent-emerald)" }}>
                🟢 Licence: {selectedLocation.licence_number}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ────────────────────────────────────────────────────────── */}
      {/* KPI Overview Metrics */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "28px 28px 0" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
          {/* GMV */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Total Store GMV</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-gold)", marginTop: 6 }}>
              {dashboard?.total_gmv_formatted || "₹0.00"}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              From {dashboard?.total_orders_count || 0} statutory orders
            </span>
          </div>

          {/* Active SKUs */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Active Catalog SKUs</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--text-primary)", marginTop: 6 }}>
              {dashboard?.active_skus_count || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--accent-emerald)", marginTop: 4, display: "block" }}>
              ✓ {dashboard?.in_stock_skus_count || 0} in stock
            </span>
          </div>

          {/* Low Stock */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Low Stock Warnings</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-amber)", marginTop: 6 }}>
              {dashboard?.low_stock_skus_count || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              &le; 5 units remaining
            </span>
          </div>

          {/* Out of Stock */}
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 20 }}>
            <span style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 600 }}>Out of Stock</span>
            <div style={{ fontSize: 28, fontWeight: 900, color: "var(--accent-ruby)", marginTop: 6 }}>
              {dashboard?.out_of_stock_skus_count || 0}
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, display: "block" }}>
              Requires POS restocking
            </span>
          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────── */}
      {/* Main Tabs Navigation */}
      {/* ────────────────────────────────────────────────────────── */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "28px 28px 48px" }}>
        <div style={{ display: "flex", gap: 10, borderBottom: "1px solid var(--border-color)", paddingBottom: 12, marginBottom: 24 }}>
          <button
            onClick={() => setActiveTab("orders")}
            style={{
              backgroundColor: activeTab === "orders" ? "var(--accent-blue)" : "var(--bg-surface)",
              color: activeTab === "orders" ? "#ffffff" : "var(--text-secondary)",
              border: "1px solid",
              borderColor: activeTab === "orders" ? "var(--accent-blue)" : "var(--border-color)",
              padding: "10px 22px",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            📦 Store Fulfillment Queue ({orders.length})
          </button>

          <button
            onClick={() => setActiveTab("pos_sync")}
            style={{
              backgroundColor: activeTab === "pos_sync" ? "var(--accent-blue)" : "var(--bg-surface)",
              color: activeTab === "pos_sync" ? "#ffffff" : "var(--text-secondary)",
              border: "1px solid",
              borderColor: activeTab === "pos_sync" ? "var(--accent-blue)" : "var(--border-color)",
              padding: "10px 22px",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            🔄 Bulk POS Inventory Sync
          </button>

          <button
            onClick={() => setActiveTab("licence")}
            style={{
              backgroundColor: activeTab === "licence" ? "var(--accent-blue)" : "var(--bg-surface)",
              color: activeTab === "licence" ? "#ffffff" : "var(--text-secondary)",
              border: "1px solid",
              borderColor: activeTab === "licence" ? "var(--accent-blue)" : "var(--border-color)",
              padding: "10px 22px",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            📜 Excise Licence & Compliance
          </button>
        </div>

        {/* ────────────────────────────────────────────────────────── */}
        {/* Tab 1: Orders Fulfillment Queue */}
        {/* ────────────────────────────────────────────────────────── */}
        {activeTab === "orders" && (
          <div>
            {orders.length === 0 ? (
              <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 48, textAlign: "center" }}>
                <div style={{ fontSize: 36, marginBottom: 12 }}>📋</div>
                <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>No Orders in Fulfillment Queue</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 4 }}>
                  Incoming consumer pickup or delivery orders will appear here automatically.
                </p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                {orders.map((ord) => {
                  const isConfirmed = ord.status === "CONFIRMED";
                  const isPreparing = ord.status === "PREPARING";
                  const isReady = ord.status === "READY_FOR_PICKUP";
                  const isFulfilled = ord.status === "FULFILLED";

                  return (
                    <div
                      key={ord.id}
                      style={{
                        backgroundColor: "var(--bg-card)",
                        border: "1px solid var(--border-color)",
                        borderRadius: 12,
                        padding: 20,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        flexWrap: "wrap",
                        gap: 16,
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                          <span style={{ fontSize: 14, fontWeight: 800, color: "var(--text-primary)" }}>
                            Order #{ord.id.substring(0, 8)}
                          </span>
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: 4,
                              backgroundColor: isFulfilled
                                ? "rgba(16, 185, 129, 0.15)"
                                : isReady
                                ? "rgba(59, 130, 246, 0.15)"
                                : "rgba(229, 169, 60, 0.15)",
                              color: isFulfilled
                                ? "var(--accent-emerald)"
                                : isReady
                                ? "var(--accent-blue)"
                                : "var(--accent-gold)",
                            }}
                          >
                            {ord.status}
                          </span>
                        </div>

                        <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 8 }}>
                          {ord.items.map((it) => (
                            <div key={it.id}>
                              <strong>{it.quantity}×</strong> {it.product_name} ({it.volume_ml}ml) — {it.total_price_formatted}
                            </div>
                          ))}
                        </div>

                        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                          Compliance Ref: {ord.compliance_decision_id || "Validated"}
                        </div>
                      </div>

                      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                        <div style={{ textAlign: "right" }}>
                          <span style={{ fontSize: 11, color: "var(--text-muted)", display: "block" }}>Order Value</span>
                          <span style={{ fontSize: 18, fontWeight: 800, color: "var(--accent-gold)" }}>
                            {ord.total_formatted}
                          </span>
                        </div>

                        {/* State Machine Transition Actions */}
                        {isConfirmed && (
                          <button
                            onClick={() => handleTransitionStatus(ord.id, "PREPARING")}
                            style={{
                              backgroundColor: "var(--accent-blue)",
                              color: "#ffffff",
                              border: "none",
                              borderRadius: 8,
                              padding: "10px 18px",
                              fontWeight: 700,
                              fontSize: 13,
                              cursor: "pointer",
                            }}
                          >
                            Start Preparing ➔
                          </button>
                        )}

                        {isPreparing && (
                          <button
                            onClick={() => handleTransitionStatus(ord.id, "READY_FOR_PICKUP")}
                            style={{
                              backgroundColor: "var(--accent-amber)",
                              color: "#0b0c10",
                              border: "none",
                              borderRadius: 8,
                              padding: "10px 18px",
                              fontWeight: 700,
                              fontSize: 13,
                              cursor: "pointer",
                            }}
                          >
                            Mark Ready for Pickup ➔
                          </button>
                        )}

                        {isReady && (
                          <button
                            onClick={() => handleTransitionStatus(ord.id, "FULFILLED")}
                            style={{
                              backgroundColor: "var(--accent-emerald)",
                              color: "#0b0c10",
                              border: "none",
                              borderRadius: 8,
                              padding: "10px 18px",
                              fontWeight: 700,
                              fontSize: 13,
                              cursor: "pointer",
                            }}
                          >
                            Complete Handover ✓
                          </button>
                        )}

                        {isFulfilled && (
                          <span style={{ fontSize: 13, color: "var(--accent-emerald)", fontWeight: 700 }}>
                            ✓ Fulfilled
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* Tab 2: Bulk POS Inventory Sync */}
        {/* ────────────────────────────────────────────────────────── */}
        {activeTab === "pos_sync" && (
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 24 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>
              Bulk POS Feed Ingestion Terminal
            </h3>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
              Sync point-of-sale inventory quantities and statutory MRP prices directly with the DrunkIt master catalog.
            </p>

            <textarea
              rows={12}
              value={posPayload}
              onChange={(e) => setPosPayload(e.target.value)}
              style={{
                width: "100%",
                backgroundColor: "var(--bg-surface)",
                border: "1px solid var(--border-color)",
                color: "var(--text-primary)",
                fontFamily: "monospace",
                fontSize: 13,
                padding: 14,
                borderRadius: 8,
                outline: "none",
                marginBottom: 16,
              }}
            />

            <button
              onClick={handleSyncPOS}
              disabled={syncing}
              style={{
                backgroundColor: "var(--accent-blue)",
                color: "#ffffff",
                fontWeight: 700,
                fontSize: 14,
                padding: "12px 24px",
                borderRadius: 8,
                border: "none",
                cursor: syncing ? "not-allowed" : "pointer",
              }}
            >
              {syncing ? "Syncing POS Ingestion..." : "Execute POS Sync Feed"}
            </button>

            {/* Sync Feedback */}
            {syncResult && (
              <div
                style={{
                  marginTop: 20,
                  backgroundColor: syncResult.error ? "rgba(239, 68, 68, 0.15)" : "rgba(16, 185, 129, 0.15)",
                  border: "1px solid",
                  borderColor: syncResult.error ? "var(--accent-ruby)" : "var(--accent-emerald)",
                  borderRadius: 8,
                  padding: 16,
                }}
              >
                {syncResult.error ? (
                  <div style={{ color: "var(--accent-ruby)", fontSize: 13 }}>⚠️ {syncResult.error}</div>
                ) : (
                  <div>
                    <h4 style={{ fontSize: 14, fontWeight: 700, color: "var(--accent-emerald)", marginBottom: 6 }}>
                      ✓ POS Sync Completed Successfully
                    </h4>
                    <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", gap: 16 }}>
                      <span>Total: {syncResult.total_items}</span>
                      <span>Mapped: {syncResult.mapped_count}</span>
                      <span>Snapshots: {syncResult.snapshots_created}</span>
                      <span>Prices Updated: {syncResult.prices_updated}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ────────────────────────────────────────────────────────── */}
        {/* Tab 3: Excise Licence & Compliance */}
        {/* ────────────────────────────────────────────────────────── */}
        {activeTab === "licence" && (
          <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 24 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>
              Statutory Excise Licence & Operating Jurisdiction
            </h3>
            <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 20 }}>
              Official regulatory standing registered with the State Excise Directorate.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
              <div style={{ backgroundColor: "var(--bg-surface)", padding: 16, borderRadius: 8 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Licence Number</span>
                <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", marginTop: 4 }}>
                  {selectedLocation.licence_number}
                </div>
              </div>

              <div style={{ backgroundColor: "var(--bg-surface)", padding: 16, borderRadius: 8 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Jurisdiction</span>
                <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)", marginTop: 4 }}>
                  West Bengal (IN-WB)
                </div>
              </div>

              <div style={{ backgroundColor: "var(--bg-surface)", padding: 16, borderRadius: 8 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Operating Hours</span>
                <div style={{ fontSize: 16, fontWeight: 700, color: "var(--accent-emerald)", marginTop: 4 }}>
                  10:00 AM – 10:00 PM IST
                </div>
              </div>

              <div style={{ backgroundColor: "var(--bg-surface)", padding: 16, borderRadius: 8 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>Standing</span>
                <div style={{ fontSize: 16, fontWeight: 700, color: "var(--accent-emerald)", marginTop: 4 }}>
                  🟢 VERIFIED & ACTIVE
                </div>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
