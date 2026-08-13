"use client";

import { useState, use } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { MapPin, Navigation, CheckCircle, ShieldCheck } from "lucide-react";
import { apiClient } from "@/lib/api-client";

export default function MissionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const qc = useQueryClient();
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: mission, isLoading } = useQuery({
    queryKey: ["mission", id],
    queryFn: () => apiClient.get(`/api/v1/delivery/missions/${id}`),
  });

  const updateState = useMutation({
    mutationFn: (target_state: string) => apiClient.post(`/api/v1/delivery/missions/${id}/transitions`, { target_state }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mission", id] }),
  });

  const verifyOtp = useMutation({
    mutationFn: () => apiClient.post(`/api/v1/delivery/missions/${id}/complete`, { otp, verification_method: "DOORSTEP_OTP" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mission", id] }),
    onError: (e: any) => setError(e.message),
  });

  if (isLoading) return <div className="p-4 text-center">Loading mission...</div>;
  if (!mission) return <div className="p-4 text-center">Mission not found</div>;

  const m = mission.data || mission;

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-2">
          <h2 className="font-bold text-lg">Mission #{id.slice(0, 8)}</h2>
          <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800 font-bold">{m.state}</span>
        </div>
        <p className="text-xs text-gray-500">Order #{m.order_id}</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm space-y-3 text-sm">
        <h3 className="font-bold text-gray-700">Pickup Address</h3>
        <p className="text-gray-600">{m.pickup_address?.address_line1 || "Main Store Depot"}</p>

        <h3 className="font-bold text-gray-700 border-t pt-2">Delivery Address</h3>
        <p className="text-gray-600">{m.delivery_address?.address_line1 || "Consumer doorstep"}</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm space-y-3">
        <h3 className="font-bold text-sm text-gray-700">Mission Actions</h3>

        {m.state === "ASSIGNED" && (
          <button onClick={() => updateState.mutate("PICKING_UP")} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2">
            <Navigation size={18} /> Head to Pickup
          </button>
        )}

        {m.state === "PICKING_UP" && (
          <button onClick={() => updateState.mutate("PICKED_UP")} className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2">
            <CheckCircle size={18} /> Confirm Items Picked Up
          </button>
        )}

        {m.state === "PICKED_UP" && (
          <button onClick={() => updateState.mutate("IN_TRANSIT")} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2">
            <Navigation size={18} /> Start Transit to Consumer
          </button>
        )}

        {m.state === "IN_TRANSIT" && (
          <button onClick={() => updateState.mutate("HANDOFF_PENDING")} className="w-full bg-amber-600 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2">
            <MapPin size={18} /> Arrived at Doorstep
          </button>
        )}

        {m.state === "HANDOFF_PENDING" && (
          <div className="space-y-3 border-t pt-3">
            <div className="flex items-center gap-2 text-green-700 font-bold text-sm">
              <ShieldCheck size={20} /> Doorstep Age & OTP Verification
            </div>
            <input
              value={otp}
              onChange={e => setOtp(e.target.value)}
              placeholder="Enter 4-digit Customer OTP"
              className="w-full border-2 border-blue-500 rounded-lg p-3 text-center text-lg font-bold tracking-widest"
              maxLength={6}
            />
            {error && <p className="text-red-500 text-xs">{error}</p>}
            <button onClick={() => verifyOtp.mutate()} disabled={verifyOtp.isPending || !otp} className="w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 disabled:opacity-50">
              {verifyOtp.isPending ? "Verifying..." : "Complete Delivery"}
            </button>
          </div>
        )}

        {m.state === "DELIVERED" && (
          <div className="bg-green-50 p-4 rounded-lg text-center text-green-800 font-bold">
            ✓ Mission Completed Successfully!
          </div>
        )}
      </div>
    </div>
  );
}
