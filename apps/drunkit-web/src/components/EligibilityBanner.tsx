import { Link } from "react-router-dom";
import type { Me } from "../types/api";

export function EligibilityBanner({ me }: { me: Me | null }) {
  if (!me) {
    return (
      <div className="flex items-center justify-between rounded-lg border border-brass-600/30 bg-brass-500/5 px-4 py-3">
        <p className="text-sm text-parchment/80">Log in and verify your age to order.</p>
        <Link to="/login" className="text-sm font-medium text-brass-400 hover:text-brass-300">
          Log in →
        </Link>
      </div>
    );
  }

  if (me.eligibility_state === "VERIFIED") return null;

  const message =
    me.eligibility_state === "FAILED"
      ? "We couldn't verify you're eligible to order in your state right now."
      : "Verify your age and delivery location to start ordering.";

  return (
    <div className="flex items-center justify-between rounded-lg border border-brass-600/30 bg-brass-500/5 px-4 py-3">
      <p className="text-sm text-parchment/80">{message}</p>
      <Link to="/eligibility" className="text-sm font-medium text-brass-400 hover:text-brass-300">
        Verify now →
      </Link>
    </div>
  );
}
