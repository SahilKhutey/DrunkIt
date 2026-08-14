import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import { useAuth } from "../context/AuthContext";

// Placeholder list — the platform only actually serves whichever
// states are set to allow_delivery: true in the backend's
// policies/jurisdictions.json, which ships empty of real data. This
// dropdown intentionally lists all states so the "not currently
// available here" response is visible and honest, rather than
// quietly hiding the reality that most states aren't enabled yet.
const INDIAN_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
  "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
  "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi",
];

export function EligibilityPage() {
  const [state, setState] = useState("");
  const [dob, setDob] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { refreshMe, setDeliveryState } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const result = await api.verifyEligibility(state, dob);
      setDeliveryState(result.state);
      await refreshMe();
      if (result.can_checkout) {
        navigate("/");
      } else {
        setError(result.reason);
      }
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Couldn't verify eligibility.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center px-4">
      <h1 className="font-display text-2xl text-parchment">Verify to order</h1>
      <p className="mt-1 text-sm text-parchment/50">
        Regulated products require a one-time age and location check, enforced by our platform on
        every order — not just shown in this form.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3">
        <label className="text-xs text-parchment/50" htmlFor="state">
          Delivery state
        </label>
        <select
          id="state"
          required
          value={state}
          onChange={(e) => setState(e.target.value)}
          className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 text-parchment outline-none focus:border-brass-500"
        >
          <option value="" disabled>
            Select your state
          </option>
          {INDIAN_STATES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <label className="mt-2 text-xs text-parchment/50" htmlFor="dob">
          Date of birth
        </label>
        <input
          id="dob"
          type="date"
          required
          value={dob}
          onChange={(e) => setDob(e.target.value)}
          className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 font-mono text-parchment outline-none focus:border-brass-500"
        />

        {error && (
          <p className="rounded-lg border border-rust-600/30 bg-rust-500/5 px-3 py-2 text-sm text-rust-400">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="mt-2 rounded-lg bg-brass-500 py-2.5 text-sm font-medium text-ink-950 hover:bg-brass-400 disabled:opacity-50"
        >
          {busy ? "Checking…" : "Verify"}
        </button>
      </form>
    </div>
  );
}
