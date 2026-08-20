import { useEffect, useState } from "react";
import { api, ApiRequestError } from "../api/client";
import type { AdminDeliveryView } from "../types/api";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Modal } from "../components/ui/Modal";
import { Badge } from "../components/ui/Badge";
import { useToast } from "../components/ui/Toast";

const STATUS_TONE: Record<string, "neutral" | "brass" | "sage" | "rust" | "copper"> = {
  REQUESTED: "copper",
  ASSIGNED: "brass",
  PICKED_UP: "brass",
  IN_TRANSIT: "brass",
  ARRIVING: "brass",
  HANDOFF_VERIFICATION: "copper",
  DELIVERED: "sage",
  FAILED: "rust",
  CANCELLED: "neutral",
};

// The forward-progress transitions an ops person can trigger with one
// click — mirrors the backend's _ALLOWED_TRANSITIONS in
// delivery/service.py. Assign and handoff have their own dedicated
// actions/endpoints, so they're intentionally not in this list.
const NEXT_STATUS: Record<string, string | null> = {
  ASSIGNED: "PICKED_UP",
  PICKED_UP: "IN_TRANSIT",
  IN_TRANSIT: "ARRIVING",
  ARRIVING: "HANDOFF_VERIFICATION",
};

const STATUS_FILTERS = ["", "REQUESTED", "ASSIGNED", "PICKED_UP", "IN_TRANSIT", "ARRIVING", "HANDOFF_VERIFICATION", "DELIVERED", "FAILED", "CANCELLED"];

export function DeliveriesPage() {
  const { showToast } = useToast();
  const [statusFilter, setStatusFilter] = useState("");
  const [deliveries, setDeliveries] = useState<AdminDeliveryView[]>([]);
  const [loading, setLoading] = useState(true);
  const [assignTarget, setAssignTarget] = useState<AdminDeliveryView | null>(null);
  const [handoffTarget, setHandoffTarget] = useState<AdminDeliveryView | null>(null);

  function load() {
    setLoading(true);
    api
      .listDeliveries(statusFilter || undefined)
      .then(setDeliveries)
      .catch((err) => showToast(err instanceof ApiRequestError ? err.message : "Couldn't load deliveries.", "error"))
      .finally(() => setLoading(false));
  }
  useEffect(load, [statusFilter]);

  async function handleAdvance(d: AdminDeliveryView) {
    const next = NEXT_STATUS[d.status];
    if (!next) return;
    try {
      await api.transitionDelivery(d.id, next);
      showToast(`Moved to ${next.replace(/_/g, " ")}`, "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't update delivery.", "error");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="label-eyebrow">Deliveries</p>
          <h1 className="mt-1 font-display text-2xl text-parchment">Dispatch console</h1>
        </div>
        <div className="w-48">
          <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            {STATUS_FILTERS.map((s) => (
              <option key={s} value={s}>{s ? s.replace(/_/g, " ") : "All statuses"}</option>
            ))}
          </Select>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3">
        {loading && <p className="text-sm text-parchment/40">Loading…</p>}
        {!loading && deliveries.length === 0 && <p className="text-sm text-parchment/40">No deliveries match this filter.</p>}

        {deliveries.map((d) => (
          <div key={d.id} className="flex items-center justify-between rounded-xl border border-ink-700 bg-ink-800/60 p-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-parchment/50">#{d.id.slice(0, 8)}</span>
                <Badge tone={STATUS_TONE[d.status] ?? "neutral"}>{d.status.replace(/_/g, " ")}</Badge>
              </div>
              <p className="mt-1 text-sm text-parchment">{d.store_name}</p>
              {d.driver_name && (
                <p className="text-xs text-parchment/50">{d.driver_name} · {d.driver_phone}</p>
              )}
              {d.eta_min_minutes != null && (
                <p className="text-xs font-mono text-parchment/40">ETA {d.eta_min_minutes}–{d.eta_max_minutes} min</p>
              )}
            </div>

            <div className="flex gap-2">
              {d.status === "REQUESTED" && (
                <Button size="sm" onClick={() => setAssignTarget(d)}>Assign driver</Button>
              )}
              {NEXT_STATUS[d.status] && (
                <Button size="sm" variant="secondary" onClick={() => handleAdvance(d)}>
                  → {NEXT_STATUS[d.status]!.replace(/_/g, " ")}
                </Button>
              )}
              {d.status === "HANDOFF_VERIFICATION" && (
                <Button size="sm" onClick={() => setHandoffTarget(d)}>Verify handoff</Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {assignTarget && (
        <AssignDriverModal delivery={assignTarget} onClose={() => setAssignTarget(null)} onDone={load} />
      )}
      {handoffTarget && (
        <HandoffModal delivery={handoffTarget} onClose={() => setHandoffTarget(null)} onDone={load} />
      )}
    </div>
  );
}

function AssignDriverModal({ delivery, onClose, onDone }: { delivery: AdminDeliveryView; onClose: () => void; onDone: () => void }) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.assignDriver(delivery.id, name, phone);
      showToast("Driver assigned", "success");
      onClose();
      onDone();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't assign driver.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Assign driver">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <Input label="Driver name" required value={name} onChange={(e) => setName(e.target.value)} />
        <Input label="Driver phone" required value={phone} onChange={(e) => setPhone(e.target.value)} />
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={busy}>Assign</Button>
        </div>
      </form>
    </Modal>
  );
}

function HandoffModal({ delivery, onClose, onDone }: { delivery: AdminDeliveryView; onClose: () => void; onDone: () => void }) {
  const { showToast } = useToast();
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleDecision(verified: boolean) {
    setBusy(true);
    try {
      await api.verifyHandoff(delivery.id, verified, verified ? undefined : reason);
      showToast(verified ? "Delivery marked as delivered" : "Delivery marked as failed", verified ? "success" : "error");
      onClose();
      onDone();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't record handoff.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open onClose={onClose} title="Verify handoff">
      <p className="text-sm text-parchment/60">
        Confirm the controlled handoff for this delivery. The actual verification method (ID
        scan, OTP, etc.) is a policy decision outside this console — this records the outcome.
      </p>
      <Input
        label="Failure reason (if declining)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        className="mt-3"
      />
      <div className="mt-4 flex justify-end gap-2">
        <Button variant="danger" loading={busy} onClick={() => handleDecision(false)}>
          Failed
        </Button>
        <Button loading={busy} onClick={() => handleDecision(true)}>
          Verified — mark delivered
        </Button>
      </div>
    </Modal>
  );
}
