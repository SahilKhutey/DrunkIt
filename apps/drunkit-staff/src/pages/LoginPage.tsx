import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken, ApiRequestError } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const { refreshMe } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await api.login(email, password);
      setToken(res.access_token);
      await refreshMe();
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Couldn't log in.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-sm flex-col justify-center px-4">
      <p className="label-eyebrow">Staff console</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">
        Drunk<span className="text-brass-500">It</span>
      </h1>
      <p className="mt-1 text-sm text-parchment/50">Retailer and platform operations.</p>

      <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-3">
        <Input
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
        />
        <Input
          label="Password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && (
          <p className="rounded-lg border border-rust-600/30 bg-rust-500/5 px-3 py-2 text-sm text-rust-400">
            {error}
          </p>
        )}
        <Button type="submit" loading={busy} className="mt-2">
          {busy ? "Signing in…" : "Sign in"}
        </Button>
      </form>

      <p className="mt-6 text-xs text-parchment/30">
        Accounts are created by a platform admin — there's no self-registration here.
      </p>
    </div>
  );
}
