import React from 'react';

interface ScoreSliderProps {
  value: number;
  onChange: (val: number) => void;
}

export const ScoreSlider: React.FC<ScoreSliderProps> = ({ value, onChange }) => {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm text-slate-300 font-medium">Analyst Risk Rating: {value.toFixed(2)}</label>
      <input
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
      />
    </div>
  );
};
