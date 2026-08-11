import React from 'react';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: string;
  variant?: 'indigo' | 'emerald' | 'amber' | 'cyan';
}

export const StatusCard: React.FC<StatusCardProps> = ({ title, value, subtitle, icon, trend, variant = 'indigo' }) => {
  const borderColors = {
    indigo: 'border-indigo-500/20 bg-slate-900/60 hover:border-indigo-500/40',
    emerald: 'border-emerald-500/20 bg-slate-900/60 hover:border-emerald-500/40',
    amber: 'border-amber-500/20 bg-slate-900/60 hover:border-amber-500/40',
    cyan: 'border-cyan-500/20 bg-slate-900/60 hover:border-cyan-500/40',
  };

  return (
    <div className={`p-5 rounded-xl border transition-all duration-200 ${borderColors[variant]}`}>
      <div className="flex justify-between items-start mb-3">
        <span className="text-xs font-medium text-slate-400">{title}</span>
        {icon && <div className="p-2 rounded-lg bg-slate-800/80 text-slate-300">{icon}</div>}
      </div>
      <div className="text-2xl font-bold text-slate-100 mb-1">{value}</div>
      {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      {trend && <span className="inline-block mt-2 text-[11px] font-semibold text-emerald-400">{trend}</span>}
    </div>
  );
};
