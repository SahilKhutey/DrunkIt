"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { MapPin, Navigation, CheckCircle, Package } from "lucide-react";
import { apiClient } from "@/lib/api-client";

export default function DriverDashboard() {
  const qc = useQueryClient();
  const [online, setOnline] = useState(true);

  const { data: missions } = useQuery({
    queryKey: ["driver-missions", online],
    queryFn: () => apiClient.get("/api/v1/delivery/missions?active_only=true"),
  });

  const toggleOnline = useMutation({
    mutationFn: () => apiClient.post("/api/v1/delivery/online-toggle", { online: !online }),
    onSuccess: () => {
      setOnline(!online);
      qc.invalidateQueries({ queryKey: ["driver-missions"] });
    },
  });

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded-lg shadow-sm flex justify-between items-center">
        <div>
          <h2 className="font-bold text-gray-800">Driver Status</h2>
          <p className="text-xs text-gray-500">{online ? "Ready to accept missions" : "Offline"}</p>
        </div>
        <button
          onClick={() => toggleOnline.mutate()}
          className={`px-4 py-2 rounded-full text-sm font-semibold text-white ${online ? "bg-green-600 hover:bg-green-700" : "bg-gray-500 hover:bg-gray-600"}`}
        >
          {online ? "ONLINE" : "OFFLINE"}
        </button>
      </div>

      <h3 className="font-bold text-sm text-gray-700 uppercase">Assigned Missions ({missions?.items?.length ?? 0})</h3>

      <div className="space-y-3">
        {missions?.items?.map((m: any) => (
          <Link key={m.id} href={`/missions/${m.id}`} className="block bg-white p-4 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">{m.state}</span>
              <span className="text-xs text-gray-400">ETA {m.eta_minutes} min</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2 text-gray-700">
                <Package size={16} className="text-blue-500" />
                <span className="font-medium">Order #{m.order_id?.slice(0, 8)}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <MapPin size={16} className="text-green-600" />
                <span>{m.pickup_address?.address_line1 || "Store location"}</span>
              </div>
            </div>
          </Link>
        ))}

        {!missions?.items?.length && (
          <div className="bg-white p-8 text-center rounded-lg text-gray-500 text-sm">
            No active missions. Stay online for new dispatches.
          </div>
        )}
      </div>
    </div>
  );
}
