import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  badge?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: string;
  accentColor?: 'blue' | 'rose' | 'amber' | 'emerald';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  badge,
  trend,
  trendValue,
  icon,
  accentColor = 'blue',
}) => {
  const colorMap = {
    blue: {
      border: 'border-primary/30 hover:border-primary/60',
      text: 'text-primary',
      bgGlow: 'bg-primary/5',
      badgeBg: 'bg-primary/10 text-primary border-primary/20',
      shadow: 'hover:shadow-[0_0_20px_rgba(133,173,255,0.15)]',
    },
    rose: {
      border: 'border-error/30 hover:border-error/60',
      text: 'text-error',
      bgGlow: 'bg-error/5',
      badgeBg: 'bg-error/10 text-error border-error/20',
      shadow: 'hover:shadow-[0_0_20px_rgba(255,113,108,0.15)]',
    },
    amber: {
      border: 'border-amber-500/30 hover:border-amber-500/60',
      text: 'text-amber-400',
      bgGlow: 'bg-amber-500/5',
      badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      shadow: 'hover:shadow-[0_0_20px_rgba(245,158,11,0.15)]',
    },
    emerald: {
      border: 'border-emerald-500/30 hover:border-emerald-500/60',
      text: 'text-emerald-400',
      bgGlow: 'bg-emerald-500/5',
      badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      shadow: 'hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]',
    },
  }[accentColor];

  return (
    <div
      className={`relative overflow-hidden rounded-xl border bg-surface-container/90 p-5 shadow-lg backdrop-blur-md transition-all duration-300 ${colorMap.border} ${colorMap.bgGlow} ${colorMap.shadow}`}
    >
      {/* Top subtle highlight border line */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon && (
            <span className={`material-symbols-outlined text-lg ${colorMap.text}`}>
              {icon}
            </span>
          )}
          <h3 className="text-xs font-headline font-bold uppercase tracking-wider text-slate-300">
            {title}
          </h3>
        </div>
        {badge && (
          <span className={`rounded-full px-2 py-0.5 text-[10px] font-mono font-semibold border ${colorMap.badgeBg}`}>
            {badge}
          </span>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between">
        <span className={`font-mono text-2xl lg:text-3xl font-extrabold tracking-tight ${colorMap.text}`}>
          {value}
        </span>
        {trendValue && (
          <div className="flex items-center gap-0.5 text-xs font-mono font-semibold">
            {trend === 'up' && <span className="text-rose-400">▲</span>}
            {trend === 'down' && <span className="text-emerald-400">▼</span>}
            <span className={trend === 'up' ? 'text-rose-400' : trend === 'down' ? 'text-emerald-400' : 'text-slate-400'}>
              {trendValue}
            </span>
          </div>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs font-body text-slate-400 flex items-center gap-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default StatCard;
