import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, ApiRequestError } from "../api/client";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

// Placeholder coordinates — see HomePage.tsx note on real geolocation.
const DEFAULT_LAT = 19.08;
const DEFAULT_LNG = 72.88;

export function CheckoutPage() {
  const { lines, storeId, subtotal, clear } = useCart();
  const { isLoggedIn, me } = useAuth();
  const [address, setAddress] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  if (lines.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <p className="text-parchment/70">Your cart is empty.</p>
        <Link to="/" className="mt-2 inline-block text-sm text-brass-400 hover:text-brass-300">
          Browse products
        </Link>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <p className="text-parchment/70">Log in to check out.</p>
        <Link
          to="/login"
          className="mt-3 inline-block rounded-lg bg-brass-500 px-4 py-2 text-sm font-medium text-ink-950 hover:bg-brass-400"
        >
          Log in
        </Link>
      </div>
    );
  }

  if (me && me.eligibility_state !== "VERIFIED") {
    return (
      <div className="mx-auto max-w-lg px-4 py-20 text-center">
        <p className="text-parchment/70">Verify your age and delivery location before checking out.</p>
        <Link
          to="/eligibility"
          className="mt-3 inline-block rounded-lg bg-brass-500 px-4 py-2 text-sm font-medium text-ink-950 hover:bg-brass-400"
        >
          Verify eligibility
        </Link>
      </div>
    );
  }

  async function handlePlaceOrder(e: React.FormEvent) {
    e.preventDefault();
    if (!storeId) return;
    setError(null);
    setBusy(true);
    try {
      const order = await api.placeOrder({
        store_id: storeId,
        items: lines.map((l) => ({ product_id: l.product_id, quantity: l.quantity })),
        delivery_address: address,
        delivery_latitude: DEFAULT_LAT,
        delivery_longitude: DEFAULT_LNG,
      });
      clear();
      navigate(`/orders/${order.id}`);
    } catch (err) {
      // These are exactly the server-side checks re-run at checkout —
      // stock or eligibility may have changed since items were added
      // to the cart, and the backend is the one enforcing it here.
      setError(err instanceof ApiRequestError ? err.message : "Couldn't place your order.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-6">
      <h1 className="font-display text-2xl text-parchment">Checkout</h1>

      <form onSubmit={handlePlaceOrder} className="mt-6 flex flex-col gap-3">
        <label className="text-xs text-parchment/50" htmlFor="address">
          Delivery address
        </label>
        <textarea
          id="address"
          required
          rows={3}
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Flat, street, landmark, city, PIN"
          className="rounded-lg border border-ink-600 bg-ink-800 px-3 py-2 text-sm text-parchment outline-none focus:border-brass-500"
        />

        <div className="mt-2 rounded-lg border border-ink-700 bg-ink-800/50 p-3 font-mono text-sm text-parchment/70">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>₹{subtotal.toFixed(0)}</span>
          </div>
          <p className="mt-1 text-xs text-parchment/40">
            Final total (incl. delivery fee) is confirmed on the next screen.
          </p>
        </div>

        {error && (
          <p className="rounded-lg border border-rust-600/30 bg-rust-500/5 px-3 py-2 text-sm text-rust-400">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="mt-2 rounded-lg bg-brass-500 py-3 text-sm font-medium text-ink-950 hover:bg-brass-400 disabled:opacity-50"
        >
          {busy ? "Placing order…" : "Place order"}
        </button>
      </form>
    </div>
  );
}
