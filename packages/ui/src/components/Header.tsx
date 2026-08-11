import React from 'react';
import { ShieldCheck, Lock, Activity } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle: string;
  domainName: 'ADMINISTRATIVE BODY' | 'RETAILER SYSTEM' | 'CONSUMER STOREFRONT';
  jurisdiction?: string;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, domainName, jurisdiction = 'IN-KA' }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur px-6 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {domainName}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" /> Jurisdiction: {jurisdiction}
          </span>
        </div>
        <h1 className="text-xl font-bold text-slate-100">{title}</h1>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <Lock className="w-3.5 h-3.5 text-indigo-400" />
          <span>Trust Fabric Active</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/50 border border-emerald-800/40 px-3 py-1.5 rounded-lg font-mono">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>ONLINE</span>
        </div>
      </div>
    </header>
  );
};
