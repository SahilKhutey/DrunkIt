'use client';

import React, { useState, useEffect } from 'react';
import { Header, TrustBadge } from '@faccp/ui';
import { ShieldCheck, ShoppingCart, Lock, Sparkles, CheckCircle2, AlertCircle, MapPin } from 'lucide-react';

export default function ConsumerStorefront() {
  const [jurisdiction, setJurisdiction] = useState('IN-KA');
  const [storeId, setStoreId] = useState('STR-BANGALORE-01');
  const [products, setProducts] = useState<any[]>([]);
  const [cart, setCart] = useState<{ [sku: string]: number }>({});
  const [ageEligible, setAgeEligible] = useState(true);
  const [verificationProof, setVerificationProof] = useState<any>(null);
  const [orderResult, setOrderResult] = useState<any>(null);
  const [placingOrder, setPlacingOrder] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await fetch('http://localhost:8004/api/v1/catalog/products');
      if (res.ok) {
        setProducts(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleVerifyAge = async () => {
    try {
      const res = await fetch('http://localhost:8001/api/v1/trust/verify-age', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          consumer_id: 'C-1001',
          dob_year: 1995,
          jurisdiction: jurisdiction
        })
      });
      if (res.ok) {
        const proof = await res.json();
        setVerificationProof(proof);
        setAgeEligible(proof.age_eligible);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const addToCart = (sku: string) => {
    setCart(prev => ({ ...prev, [sku]: (prev[sku] || 0) + 1 }));
  };

  const removeFromCart = (sku: string) => {
    setCart(prev => {
      const updated = { ...prev };
      if (updated[sku] > 1) {
        updated[sku] -= 1;
      } else {
        delete updated[sku];
      }
      return updated;
    });
  };

  const getCartItems = () => {
    return Object.entries(cart).map(([sku, qty]) => {
      const p = products.find(prod => prod.sku === sku);
      return {
        sku,
        product_name: p?.name || sku,
        category: p?.category || 'SPIRITS',
        abv: p?.abv || 40.0,
        volume_ml: p?.volume_ml || 750,
        quantity: qty,
        unit_price: p?.base_price || 1000
      };
    });
  };

  const calculateSubtotal = () => {
    return getCartItems().reduce((acc, item) => acc + item.unit_price * item.quantity, 0);
  };

  const handleCheckout = async () => {
    setPlacingOrder(true);
    setOrderResult(null);

    const items = getCartItems();
    try {
      const res = await fetch('http://localhost:8006/api/v1/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          consumer_id: 'C-1001',
          consumer_age_eligible: ageEligible,
          store_id: storeId,
          jurisdiction: jurisdiction,
          items: items
        })
      });
      if (res.ok) {
        const orderData = await res.json();
        setOrderResult(orderData);
        if (orderData.status === 'CONFIRMED') {
          setCart({});
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setPlacingOrder(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Header
        domainName="CONSUMER STOREFRONT"
        title="Federated Premium Spirits & Wine Storefront"
        subtitle="Zero-Knowledge Privacy Age Verification & Compliance-Protected Delivery"
        jurisdiction={jurisdiction}
      />

      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {/* Zero-Knowledge Age Verification Banner */}
        <div className="p-5 rounded-xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-950 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-start gap-3">
            <div className="p-3 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-100">Zero-Knowledge Privacy Age Verification</h2>
                <TrustBadge level={ageEligible ? "C3_AGE_ELIGIBLE" : "C1_UNVERIFIED"} verified={ageEligible} />
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Your actual government identity document remains in your isolated Identity Vault. The storefront receives only an encrypted <code className="text-indigo-300">age_eligible = true</code> claim.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleVerifyAge}
              className="px-4 py-2 rounded-lg text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-lg shadow-indigo-600/20 flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              {verificationProof ? "Re-Verify ZK Proof" : "Verify Age (ZK-Claim)"}
            </button>
          </div>
        </div>

        {/* Location & Store Selector */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/40 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <MapPin className="w-4 h-4 text-emerald-400" />
            <span>Fulfilling Store: <strong className="text-indigo-300">{storeId}</strong></span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => { setJurisdiction('IN-KA'); setStoreId('STR-BANGALORE-01'); }}
              className={`px-3 py-1 rounded text-xs font-semibold ${jurisdiction === 'IN-KA' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'}`}
            >
              Bengaluru (IN-KA)
            </button>
            <button
              onClick={() => { setJurisdiction('IN-MH'); setStoreId('STR-MUMBAI-01'); }}
              className={`px-3 py-1 rounded text-xs font-semibold ${jurisdiction === 'IN-MH' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'}`}
            >
              Mumbai (IN-MH)
            </button>
          </div>
        </div>

        {/* Catalog & Cart Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Catalog Grid */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-base font-bold flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              Licensed Product Catalog ({products.length} SKUs)
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {products.map(p => (
                <div key={p.sku} className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden flex flex-col justify-between hover:border-slate-700 transition-all">
                  <div className="p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-indigo-400 border border-slate-700">
                        {p.category} | ABV {p.abv}%
                      </span>
                      <span className="text-xs text-slate-400">{p.volume_ml}ml</span>
                    </div>

                    <div>
                      <h3 className="text-sm font-bold text-slate-100">{p.name}</h3>
                      <p className="text-xs text-slate-400">{p.brand} • {p.country_of_origin}</p>
                    </div>
                  </div>

                  <div className="p-4 pt-0 flex justify-between items-center border-t border-slate-800/60 mt-auto">
                    <div className="text-base font-bold text-emerald-400">₹{p.base_price}</div>
                    <button
                      onClick={() => addToCart(p.sku)}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600/90 hover:bg-indigo-500 text-white transition-all flex items-center gap-1.5"
                    >
                      <ShoppingCart className="w-3.5 h-3.5" /> Add to Cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cart & Compliance Checkout Box */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 space-y-4 h-fit">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800">
              <h2 className="text-base font-bold flex items-center gap-2">
                <ShoppingCart className="w-4 h-4 text-emerald-400" />
                Compliance Cart
              </h2>
              <span className="text-xs text-slate-400">{getCartItems().length} Items</span>
            </div>

            {getCartItems().length === 0 ? (
              <p className="text-xs text-slate-400 py-6 text-center">Your shopping cart is empty</p>
            ) : (
              <div className="space-y-3">
                {getCartItems().map(item => (
                  <div key={item.sku} className="flex justify-between items-center text-xs p-2.5 rounded bg-slate-950 border border-slate-800">
                    <div>
                      <div className="font-semibold text-slate-200">{item.product_name}</div>
                      <div className="text-slate-400">Qty: {item.quantity} × ₹{item.unit_price}</div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button onClick={() => removeFromCart(item.sku)} className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300">-</button>
                      <button onClick={() => addToCart(item.sku)} className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300">+</button>
                    </div>
                  </div>
                ))}

                <div className="pt-3 border-t border-slate-800 space-y-1.5 text-xs text-slate-300">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span>₹{calculateSubtotal()}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Est. Tax (18%)</span>
                    <span>₹{round(calculateSubtotal() * 0.18)}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Licensed Delivery Fee</span>
                    <span>₹150</span>
                  </div>
                  <div className="flex justify-between text-sm font-bold text-emerald-400 pt-2 border-t border-slate-800">
                    <span>Total Amount</span>
                    <span>₹{calculateSubtotal() + round(calculateSubtotal() * 0.18) + 150 + 50}</span>
                  </div>
                </div>

                <button
                  onClick={handleCheckout}
                  disabled={placingOrder}
                  className="w-full py-2.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 mt-4"
                >
                  <Lock className="w-3.5 h-3.5" />
                  {placingOrder ? "Evaluating Compliance..." : "Place Compliance-Checked Order"}
                </button>
              </div>
            )}

            {/* Order Result Banner */}
            {orderResult && (
              <div className={`p-4 rounded-xl border text-xs space-y-2 mt-4 ${
                orderResult.status === 'CONFIRMED'
                  ? 'border-emerald-500/30 bg-emerald-950/40 text-emerald-300'
                  : 'border-rose-500/30 bg-rose-950/40 text-rose-300'
              }`}>
                <div className="flex items-center gap-2 font-bold">
                  {orderResult.status === 'CONFIRMED' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-400" />
                  )}
                  <span>Order Status: {orderResult.status}</span>
                </div>

                <div>Order ID: <strong className="font-mono">{orderResult.order_id}</strong></div>

                {orderResult.delivery_otp && (
                  <div className="p-2 rounded bg-slate-950/80 border border-emerald-500/30 font-mono text-emerald-400 font-bold text-center">
                    Delivery Verification OTP: {orderResult.delivery_otp}
                  </div>
                )}

                {orderResult.reasons && orderResult.reasons.length > 0 && (
                  <div className="text-[11px] opacity-90">
                    {orderResult.reasons.map((r: string, idx: number) => (
                      <div key={idx}>• {r}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function round(val: number) {
  return Math.round(val * 100) / 100;
}
