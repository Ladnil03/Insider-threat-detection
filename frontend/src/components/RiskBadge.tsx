import React from 'react';
import { RiskLevel } from '../types';

interface RiskBadgeProps {
  level: RiskLevel | string;
  score?: number;
  showScore?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  score,
  showScore = false,
}) => {
  const normalizedLevel = (level || 'LOW').toUpperCase();

  const badgeConfig: Record<
    string,
    { bg: string; text: string; border: string; dot: string; label: string }
  > = {
    LOW: {
      bg: 'bg-emerald-950/60',
      text: 'text-emerald-300',
      border: 'border-emerald-700/60',
      dot: 'bg-emerald-400 shadow-emerald-500/50',
      label: 'LOW',
    },
    MODERATE: {
      bg: 'bg-amber-950/60',
      text: 'text-amber-300',
      border: 'border-amber-700/60',
      dot: 'bg-amber-400 shadow-amber-500/50',
      label: 'MODERATE',
    },
    MEDIUM: {
      bg: 'bg-amber-950/60',
      text: 'text-amber-300',
      border: 'border-amber-700/60',
      dot: 'bg-amber-400 shadow-amber-500/50',
      label: 'MODERATE',
    },
    HIGH: {
      bg: 'bg-orange-950/60',
      text: 'text-orange-300',
      border: 'border-orange-700/60',
      dot: 'bg-orange-400 shadow-orange-500/50',
      label: 'HIGH',
    },
    CRITICAL: {
      bg: 'bg-rose-950/60',
      text: 'text-rose-300',
      border: 'border-rose-700/60',
      dot: 'bg-rose-400 shadow-rose-500/50',
      label: 'CRITICAL',
    },
  };

  const current = badgeConfig[normalizedLevel] || badgeConfig.LOW;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-semibold rounded-full border shadow-sm ${current.bg} ${current.text} ${current.border}`}
      data-testid="risk-badge"
    >
      <span className={`w-1.5 h-1.5 rounded-full shadow-sm ${current.dot}`} />
      <span>{current.label}</span>
      {showScore && typeof score === 'number' && (
        <span className="opacity-80 font-mono text-[11px] ml-0.5">
          ({score.toFixed(3)})
        </span>
      )}
    </span>
  );
};

export default RiskBadge;
