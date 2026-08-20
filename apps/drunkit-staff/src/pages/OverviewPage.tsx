import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { StoreView, RetailerView, AdminDeliveryView } from "../types/api";

export function OverviewPage() {
  const { me, isPlatformAdmin } = useAuth();
  const [stores, setStores] = useState<StoreView[]>([]);
  const [retailers, setRetailers] = useState<RetailerView[]>([]);
  const [pendingDeliveries, setPendingDeliveries] = useState<AdminDeliveryView[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listStores().catch(() => []),
      isPlatformAdmin ? api.listRetailers().catch(() => []) : Promise.resolve([]),
      isPlatformAdmin ? api.listDeliveries("REQUESTED").catch(() => []) : Promise.resolve([]),
    ]).then(([s, r, d]) => {
      setStores(s);
      setRetailers(r);
      setPendingDeliveries(d);
      setLoading(false);
    });
  }, [isPlatformAdmin]);

  return (
    <div>
      <p className="label-eyebrow">Overview</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">
        {isPlatformAdmin ? "Platform overview" : "Your stores"}
      </h1>
      <p className="mt-1 text-sm text-parchment/50">Signed in as {me?.email}.</p>

      {loading ? (
        <p className="mt-6 text-sm text-parchment/40">Loading…</p>
      ) : (
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3">
          {isPlatformAdmin && (
            <StatCard label="Retailers" value={retailers.length} to="/retailers" />
          )}
          <StatCard label={isPlatformAdmin ? "Stores" : "Your stores"} value={stores.length} to="/stores" />
          {isPlatformAdmin && (
            <StatCard label="Deliveries awaiting dispatch" value={pendingDeliveries.length} to="/deliveries" tone="brass" />
          )}
        </div>
      )}

      {!loading && stores.length === 0 && (
        <div className="mt-8 rounded-xl border border-dashed border-ink-700 p-6 text-center">
          <p className="text-sm text-parchment/50">
            {isPlatformAdmin
              ? "No stores yet — create a retailer, verify it, then add a store."
              : "No stores set up under your account yet."}
          </p>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, to, tone }: { label: string; value: number; to: string; tone?: "brass" }) {
  return (
    <Link
      to={to}
      className="rounded-xl border border-ink-700 bg-ink-800/60 p-4 transition-colors hover:border-brass-600/40"
    >
      <p className="text-xs text-parchment/50">{label}</p>
      <p className={`mt-1 font-mono text-2xl ${tone === "brass" ? "text-brass-400" : "text-parchment"}`}>
        {value}
      </p>
    </Link>
  );
}
