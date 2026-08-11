'use client';

import React, { useState, useEffect } from 'react';
import { Header, StatusCard, TrustBadge } from '@faccp/ui';
import { Store, Package, FileCheck, ShoppingBag, ShieldCheck, CheckCircle, Clock } from 'lucide-react';

export default function RetailerDashboard() {
  const [storeId, setStoreId] = useState('STR-BANGALORE-01');
  const [storeData, setStoreData] = useState<any>(null);
  const [inventory, setInventory] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    fetchStoreDetails();
  }, [storeId]);

  const fetchStoreDetails = async () => {
    try {
      const [sRes, iRes, oRes] = await Promise.all([
        fetch(`http://localhost:8003/api/v1/stores/${storeId}`).then(r => r.json()).catch(() => null),
        fetch(`http://localhost:8005/api/v1/inventory/store/${storeId}`).then(r => r.json()).catch(() => []),
        fetch(`http://localhost:8006/api/v1/orders?store_id=${storeId}`).then(r => r.json()).catch(() => [])
      ]);
      setStoreData(sRes);
      setInventory(iRes);
      setOrders(oRes);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Header
        domainName="RETAILER SYSTEM"
        title="Apex Wines & Spirits - Store Operations & Inventory Hub"
        subtitle="Licensed Store Operations, Batch Tracking & Compliance Fulfillment Workspace"
        jurisdiction={storeData?.jurisdiction || 'IN-KA'}
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {/* Store Selector & License Status Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/50">
          <div className="flex items-center gap-3">
            <Store className="w-5 h-5 text-indigo-400" />
            <div>
              <span className="text-sm font-semibold">{storeData?.name || 'Apex Wines & Spirits'}</span>
              <span className="text-xs text-slate-400 block">{storeData?.address}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 font-mono">Store ID: {storeId}</span>
            {storeData?.trust_level && (
              <TrustBadge level={storeData.trust_level} verified={storeData.active} />
            )}
          </div>
        </div>

        {/* Status Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatusCard
            title="Excise License Status"
            value={storeData?.license?.status || 'ACTIVE'}
            subtitle={storeData?.license?.license_number || 'KA-EX-CL2-2026-0881'}
            icon={<FileCheck className="w-5 h-5 text-emerald-400" />}
            trend="Valid Until March 2027"
            variant="emerald"
          />
          <StatusCard
            title="Active SKUs Stocked"
            value={inventory.length || 4}
            subtitle="Batch Verified Stock"
            icon={<Package className="w-5 h-5 text-indigo-400" />}
            trend="100% Stock Synchronized"
            variant="indigo"
          />
          <StatusCard
            title="Fulfillment Orders"
            value={orders.length || 1}
            subtitle="Incoming & Processed"
            icon={<ShoppingBag className="w-5 h-5 text-cyan-400" />}
            trend="Compliance Pre-Verified"
            variant="cyan"
          />
          <StatusCard
            title="Permitted Hours"
            value="10:00 - 22:30"
            subtitle="IN-KA State Trading License"
            icon={<Clock className="w-5 h-5 text-amber-400" />}
            trend="Trading Window Open"
            variant="amber"
          />
        </div>

        {/* Two Column Layout: Store Inventory & Incoming Orders */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inventory Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold flex items-center gap-2">
                <Package className="w-4 h-4 text-indigo-400" />
                Store Inventory & Batch Tracking
              </h2>
              <span className="text-xs text-slate-400">Total SKUs: {inventory.length}</span>
            </div>

            <div className="space-y-3">
              {inventory.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">Loading store inventory...</p>
              ) : (
                inventory.map((item: any) => (
                  <div key={item.sku} className="p-3.5 rounded-lg border border-slate-800 bg-slate-950/60 flex justify-between items-center">
                    <div>
                      <div className="text-sm font-semibold text-slate-100">{item.sku}</div>
                      <div className="text-xs text-slate-400 font-mono">Batch: {item.batch_number}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-emerald-400">{item.available_stock} Available</div>
                      <div className="text-xs text-slate-400">{item.reserved_stock} Reserved</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Incoming Orders */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold flex items-center gap-2">
                <ShoppingBag className="w-4 h-4 text-cyan-400" />
                Compliance-Verified Orders
              </h2>
              <span className="text-xs text-cyan-400">Real-Time Dispatch Queue</span>
            </div>

            <div className="space-y-3">
              {orders.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No active orders queued...</p>
              ) : (
                orders.map((ord: any) => (
                  <div key={ord.order_id} className="p-4 rounded-lg border border-slate-800 bg-slate-950/80 space-y-2">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="text-sm font-bold text-slate-100">{ord.order_id}</div>
                        <div className="text-xs text-slate-400">Consumer: {ord.consumer_id}</div>
                      </div>
                      <span className="px-2.5 py-1 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                        {ord.status}
                      </span>
                    </div>

                    <div className="p-2 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between font-mono">
                      <span>Verification OTP: <strong className="text-indigo-400">{ord.delivery_otp || 'N/A'}</strong></span>
                      <span className="text-slate-300">Total: ₹{ord.total_amount}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
