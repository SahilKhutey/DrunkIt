import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function Navbar() {
  const { me, isLoggedIn, logout } = useAuth();
  const { itemCount, subtotal } = useCart();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-20 border-b border-ink-700 bg-ink-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="font-display text-xl tracking-tight text-parchment">
          Drunk<span className="text-brass-500">It</span>
        </Link>

        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              <Link
                to="/orders"
                className="hidden sm:inline text-sm text-parchment/70 hover:text-parchment transition-colors"
              >
                Orders
              </Link>
              <span className="hidden sm:inline text-sm text-parchment/50 font-mono">{me?.phone}</span>
              <button
                onClick={() => {
                  logout();
                  navigate("/");
                }}
                className="text-sm text-parchment/50 hover:text-rust-400 transition-colors"
              >
                Log out
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-lg border border-brass-600/50 px-3 py-1.5 text-sm text-brass-400 hover:bg-brass-500/10 transition-colors"
            >
              Log in
            </Link>
          )}

          <Link
            to="/cart"
            className="relative rounded-lg bg-ink-800 px-3 py-1.5 text-sm text-parchment hover:bg-ink-700 transition-colors"
          >
            Cart
            {itemCount > 0 && (
              <span className="ml-2 font-mono text-brass-400">₹{subtotal.toFixed(0)}</span>
            )}
            {itemCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-brass-500 px-1 text-[10px] font-bold text-ink-950">
                {itemCount}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
