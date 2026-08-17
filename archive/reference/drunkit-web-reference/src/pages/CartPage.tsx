import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";

const DELIVERY_FEE = 25; // matches the backend's flat placeholder fee — see order/service.py

export function CartPage() {
  const { lines, setQuantity, removeItem, subtotal, storeName } = useCart();
  const navigate = useNavigate();

  if (lines.length === 0) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-3 px-4 py-20 text-center">
        <p className="font-display text-xl text-parchment">Your cart is empty</p>
        <p className="text-sm text-parchment/50">Add something from the shelf to get started.</p>
        <Link
          to="/"
          className="mt-2 rounded-lg bg-brass-500 px-4 py-2 text-sm font-medium text-ink-950 hover:bg-brass-400"
        >
          Browse products
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <h1 className="font-display text-2xl text-parchment">Your cart</h1>
      {storeName && <p className="mt-1 text-sm text-parchment/50">From {storeName}</p>}

      <div className="mt-6 flex flex-col divide-y divide-ink-700 rounded-xl border border-ink-700">
        {lines.map((line) => (
          <div key={line.product_id} className="flex items-center justify-between gap-4 p-4">
            <div>
              <p className="text-sm text-parchment">{line.name}</p>
              <p className="text-xs text-parchment/50">{line.pack_size}</p>
              <p className="mt-1 font-mono text-sm text-brass-400">₹{line.unit_price.toFixed(0)}</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center rounded-lg border border-ink-600">
                <button
                  onClick={() => setQuantity(line.product_id, line.quantity - 1)}
                  className="px-3 py-1 text-parchment/70 hover:text-parchment"
                  aria-label={`Decrease quantity of ${line.name}`}
                >
                  −
                </button>
                <span className="w-6 text-center font-mono text-sm text-parchment">{line.quantity}</span>
                <button
                  onClick={() => setQuantity(line.product_id, line.quantity + 1)}
                  className="px-3 py-1 text-parchment/70 hover:text-parchment"
                  aria-label={`Increase quantity of ${line.name}`}
                >
                  +
                </button>
              </div>
              <button
                onClick={() => removeItem(line.product_id)}
                className="text-xs text-parchment/40 hover:text-rust-400"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-col gap-2 rounded-xl border border-ink-700 bg-ink-800/50 p-4 font-mono text-sm">
        <div className="flex justify-between text-parchment/70">
          <span>Subtotal</span>
          <span>₹{subtotal.toFixed(0)}</span>
        </div>
        <div className="flex justify-between text-parchment/70">
          <span>Delivery fee</span>
          <span>₹{DELIVERY_FEE.toFixed(0)}</span>
        </div>
        <div className="mt-1 flex justify-between border-t border-ink-700 pt-2 text-base text-parchment">
          <span>Total</span>
          <span>₹{(subtotal + DELIVERY_FEE).toFixed(0)}</span>
        </div>
      </div>

      <button
        onClick={() => navigate("/checkout")}
        className="mt-4 w-full rounded-lg bg-brass-500 py-3 text-sm font-medium text-ink-950 hover:bg-brass-400"
      >
        Proceed to checkout
      </button>
    </div>
  );
}
