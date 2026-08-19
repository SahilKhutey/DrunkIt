import { Link } from "react-router-dom";
import { Seal } from "./Seal";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-ink-700">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <span className="font-display text-sm text-parchment/60">
            Drunk<span className="text-brass-500">It</span>
          </span>
          <Seal label="Verified platform" tone="brass" />
        </div>

        <nav className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-parchment/50">
          <Link to="/about" className="hover:text-parchment">
            About
          </Link>
          <Link to="/responsible-drinking" className="hover:text-parchment">
            Responsible drinking
          </Link>
          <Link to="/account" className="hover:text-parchment">
            Account
          </Link>
        </nav>
      </div>
    </footer>
  );
}
