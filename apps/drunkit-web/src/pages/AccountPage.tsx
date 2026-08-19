import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Seal } from "../components/Seal";

const ELIGIBILITY_TONE = {
  VERIFIED: "sage",
  FAILED: "rust",
  NOT_STARTED: "neutral",
  EXPIRED: "copper",
} as const;

export function AccountPage() {
  const { me, deliveryState, logout, loading } = useAuth();
  const navigate = useNavigate();

  if (loading) {
    return <div className="mx-auto max-w-md px-4 py-10 text-parchment/50">Loading…</div>;
  }

  if (!me) {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-md flex-col items-center justify-center px-4 text-center">
        <p className="text-sm text-parchment/60">You're not logged in.</p>
        <Link to="/login" className="mt-4">
          <Button>Log in</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <p className="label-eyebrow">Account</p>
      <h1 className="mt-1 font-display text-2xl text-parchment">{me.phone}</h1>

      <div className="mt-6 flex flex-col gap-4 rounded-xl border border-ink-700 bg-ink-800/60 p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-parchment/60">Eligibility</span>
          <Badge tone={ELIGIBILITY_TONE[me.eligibility_state]}>{me.eligibility_state}</Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-parchment/60">Delivery state</span>
          <span className="text-sm text-parchment">{deliveryState ?? "Not set"}</span>
        </div>
        {me.eligibility_state === "VERIFIED" && (
          <Seal label="Age verified" tone="sage" />
        )}
      </div>

      <div className="mt-6 flex flex-col gap-2">
        <Link to="/eligibility">
          <Button variant="secondary" className="w-full">
            {me.eligibility_state === "VERIFIED" ? "Update delivery state" : "Verify eligibility"}
          </Button>
        </Link>
        <Link to="/orders">
          <Button variant="secondary" className="w-full">
            Order history
          </Button>
        </Link>
        <Button
          variant="ghost"
          className="w-full"
          onClick={() => {
            logout();
            navigate("/");
          }}
        >
          Log out
        </Button>
      </div>
    </div>
  );
}
