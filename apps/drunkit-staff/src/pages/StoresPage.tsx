import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import type { StoreView, RetailerView } from "../types/api";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Modal } from "../components/ui/Modal";
import { Badge } from "../components/ui/Badge";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/ui/Toast";

export function StoresPage() {
  const { isPlatformAdmin, me } = useAuth();
  const { showToast } = useToast();
  const [stores, setStores] = useState<StoreView[]>([]);
  const [retailers, setRetailers] = useState<RetailerView[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  function load() {
    setLoading(true);
    Promise.all([api.listStores(), isPlatformAdmin ? api.listRetailers() : Promise.resolve([])])
      .then(([s, r]) => {
        setStores(s);
        setRetailers(r);
      })
      .catch((err) => showToast(err instanceof ApiRequestError ? err.message : "Couldn't load stores.", "error"))
      .finally(() => setLoading(false));
  }
  useEffect(load, [isPlatformAdmin]);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="label-eyebrow">Stores</p>
          <h1 className="mt-1 font-display text-2xl text-parchment">
            {isPlatformAdmin ? "All stores" : "Your stores"}
          </h1>
        </div>
        <Button
          onClick={() => setCreateOpen(true)}
          disabled={!isPlatformAdmin && !me?.retailer_id}
        >
          New store
        </Button>
      </div>

      <div className="mt-6 overflow-x-auto rounded-xl border border-ink-700">
        <table className="data-table w-full">
          <thead>
            <tr>
              <th>Name</th>
              {isPlatformAdmin && <th>Retailer</th>}
              <th>Location</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="text-center text-parchment/40">Loading…</td>
              </tr>
            )}
            {!loading && stores.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-parchment/40">No stores yet.</td>
              </tr>
            )}
            {stores.map((s) => (
              <tr key={s.id}>
                <td className="font-medium text-parchment">{s.name}</td>
                {isPlatformAdmin && <td className="text-parchment/60">{s.retailer_name}</td>}
                <td className="text-parchment/60">{s.city}, {s.state}</td>
                <td>
                  <Badge tone={s.active && s.is_open ? "sage" : "neutral"}>
                    {s.active ? (s.is_open ? "Open" : "Closed") : "Inactive"}
                  </Badge>
                </td>
                <td className="text-right">
                  <Link to={`/listings?store_id=${s.id}`} className="text-xs text-brass-400 hover:text-brass-300">
                    View listings →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <CreateStoreModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={load}
        retailers={retailers}
        fixedRetailerId={isPlatformAdmin ? undefined : me?.retailer_id ?? undefined}
      />
    </div>
  );
}

function CreateStoreModal({
  open,
  onClose,
  onCreated,
  retailers,
  fixedRetailerId,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
  retailers: RetailerView[];
  fixedRetailerId?: string;
}) {
  const { showToast } = useToast();
  const [retailerId, setRetailerId] = useState(fixedRetailerId ?? "");
  const [name, setName] = useState("");
  const [state, setState] = useState("");
  const [city, setCity] = useState("");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const targetRetailerId = fixedRetailerId ?? retailerId;
    if (!targetRetailerId) return;
    setBusy(true);
    try {
      await api.createStore({
        retailer_id: targetRetailerId,
        name,
        state,
        city,
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
      });
      showToast("Store created", "success");
      onClose();
      onCreated();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't create store.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New store">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        {!fixedRetailerId && (
          <Select label="Retailer" required value={retailerId} onChange={(e) => setRetailerId(e.target.value)}>
            <option value="" disabled>Select a retailer</option>
            {retailers.map((r) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </Select>
        )}
        <Input label="Store name" required value={name} onChange={(e) => setName(e.target.value)} />
        <div className="grid grid-cols-2 gap-3">
          <Input label="State (jurisdiction key)" required value={state} onChange={(e) => setState(e.target.value)} placeholder="MAHARASHTRA" />
          <Input label="City" required value={city} onChange={(e) => setCity(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Input label="Latitude" type="number" step="any" required value={lat} onChange={(e) => setLat(e.target.value)} />
          <Input label="Longitude" type="number" step="any" required value={lng} onChange={(e) => setLng(e.target.value)} />
        </div>
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={busy}>Create</Button>
        </div>
      </form>
    </Modal>
  );
}
