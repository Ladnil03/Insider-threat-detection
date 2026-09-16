import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { FeatureAttribution } from '../types';

interface ShapExplanationPanelProps {
  features: FeatureAttribution[];
  baseValue?: number;
  reconstructionError?: number;
  saiScore?: number;
  summary?: string;
  topRiskDrivers?: Array<Record<string, unknown>>;
  isLoading?: boolean;
}

export const ShapExplanationPanel: React.FC<ShapExplanationPanelProps> = ({
  features,
  baseValue = 0.05,
  reconstructionError,
  saiScore,
  summary,
  topRiskDrivers = [],
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent mb-2" />
        <span className="text-xs">Computing game-theoretic SHAP attributions...</span>
      </div>
    );
  }

  if (!features || features.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-center text-slate-400">
        <p className="text-xs">Select an activity event from the timeline to view its SHAP explanation breakdown.</p>
      </div>
    );
  }

  // Sort by absolute attribution descending, take top 10 for clean visualization
  const sortedFeatures = [...features]
    .sort((a, b) => Math.abs(b.attribution) - Math.abs(a.attribution))
    .slice(0, 10);

  const chartData = sortedFeatures.map((f) => ({
    name: f.feature.length > 28 ? `${f.feature.slice(0, 26)}...` : f.feature,
    fullName: f.feature,
    attribution: Number(f.attribution.toFixed(4)),
    value: Number(f.value.toFixed(2)),
    percentage: Number(f.percentage.toFixed(1)),
    direction: f.direction || (f.attribution >= 0 ? 'increased' : 'decreased'),
  }));

  return (
    <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-4 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              SHAP Anomaly Explainability (XAI)
            </h3>
            <span className="rounded bg-indigo-950/80 px-2 py-0.5 text-[10px] font-semibold text-indigo-300 border border-indigo-800/60 uppercase">
              Novel Extension
            </span>
          </div>
          <p className="mt-0.5 text-xs text-slate-400">
            Shapley attribution of continuous autoencoder reconstruction error
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="rounded bg-slate-800/80 px-2.5 py-1 border border-slate-700/60">
            <span className="text-slate-400">Base: </span>
            <span className="text-slate-200 font-semibold">{baseValue.toFixed(4)}</span>
          </div>
          {typeof saiScore === 'number' && (
            <div className="rounded bg-slate-800/80 px-2.5 py-1 border border-slate-700/60">
              <span className="text-slate-400">SAI: </span>
              <span className="text-blue-400 font-semibold">{saiScore.toFixed(4)}</span>
            </div>
          )}
          {typeof reconstructionError === 'number' && (
            <div className="rounded bg-slate-800/80 px-2.5 py-1 border border-slate-700/60">
              <span className="text-slate-400">MSE: </span>
              <span className="text-amber-400 font-semibold">{reconstructionError.toFixed(4)}</span>
            </div>
          )}
        </div>
      </div>

      {/* Human Readable Summary */}
      {summary && (
        <div className="rounded-lg border border-indigo-900/40 bg-indigo-950/20 p-3 text-xs text-indigo-200 leading-relaxed">
          <span className="font-semibold text-indigo-100 uppercase tracking-wider text-[10px] block mb-0.5">
            Key Attribution Insight:
          </span>
          {summary}
        </div>
      )}

      {/* SHAP Waterfall / Bar Attribution Chart */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-300">Top Feature Contributions to Anomaly Score</span>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-rose-500" />
              <span className="text-slate-400">Risk Elevator (+)</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span className="text-slate-400">Baseline Suppressor (-)</span>
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 130, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" stroke="#64748b" fontSize={11} />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#94a3b8"
                fontSize={11}
                tickLine={false}
                width={125}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="rounded-lg border border-slate-700 bg-slate-900 p-2.5 shadow-xl text-xs">
                        <div className="font-bold text-slate-100">{d.fullName}</div>
                        <div className="mt-1 text-slate-300">
                          Attribution (SHAP):{' '}
                          <span
                            className={`font-mono font-bold ${
                              d.attribution >= 0 ? 'text-rose-400' : 'text-emerald-400'
                            }`}
                          >
                            {d.attribution >= 0 ? `+${d.attribution}` : d.attribution}
                          </span>
                        </div>
                        <div className="text-slate-400">Observed Value: {d.value}</div>
                        <div className="text-slate-400">Contribution: {d.percentage}%</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <ReferenceLine x={0} stroke="#475569" />
              <Bar dataKey="attribution" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.attribution >= 0 ? '#f43f5e' : '#10b981'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Risk Drivers Table */}
      {topRiskDrivers && topRiskDrivers.length > 0 && (
        <div className="pt-2 border-t border-slate-800">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Top Flagged Risk Drivers
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {topRiskDrivers.map((driver, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-slate-800 bg-slate-950/60 p-2.5 text-xs"
              >
                <div className="font-semibold text-slate-200 truncate">
                  {String(driver.feature || `Driver #${idx + 1}`)}
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">Impact:</span>
                  <span className="font-mono font-bold text-rose-400">
                    {driver.impact ? String(driver.impact) : `${driver.percentage || 0}%`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ShapExplanationPanel;
