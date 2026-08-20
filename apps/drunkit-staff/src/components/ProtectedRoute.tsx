import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn, loading } = useAuth();

  if (loading) {
    return <div className="flex min-h-screen items-center justify-center text-parchment/50">Loading…</div>;
  }
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export function AdminOnlyRoute({ children }: { children: React.ReactNode }) {
  const { isPlatformAdmin, loading } = useAuth();
  if (loading) return null;
  if (!isPlatformAdmin) {
    return (
      <div className="rounded-xl border border-rust-600/30 bg-rust-500/5 p-6 text-center">
        <p className="text-sm text-rust-400">This page is only available to platform admins.</p>
      </div>
    );
  }
  return <>{children}</>;
}
