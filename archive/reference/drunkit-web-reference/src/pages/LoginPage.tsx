import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { ApiRequestError } from "../api/client";

export function LoginPage() {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [stage, setStage] = useState<"phone" | "otp">("phone");
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { refreshMe } = useAuth();

  async function handleRequestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await api.requestOtp(phone);
      setDevOtp(res.dev_otp);
      setStage("otp");
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Couldn't send a code. Try again.");
    } finally {
      setBusy(false);
    }
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await api.verifyOtp(phone, code);
      setToken(res.access_token);
      await refreshMe();
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Verification failed. Try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-sm flex-col justify-center px-4">
      <h1 className="font-display text-2xl text-parchment">
        {stage === "phone" ? "Log in" : "Enter the code"}
      </h1>
      <p className="mt-1 text-sm text-parchment/50">
        {stage === "phone"
          ? "We'll text you a 6-digit code to verify it's you."
          : `Sent to ${phone}.`}
      </p>

      {stage === "phone" ? (
        <form onSubmit={handleRequestOtp} className="mt-6 flex flex-col gap-3">
          <label className="text-xs text-parchment/50" htmlFor="phone">
            Phone number
          </label>
          <input
            id="phone"
            type="tel"
            required
            minLength={8}
            maxLength={15}
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="9XXXXXXXXX"
            className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 font-mono text-parchment outline-none focus:border-brass-500"
          />
          {error && <p className="text-sm text-rust-400">{error}</p>}
          <button
            type="submit"
            disabled={busy}
            className="mt-2 rounded-lg bg-brass-500 py-2.5 text-sm font-medium text-ink-950 hover:bg-brass-400 disabled:opacity-50"
          >
            {busy ? "Sending…" : "Send code"}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyOtp} className="mt-6 flex flex-col gap-3">
          <label className="text-xs text-parchment/50" htmlFor="code">
            6-digit code
          </label>
          <input
            id="code"
            type="text"
            inputMode="numeric"
            required
            minLength={6}
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
            placeholder="000000"
            className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 font-mono text-lg tracking-[0.3em] text-parchment outline-none focus:border-brass-500"
          />
          {devOtp && (
            <p className="rounded-lg border border-brass-600/30 bg-brass-500/5 px-3 py-2 text-xs text-brass-400">
              Dev mode — your code is <span className="font-mono font-bold">{devOtp}</span>. This
              banner disappears once a real SMS provider is wired in.
            </p>
          )}
          {error && <p className="text-sm text-rust-400">{error}</p>}
          <button
            type="submit"
            disabled={busy}
            className="mt-2 rounded-lg bg-brass-500 py-2.5 text-sm font-medium text-ink-950 hover:bg-brass-400 disabled:opacity-50"
          >
            {busy ? "Verifying…" : "Verify and continue"}
          </button>
          <button
            type="button"
            onClick={() => setStage("phone")}
            className="text-xs text-parchment/40 hover:text-parchment/70"
          >
            Use a different number
          </button>
        </form>
      )}
    </div>
  );
}
