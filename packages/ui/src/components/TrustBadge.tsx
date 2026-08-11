import React from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface TrustBadgeProps {
  level: string;
  verified?: boolean;
}

export const TrustBadge: React.FC<TrustBadgeProps> = ({ level, verified = true }) => {
  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${
      verified 
        ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' 
        : 'bg-amber-500/10 text-amber-300 border-amber-500/30'
    }`}>
      {verified ? <ShieldCheck className="w-3.5 h-3.5" /> : <ShieldAlert className="w-3.5 h-3.5" />}
      <span>{level}</span>
      {verified && <CheckCircle2 className="w-3 h-3 text-emerald-400 ml-0.5" />}
    </div>
  );
};
