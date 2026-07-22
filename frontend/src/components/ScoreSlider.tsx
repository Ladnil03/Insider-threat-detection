interface ScoreSliderProps {
  value: number;
  onChange: (v: number) => void;
}

function ScoreSlider({ value, onChange }: ScoreSliderProps) {
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm font-medium">Adjust Score:</label>
      <input
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-40"
      />
      <span className="text-sm tabular-nums">{value.toFixed(2)}</span>
    </div>
  );
}

export default ScoreSlider;
