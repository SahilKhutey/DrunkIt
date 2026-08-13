"use client";
import { useRouter } from "next/navigation";
import { LogOut, Navigation, User } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { clearDriverToken, apiClient } from "@/lib/api-client";

export function TopBar() {
  const router = useRouter();
  const { data: profile } = useQuery({
    queryKey: ["driver-me"],
    queryFn: () => apiClient.get("/api/v1/auth/me"),
  });
  function logout() {
    clearDriverToken();
    router.push("/login");
  }
  return (
    <header className="bg-primary-700 text-white p-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Navigation size={20} className="text-yellow-400" />
        <span className="font-bold text-lg">FACCP Driver</span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <span>{profile?.email?.split("@")[0] ?? "Driver"}</span>
        <button onClick={logout} className="p-1 hover:text-red-300" title="Logout">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
