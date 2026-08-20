import { useEffect, useState } from "react";
import { api, ApiRequestError } from "../api/client";
import type { RetailerView, StaffAccountView } from "../types/api";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { Badge } from "../components/ui/Badge";
import { useToast } from "../components/ui/Toast";

const STATUS_TONE = { PENDING: "copper", VERIFIED: "sage", SUSPENDED: "rust" } as const;

export function RetailersPage() {
  const { showToast } = useToast();
  const [retailers, setRetailers] = useState<RetailerView[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [staffModalRetailer, setStaffModalRetailer] = useState<RetailerView | null>(null);

  function load() {
    setLoading(true);
    api
      .listRetailers()
      .then(setRetailers)
      .catch((err) => showToast(err instanceof ApiRequestError ? err.message : "Couldn't load retailers.", "error"))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleVerify(id: string) {
    try {
      await api.verifyRetailer(id);
      showToast("Retailer verified", "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't verify retailer.", "error");
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <p className="label-eyebrow">Retailers</p>
          <h1 className="mt-1 font-display text-2xl text-parchment">Retailer accounts</h1>
        </div>
        <Button onClick={() => setCreateOpen(true)}>New retailer</Button>
      </div>

      <div className="mt-6 overflow-x-auto rounded-xl border border-ink-700">
        <table className="data-table w-full">
          <thead>
            <tr>
              <th>Name</th>
              <th>License #</th>
              <th>Status</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} className="text-center text-parchment/40">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && retailers.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center text-parchment/40">
                  No retailers yet.
                </td>
              </tr>
            )}
            {retailers.map((r) => (
              <tr key={r.id}>
                <td className="font-medium text-parchment">{r.name}</td>
                <td className="font-mono text-parchment/60">{r.license_number ?? "—"}</td>
                <td>
                  <Badge tone={STATUS_TONE[r.status]}>{r.status}</Badge>
                </td>
                <td className="text-parchment/50">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="text-right">
                  <div className="flex justify-end gap-2">
                    {r.status !== "VERIFIED" && (
                      <Button size="sm" variant="secondary" onClick={() => handleVerify(r.id)}>
                        Verify
                      </Button>
                    )}
                    <Button size="sm" variant="ghost" onClick={() => setStaffModalRetailer(r)}>
                      Staff
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <CreateRetailerModal open={createOpen} onClose={() => setCreateOpen(false)} onCreated={load} />
      {staffModalRetailer && (
        <RetailerStaffModal retailer={staffModalRetailer} onClose={() => setStaffModalRetailer(null)} />
      )}
    </div>
  );
}

function CreateRetailerModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: () => void }) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [license, setLicense] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.createRetailer(name, license || undefined);
      showToast("Retailer created", "success");
      setName("");
      setLicense("");
      onClose();
      onCreated();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't create retailer.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New retailer">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <Input label="Name" required value={name} onChange={(e) => setName(e.target.value)} />
        <Input
          label="License number (optional)"
          value={license}
          onChange={(e) => setLicense(e.target.value)}
        />
        <div className="mt-2 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={busy}>
            Create
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function RetailerStaffModal({ retailer, onClose }: { retailer: RetailerView; onClose: () => void }) {
  const { showToast } = useToast();
  const [accounts, setAccounts] = useState<StaffAccountView[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  function load() {
    api.listRetailerStaff(retailer.id).then(setAccounts).catch(() => {});
  }
  useEffect(load, [retailer.id]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.createRetailerStaff(retailer.id, email, password);
      showToast("Staff account created", "success");
      setEmail("");
      setPassword("");
      load();
    } catch (err) {
      showToast(err instanceof ApiRequestError ? err.message : "Couldn't create staff account.", "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open onClose={onClose} title={`Staff — ${retailer.name}`}>
      <ul className="flex flex-col gap-1.5">
        {accounts.length === 0 && <li className="text-sm text-parchment/40">No staff accounts yet.</li>}
        {accounts.map((a) => (
          <li key={a.id} className="flex items-center justify-between rounded-lg bg-ink-700/50 px-3 py-1.5 text-sm">
            <span className="font-mono">{a.email}</span>
            <span className="text-xs text-parchment/40">{a.active ? "active" : "inactive"}</span>
          </li>
        ))}
      </ul>

      <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3 border-t border-ink-700 pt-4">
        <p className="text-xs text-parchment/50">Add a new staff login for this retailer.</p>
        <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        <Input
          label="Password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Close
          </Button>
          <Button type="submit" loading={busy}>
            Add staff
          </Button>
        </div>
      </form>
    </Modal>
  );
}
