import React from 'react';

interface RiskGaugeProps {
  score: number; // 0.0 to 1.0
  title?: string;
  size?: 'sm' | 'md' | 'lg';
  trendText?: string;
  showPercent?: boolean;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  score,
  title = 'Fleet Risk Index',
  size = 'md',
  trendText,
  showPercent = false,
}) => {
  const clampedScore = Math.max(0, Math.min(1, score));
  const percent = Math.round(clampedScore * 100);

  // Determine risk category & colors
  let tierLabel = 'NOMINAL';
  let strokeColor = '#10b981'; // emerald
  let glowColor = 'rgba(16, 185, 129, 0.25)';
  let bgBadge = 'bg-emerald-950/60 border-emerald-800/60 text-emerald-400';

  if (clampedScore >= 0.8) {
    tierLabel = 'CRITICAL RISK';
    strokeColor = '#ff716c';
    glowColor = 'rgba(255, 113, 108, 0.35)';
    bgBadge = 'bg-rose-950/70 border-rose-800/80 text-rose-300';
  } else if (clampedScore >= 0.6) {
    tierLabel = 'HIGH THREAT';
    strokeColor = '#f97316';
    glowColor = 'rgba(249, 115, 22, 0.3)';
    bgBadge = 'bg-orange-950/70 border-orange-800/80 text-orange-300';
  } else if (clampedScore >= 0.3) {
    tierLabel = 'ELEVATED';
    strokeColor = '#f59e0b';
    glowColor = 'rgba(245, 158, 11, 0.3)';
    bgBadge = 'bg-amber-950/70 border-amber-800/80 text-amber-300';
  }

  // Dimensions
  const config = {
    sm: { radius: 36, stroke: 6, width: 90, height: 90, textSize: 'text-lg', labelSize: 'text-[9px]' },
    md: { radius: 52, stroke: 8, width: 130, height: 130, textSize: 'text-2xl', labelSize: 'text-[10px]' },
    lg: { radius: 70, stroke: 10, width: 170, height: 170, textSize: 'text-3xl', labelSize: 'text-xs' },
  }[size];

  const circumference = 2 * Math.PI * config.radius;
  // Use a 270 degree arc for gauge look
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - arcLength * clampedScore;

  return (
    <div className="flex flex-col items-center justify-center p-3 text-center">
      <div className="relative flex items-center justify-center" style={{ width: config.width, height: config.height }}>
        <svg
          width={config.width}
          height={config.height}
          viewBox={`0 0 ${config.width} ${config.height}`}
          className="rotate-[135deg] transform overflow-visible"
        >
          {/* Background track */}
          <circle
            cx={config.width / 2}
            cy={config.height / 2}
            r={config.radius}
            fill="transparent"
            stroke="#1b2234"
            strokeWidth={config.stroke}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeLinecap="round"
          />
          {/* Active progress track */}
          <circle
            cx={config.width / 2}
            cy={config.height / 2}
            r={config.radius}
            fill="transparent"
            stroke={strokeColor}
            strokeWidth={config.stroke}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{
              filter: `drop-shadow(0px 0px 6px ${glowColor})`,
              transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          />
        </svg>

        {/* Center score readout */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className={`font-mono font-black tracking-tight text-white ${config.textSize}`}>
            {showPercent ? `${percent}%` : clampedScore.toFixed(3)}
          </span>
          <span className={`font-mono uppercase font-bold tracking-widest ${config.labelSize} text-slate-400 mt-0.5`}>
            {showPercent ? 'Ensemble' : '/ 1.000'}
          </span>
        </div>
      </div>

      {title && (
        <div className="mt-2 text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-headline block">
            {title}
          </span>
          <div className="mt-1 flex items-center justify-center gap-1.5">
            <span className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider border ${bgBadge}`}>
              {tierLabel}
            </span>
            {trendText && (
              <span className="text-[10px] font-mono text-slate-400">
                {trendText}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
