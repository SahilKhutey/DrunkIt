"use client";

import React, { useEffect, useState } from "react";

interface DeliveryItem {
  sku_id: string;
  product_name: string;
  volume_ml: number;
  quantity: number;
  unit_price_formatted: string;
  total_price_formatted: string;
}

interface DeliveryManifest {
  order_id: string;
  retailer_name: string;
  store_address: string;
  customer_id: string;
  delivery_channel: string;
  status: string;
  total_amount_formatted: string;
  total_volume_ml: number;
  items_summary: DeliveryItem[];
  created_at: string;
}

export default function DriverAppHome() {
  const [assignments, setAssignments] = useState<DeliveryManifest[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<DeliveryManifest | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);

  // Verification Form State
  const [otp, setOtp] = useState<string>("");
  const [idType, setIdType] = useState<"AADHAAR" | "PASSPORT" | "DRIVING_LICENCE" | "VOTER_ID">("AADHAAR");
  const [age, setAge] = useState<number>(24);
  const [idChecked, setIdChecked] = useState<boolean>(false);
  const [verifying, setVerifying] = useState<boolean>(false);
  const [resultMsg, setResultMsg] = useState<{ success: boolean; text: string } | null>(null);

  // Abort State
  const [showAbort, setShowAbort] = useState<boolean>(false);
  const [abortReason, setAbortReason] = useState<"UNDERAGE_AT_DOOR" | "NO_VALID_ID_PRESENTED" | "CONSUMER_INTOXICATED" | "ADDRESS_UNREACHABLE">("UNDERAGE_AT_DOOR");

  useEffect(() => {
    async function initDriver() {
      try {
        // Auto-login driver
        await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "driver.rahul@drunkit.in", password: "DriverPassword123!", role: "RETAILER" }),
        });
        const loginRes = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: "driver.rahul@drunkit.in", password: "DriverPassword123!" }),
        });
        const tok = (await loginRes.json()).access_token;
        setToken(tok);

        await loadAssignments(tok);
      } catch (err) {
        console.error("Driver initialization error:", err);
      } finally {
        setLoading(false);
      }
    }

    initDriver();
  }, []);

  const loadAssignments = async (tok: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/delivery/assignments", {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (res.ok) {
        const data = await res.json();
        setAssignments(data);
      }
    } catch (err) {
      console.error("Failed to load delivery assignments:", err);
    }
  };

  const handleVerifyHandover = async () => {
    if (!selectedOrder || !token) return;
    if (!idChecked) {
      setResultMsg({ success: false, text: "You must physically inspect and confirm recipient ID." });
      return;
    }
    if (otp.length < 4) {
      setResultMsg({ success: false, text: "Please enter the 4-digit consumer delivery OTP." });
      return;
    }

    setVerifying(true);
    setResultMsg(null);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/delivery/orders/${selectedOrder.order_id}/verify-and-complete`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            otp: otp.trim(),
            verified_id_type: idType,
            recipient_declared_age: Number(age),
            latitude: 22.5516,
            longitude: 88.3524,
          }),
        }
      );

      const data = await res.json();
      if (res.ok) {
        setResultMsg({ success: true, text: "✓ Doorstep ID Verified & Order Delivered Successfully!" });
        await loadAssignments(token);
      } else {
        setResultMsg({ success: false, text: `⚠️ ${data?.error?.message || "Verification failed."}` });
      }
    } catch (err: any) {
      setResultMsg({ success: false, text: `⚠️ ${err.message}` });
    } finally {
      setVerifying(false);
    }
  };

  const handleAbortDelivery = async () => {
    if (!selectedOrder || !token) return;
    setVerifying(true);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/delivery/orders/${selectedOrder.order_id}/abort-statutory-return`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            reason: abortReason,
            notes: "Fail-closed statutory return initiated at doorstep.",
          }),
        }
      );

      const data = await res.json();
      if (res.ok) {
        setResultMsg({ success: false, text: `🛑 Delivery Aborted: ${data.abort_reason}. Stock returned to store.` });
        setShowAbort(false);
        await loadAssignments(token);
      }
    } catch (err: any) {
      setResultMsg({ success: false, text: `⚠️ ${err.message}` });
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "var(--bg-primary)", display: "flex", justifyContent: "center" }}>
      <div style={{ width: "100%", maxWidth: 480, padding: "16px 16px 40px" }}>
        {/* ────────────────────────────────────────────────────────── */}
        {/* Header */}
        {/* ────────────────────────────────────────────────────────── */}
        <header
          style={{
            backgroundColor: "var(--bg-surface)",
            border: "1px solid var(--border-color)",
            borderRadius: 14,
            padding: "16px 20px",
            marginBottom: 20,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 20 }}>🛵</span>
              <span style={{ fontSize: 18, fontWeight: 900, color: "var(--text-primary)" }}>
                Drunk<span style={{ color: "var(--accent-emerald)" }}>It</span> Driver
              </span>
            </div>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
              Statutory Doorstep Verification Station
            </span>
          </div>

          <div style={{ textAlign: "right" }}>
            <span
              style={{
                fontSize: 10,
                fontWeight: 700,
                backgroundColor: "rgba(16, 185, 129, 0.15)",
                color: "var(--accent-emerald)",
                padding: "2px 8px",
                borderRadius: 10,
              }}
            >
              🟢 GPS Active
            </span>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              {assignments.length} Deliveries
            </div>
          </div>
        </header>

        {/* ────────────────────────────────────────────────────────── */}
        {/* Assignments Manifest */}
        {/* ────────────────────────────────────────────────────────── */}
        <div style={{ marginBottom: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 800, color: "var(--text-primary)", marginBottom: 12 }}>
            Active Delivery Queue
          </h2>

          {loading ? (
            <div style={{ textAlign: "center", padding: "40px 0", color: "var(--text-secondary)" }}>
              Loading assigned routes...
            </div>
          ) : assignments.length === 0 ? (
            <div style={{ backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: 12, padding: 32, textAlign: "center" }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>✨</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: "var(--text-primary)" }}>All Deliveries Completed</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: 12, marginTop: 4 }}>
                Ready orders will appear here as store counters dispatch them.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {assignments.map((asgn) => (
                <div
                  key={asgn.order_id}
                  style={{
                    backgroundColor: "var(--bg-card)",
                    border: "1px solid var(--border-color)",
                    borderRadius: 12,
                    padding: 18,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                    <div>
                      <span style={{ fontSize: 13, fontWeight: 800, color: "var(--text-primary)" }}>
                        Order #{asgn.order_id.substring(0, 8)}
                      </span>
                      <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                        📍 Store: {asgn.retailer_name}
                      </div>
                    </div>
                    <span
                      style={{
                        backgroundColor: "rgba(59, 130, 246, 0.15)",
                        color: "var(--accent-blue)",
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "2px 8px",
                        borderRadius: 4,
                      }}
                    >
                      {asgn.status}
                    </span>
                  </div>

                  <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 12 }}>
                    {asgn.items_summary.map((it, idx) => (
                      <div key={idx}>
                        <strong>{it.quantity}×</strong> {it.product_name} ({it.volume_ml}ml)
                      </div>
                    ))}
                    <div style={{ marginTop: 4, color: "var(--text-muted)", fontSize: 11 }}>
                      Total Volume: {asgn.total_volume_ml} ml • Value: {asgn.total_amount_formatted}
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setSelectedOrder(asgn);
                      setResultMsg(null);
                      setOtp("");
                      setIdChecked(false);
                      setShowAbort(false);
                    }}
                    style={{
                      width: "100%",
                      backgroundColor: "var(--accent-emerald)",
                      color: "#0a0d14",
                      fontWeight: 800,
                      fontSize: 13,
                      padding: "10px",
                      borderRadius: 8,
                      border: "none",
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                      gap: 6,
                    }}
                  >
                    <span>🪪</span> Start Doorstep Verification ➔
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ────────────────────────────────────────────────────────── */}
        {/* Handover Modal */}
        {/* ────────────────────────────────────────────────────────── */}
        {selectedOrder && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: "rgba(0, 0, 0, 0.85)",
              backdropFilter: "blur(6px)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 1000,
              padding: 16,
            }}
          >
            <div
              style={{
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-color)",
                borderRadius: 16,
                width: "100%",
                maxWidth: 420,
                padding: 24,
                maxHeight: "90vh",
                overflowY: "auto",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 800, color: "var(--accent-emerald)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                    Statutory Verification
                  </span>
                  <h3 style={{ fontSize: 18, fontWeight: 800, color: "var(--text-primary)" }}>
                    Doorstep ID Handover
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedOrder(null)}
                  style={{ background: "none", border: "none", color: "var(--text-secondary)", fontSize: 22, cursor: "pointer" }}
                >
                  ✕
                </button>
              </div>

              {resultMsg ? (
                <div
                  style={{
                    backgroundColor: resultMsg.success ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                    border: "1px solid",
                    borderColor: resultMsg.success ? "var(--accent-emerald)" : "var(--accent-ruby)",
                    borderRadius: 10,
                    padding: 20,
                    textAlign: "center",
                    marginBottom: 16,
                  }}
                >
                  <div style={{ fontSize: 24, marginBottom: 8 }}>{resultMsg.success ? "🎉" : "⚠️"}</div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: resultMsg.success ? "var(--accent-emerald)" : "var(--accent-ruby)" }}>
                    {resultMsg.text}
                  </div>
                  {resultMsg.success && (
                    <button
                      onClick={() => setSelectedOrder(null)}
                      style={{
                        marginTop: 16,
                        backgroundColor: "var(--accent-emerald)",
                        color: "#0a0d14",
                        fontWeight: 700,
                        fontSize: 13,
                        padding: "8px 16px",
                        borderRadius: 6,
                        border: "none",
                        cursor: "pointer",
                      }}
                    >
                      Close
                    </button>
                  )}
                </div>
              ) : !showAbort ? (
                <div>
                  {/* Step 1: ID Type */}
                  <div style={{ marginBottom: 14 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                      1. Inspect Government ID
                    </label>
                    <select
                      value={idType}
                      onChange={(e) => setIdType(e.target.value as any)}
                      style={{
                        width: "100%",
                        backgroundColor: "var(--bg-surface)",
                        border: "1px solid var(--border-color)",
                        color: "var(--text-primary)",
                        padding: "8px 12px",
                        borderRadius: 8,
                        fontSize: 13,
                      }}
                    >
                      <option value="AADHAAR">Aadhaar Card</option>
                      <option value="DRIVING_LICENCE">Driving Licence</option>
                      <option value="PASSPORT">Indian Passport</option>
                      <option value="VOTER_ID">Voter ID Card</option>
                    </select>
                  </div>

                  {/* Step 2: Recipient Age */}
                  <div style={{ marginBottom: 14 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                      2. Verified Age on ID Document: <strong style={{ color: "var(--text-primary)" }}>{age} yrs</strong>
                    </label>
                    <input
                      type="range"
                      min="18"
                      max="80"
                      value={age}
                      onChange={(e) => setAge(Number(e.target.value))}
                      style={{ width: "100%", accentColor: "var(--accent-emerald)" }}
                    />
                  </div>

                  {/* Step 3: Physical Check Confirmation */}
                  <label style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12, color: "var(--text-primary)", cursor: "pointer", marginBottom: 16 }}>
                    <input
                      type="checkbox"
                      checked={idChecked}
                      onChange={(e) => setIdChecked(e.target.checked)}
                      style={{ marginTop: 2, accentColor: "var(--accent-emerald)" }}
                    />
                    <span>I confirm recipient matches photo ID and is strictly 21+ years old.</span>
                  </label>

                  {/* Step 4: OTP Entry */}
                  <div style={{ marginBottom: 20 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                      3. Consumer Delivery OTP
                    </label>
                    <input
                      type="text"
                      maxLength={6}
                      placeholder="e.g. 1234"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      style={{
                        width: "100%",
                        backgroundColor: "var(--bg-surface)",
                        border: "1px solid var(--border-color)",
                        color: "var(--text-primary)",
                        padding: "10px 14px",
                        borderRadius: 8,
                        fontSize: 16,
                        letterSpacing: "0.2em",
                        textAlign: "center",
                        fontWeight: 800,
                      }}
                    />
                  </div>

                  {/* Actions */}
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    <button
                      onClick={handleVerifyHandover}
                      disabled={verifying}
                      style={{
                        backgroundColor: "var(--accent-emerald)",
                        color: "#0a0d14",
                        fontWeight: 800,
                        fontSize: 14,
                        padding: "12px",
                        borderRadius: 8,
                        border: "none",
                        cursor: verifying ? "not-allowed" : "pointer",
                      }}
                    >
                      {verifying ? "Verifying..." : "Verify & Complete Handover ✓"}
                    </button>

                    <button
                      onClick={() => setShowAbort(true)}
                      style={{
                        backgroundColor: "transparent",
                        color: "var(--accent-ruby)",
                        fontWeight: 700,
                        fontSize: 12,
                        padding: "8px",
                        border: "1px solid var(--accent-ruby)",
                        borderRadius: 8,
                        cursor: "pointer",
                      }}
                    >
                      🛑 Abort Delivery (Statutory Violation)
                    </button>
                  </div>
                </div>
              ) : (
                /* Abort Panel */
                <div>
                  <div style={{ backgroundColor: "rgba(239, 68, 68, 0.12)", border: "1px solid var(--accent-ruby)", borderRadius: 10, padding: 14, marginBottom: 16 }}>
                    <h4 style={{ fontSize: 13, fontWeight: 700, color: "var(--accent-ruby)", marginBottom: 4 }}>
                      Statutory Rejection Protocol
                    </h4>
                    <p style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                      Alcohol delivery MUST be refused and returned to the licensed off-shop if statutory requirements are violated.
                    </p>
                  </div>

                  <div style={{ marginBottom: 16 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                      Violation Reason:
                    </label>
                    <select
                      value={abortReason}
                      onChange={(e) => setAbortReason(e.target.value as any)}
                      style={{
                        width: "100%",
                        backgroundColor: "var(--bg-surface)",
                        border: "1px solid var(--border-color)",
                        color: "var(--text-primary)",
                        padding: "8px 12px",
                        borderRadius: 8,
                        fontSize: 13,
                      }}
                    >
                      <option value="UNDERAGE_AT_DOOR">Underage Recipient at Doorstep (&lt;21)</option>
                      <option value="NO_VALID_ID_PRESENTED">No Valid Physical ID Presented</option>
                      <option value="CONSUMER_INTOXICATED">Consumer Visibly Intoxicated</option>
                      <option value="ADDRESS_UNREACHABLE">Address Unreachable / Customer Refused</option>
                    </select>
                  </div>

                  <div style={{ display: "flex", gap: 10 }}>
                    <button
                      onClick={handleAbortDelivery}
                      disabled={verifying}
                      style={{
                        flex: 1,
                        backgroundColor: "var(--accent-ruby)",
                        color: "#ffffff",
                        fontWeight: 800,
                        fontSize: 13,
                        padding: "10px",
                        borderRadius: 8,
                        border: "none",
                        cursor: verifying ? "not-allowed" : "pointer",
                      }}
                    >
                      Confirm Statutory Abort
                    </button>
                    <button
                      onClick={() => setShowAbort(false)}
                      style={{
                        backgroundColor: "var(--bg-surface)",
                        color: "var(--text-secondary)",
                        fontWeight: 700,
                        fontSize: 13,
                        padding: "10px 16px",
                        borderRadius: 8,
                        border: "1px solid var(--border-color)",
                        cursor: "pointer",
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
