import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  badge?: string;
  trend?: 'up' | 'down' | 'neutral';
  accentColor?: 'blue' | 'rose' | 'amber' | 'emerald';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  badge,
  accentColor = 'blue',
}) => {
  const borderStyles = {
    blue: 'border-blue-500/30 hover:border-blue-500/60 shadow-blue-500/5',
    rose: 'border-rose-500/30 hover:border-rose-500/60 shadow-rose-500/5',
    amber: 'border-amber-500/30 hover:border-amber-500/60 shadow-amber-500/5',
    emerald: 'border-emerald-500/30 hover:border-emerald-500/60 shadow-emerald-500/5',
  };

  const accentText = {
    blue: 'text-blue-400',
    rose: 'text-rose-400',
    amber: 'text-amber-400',
    emerald: 'text-emerald-400',
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl border bg-slate-900/80 p-5 shadow-lg backdrop-blur transition-all duration-200 ${borderStyles[accentColor]}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </h3>
        {badge && (
          <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-300">
            {badge}
          </span>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className={`text-2xl font-bold tracking-tight ${accentText[accentColor]}`}>
          {value}
        </span>
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
      )}
    </div>
  );
};

export default StatCard;
