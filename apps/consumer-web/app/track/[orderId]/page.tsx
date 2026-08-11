'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { RealtimeClient } from '@faccp/realtime-client';

export default function TrackOrderPage() {
  const params = useParams();
  const orderId = params?.orderId as string;
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    if (!orderId) return;
    const token = typeof window !== 'undefined' ? localStorage.getItem('faccp_access_token') || '' : '';
    const wsBase = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8016';
    const client = new RealtimeClient({ baseUrl: wsBase, token, channel: `order:${orderId}` });

    client.connect().catch(console.error);
    client.on((event: any) => {
      setEvents((prev) => [event, ...prev].slice(0, 50));
    });

    return () => client.disconnect();
  }, [orderId]);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Order Tracking</h1>
      <p className="text-gray-400 mb-4">Order ID: {orderId}</p>
      <div className="bg-slate-800 rounded-lg shadow p-4 border border-slate-700">
        <h2 className="font-semibold text-white mb-3">Live Stream Updates</h2>
        {events.length === 0 ? (
          <p className="text-gray-400">Waiting for live updates...</p>
        ) : (
          <ul className="space-y-2">
            {events.map((e, i) => (
              <li key={i} className="border-l-4 border-indigo-500 pl-3 py-1 bg-slate-900/50 rounded-r">
                <div className="font-medium text-slate-200">{e.type}</div>
                <div className="text-xs text-slate-400">
                  {new Date(e.occurred_at || Date.now()).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
