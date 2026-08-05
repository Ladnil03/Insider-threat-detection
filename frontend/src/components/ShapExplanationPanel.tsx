import React from 'react';

interface FeatureAttribution {
  feature: string;
  attribution: number;
}

interface ShapExplanationPanelProps {
  features: FeatureAttribution[];
}

export const ShapExplanationPanel: React.FC<ShapExplanationPanelProps> = ({ features }) => {
  return (
    <div className="p-4 bg-slate-800 rounded border border-slate-700">
      <h3 className="text-lg font-semibold text-slate-200 mb-3">SHAP Feature Attribution</h3>
      <ul className="space-y-2">
        {features.map((item) => (
          <li key={item.feature} className="flex justify-between text-sm">
            <span className="text-slate-300">{item.feature}</span>
            <span className="font-mono text-blue-400">{item.attribution.toFixed(4)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
