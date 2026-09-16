import React from 'react';

interface ScoreSliderProps {
  value: number;
  onChange: (val: number) => void;
  disabled?: boolean;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
}

export const ScoreSlider: React.FC<ScoreSliderProps> = ({
  value,
  onChange,
  disabled = false,
  min = 0,
  max = 1,
  step = 0.01,
  label = 'Calibrated Analyst Risk Score',
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 0.8) return 'text-rose-400';
    if (val >= 0.6) return 'text-orange-400';
    if (val >= 0.3) return 'text-amber-400';
    return 'text-emerald-400';
  };

  const getScoreLevel = (val: number) => {
    if (val >= 0.8) return 'CRITICAL';
    if (val >= 0.6) return 'HIGH';
    if (val >= 0.3) return 'MODERATE';
    return 'LOW';
  };

  const presets = [
    { label: 'Low (0.15)', value: 0.15 },
    { label: 'Moderate (0.45)', value: 0.45 },
    { label: 'High (0.70)', value: 0.70 },
    { label: 'Critical (0.90)', value: 0.90 },
  ];

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-center justify-between">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {label}
          </label>
          <p className="text-[11px] text-slate-400">
            Current Tier: <span className="font-semibold text-slate-300">{getScoreLevel(value)}</span>
          </p>
        </div>
        <div className="text-right">
          <span className={`font-mono text-2xl font-black ${getScoreColor(value)}`}>
            {value.toFixed(2)}
          </span>
          <span className="text-[11px] text-slate-400 ml-1">/ 1.00</span>
        </div>
      </div>

      {/* Interactive Range Input */}
      <div className="relative py-1">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label={label}
        />
        <div className="flex justify-between text-[10px] font-mono text-slate-400 mt-1">
          <span>0.00 (Benign)</span>
          <span>0.30</span>
          <span>0.60</span>
          <span>0.80</span>
          <span>1.00 (Critical)</span>
        </div>
      </div>

      {/* Quick Preset Buttons */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        <span className="text-[11px] text-slate-400 mr-1">Presets:</span>
        {presets.map((preset) => (
          <button
            key={preset.label}
            type="button"
            disabled={disabled}
            onClick={() => onChange(preset.value)}
            className="rounded border border-slate-700/80 bg-slate-800/80 px-2 py-0.5 text-[10px] font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white disabled:opacity-50"
          >
            {preset.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ScoreSlider;
