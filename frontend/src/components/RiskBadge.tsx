import React from 'react';

interface RiskBadgeProps {
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level }) => {
  const badgeStyles: Record<string, string> = {
    LOW: 'bg-emerald-900/50 text-emerald-300 border-emerald-700',
    MEDIUM: 'bg-amber-900/50 text-amber-300 border-amber-700',
    HIGH: 'bg-orange-900/50 text-orange-300 border-orange-700',
    CRITICAL: 'bg-rose-900/50 text-rose-300 border-rose-700',
  };

  return (
    <span
      className={`px-2.5 py-1 text-xs font-semibold rounded border ${badgeStyles[level] || badgeStyles.LOW}`}
    >
      {level}
    </span>
  );
};
