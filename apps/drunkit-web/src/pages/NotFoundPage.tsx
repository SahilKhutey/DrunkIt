import { Link } from "react-router-dom";
import { Seal } from "../components/Seal";
import { Button } from "../components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col items-center justify-center px-4 text-center">
      <Seal label="Unverified route" tone="brass" size="md" />
      <h1 className="mt-4 font-display text-3xl text-parchment">Page not found</h1>
      <p className="mt-2 text-sm text-parchment/50">
        Whatever you were looking for isn't here — it may have moved, or the link was off.
      </p>
      <Link to="/" className="mt-6">
        <Button>Back to browsing</Button>
      </Link>
    </div>
  );
}
