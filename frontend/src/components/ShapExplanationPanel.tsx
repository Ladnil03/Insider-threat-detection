import type { ShapExplanation } from "../types";

interface ShapPanelProps {
  features: ShapExplanation[];
}

function ShapExplanationPanel({ features }: ShapPanelProps) {
  return (
    <div className="rounded border p-4">
      <h3 className="mb-2 text-lg font-semibold">Feature Contributions</h3>
      {features.length === 0 && <p className="text-gray-400">No SHAP data.</p>}
      <ul>
        {features.map((f) => (
          <li key={f.feature} className="flex justify-between py-1">
            <span>{f.feature}</span>
            <span className={f.contribution > 0 ? "text-red-600" : "text-green-600"}>
              {f.contribution.toFixed(4)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ShapExplanationPanel;
