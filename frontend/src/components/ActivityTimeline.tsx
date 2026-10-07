import React from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { UserActivityHistoryItem } from '../types';

interface ActivityTimelineProps {
  history: UserActivityHistoryItem[];
  selectedActivityId?: number | null;
  onSelectActivity: (item: UserActivityHistoryItem) => void;
  isLoading?: boolean;
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  history,
  selectedActivityId,
  onSelectActivity,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="flex h-72 flex-col items-center justify-center rounded-xl border border-outline-variant/30 bg-surface-container/60 p-6 text-slate-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent mb-2" />
        <span className="text-xs font-mono">Loading longitudinal activity telemetry...</span>
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="rounded-xl border border-outline-variant/30 bg-surface-container/60 p-8 text-center text-slate-400">
        <p className="text-sm font-body">No historical activity records found for this user.</p>
      </div>
    );
  }

  const chartData = history.map((item) => ({
    id: item.activity_id,
    date: item.date_day || new Date(item.timestamp).toLocaleDateString(),
    ensemble: Number(item.ensemble_score.toFixed(4)),
    airs: Number(item.airs_score.toFixed(4)),
    prism: Number(item.prism_score.toFixed(4)),
    level: item.risk_level,
    raw: item,
  }));

  return (
    <div className="space-y-4 rounded-xl border border-outline-variant/30 bg-surface-container/90 p-5 lg:p-6 shadow-xl backdrop-blur-md">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-outline-variant/30 pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-headline font-bold uppercase tracking-wider text-slate-100">
              Longitudinal Telemetry & Threat Trajectory
            </h3>
            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-mono font-semibold text-primary border border-primary/20">
              {history.length} Record{history.length === 1 ? '' : 's'}
            </span>
          </div>
          <p className="text-xs text-on-surface-variant font-body">
            Multi-model risk scoring over time (PRISM vs AIRS vs Ensemble). Click any event pill below to inspect.
          </p>
        </div>
      </div>

      {/* Recharts Multi-line Trend */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2638" />
            <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis domain={[0, 1]} stroke="#64748b" fontSize={11} tickLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-outline-variant/40 bg-surface-container-high p-2.5 shadow-xl text-xs font-mono">
                      <div className="font-bold text-slate-100 mb-1">{d.date}</div>
                      <div className="text-primary font-bold">
                        Ensemble Score: <span>{d.ensemble}</span>
                      </div>
                      <div className="text-secondary">
                        AIRS Anomaly: <span>{d.airs}</span>
                      </div>
                      <div className="text-tertiary">
                        PRISM Rule: <span>{d.prism}</span>
                      </div>
                      <div className="text-slate-400 mt-1">Risk Tier: {d.level}</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              verticalAlign="top"
              height={30}
              wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }}
            />
            {/* Risk threshold reference lines */}
            <ReferenceLine
              y={0.8}
              stroke="#ff716c"
              strokeDasharray="3 3"
              label={{ value: 'Critical', fill: '#ff716c', fontSize: 10, position: 'right' }}
            />
            <ReferenceLine
              y={0.6}
              stroke="#f97316"
              strokeDasharray="3 3"
              label={{ value: 'High', fill: '#f97316', fontSize: 10, position: 'right' }}
            />

            <Line
              type="monotone"
              dataKey="ensemble"
              name="Ensemble (Weighted)"
              stroke="#85adff"
              strokeWidth={2.5}
              dot={{ r: 4, strokeWidth: 1, fill: '#3b82f6' }}
              activeDot={{ r: 7 }}
            />
            <Line
              type="monotone"
              dataKey="airs"
              name="AIRS (Autoencoder)"
              stroke="#ac8aff"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="prism"
              name="PRISM (Rules)"
              stroke="#8ce7ff"
              strokeWidth={1.5}
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Clickable Event Pills Strip */}
      <div className="pt-2">
        <span className="text-[11px] font-headline font-bold uppercase tracking-wider text-slate-300 block mb-2">
          Select Activity Date to Inspect:
        </span>
        <div className="flex flex-wrap gap-2">
          {history.map((item) => {
            const isSelected = selectedActivityId === item.activity_id;
            return (
              <button
                key={item.activity_id}
                onClick={() => onSelectActivity(item)}
                className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition active:scale-95 ${
                  isSelected
                    ? 'border-primary bg-primary/20 text-white shadow-glow-primary'
                    : 'border-outline-variant/30 bg-surface-container-high/60 text-slate-300 hover:border-outline-variant hover:bg-surface-container-high'
                }`}
              >
                <span className="font-mono text-[11px]">
                  {item.date_day || new Date(item.timestamp).toLocaleDateString()}
                </span>
                <span
                  className={`font-mono font-bold ${
                    item.ensemble_score >= 0.8
                      ? 'text-error'
                      : item.ensemble_score >= 0.6
                        ? 'text-orange-400'
                        : item.ensemble_score >= 0.3
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                  }`}
                >
                  {item.ensemble_score.toFixed(2)}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ActivityTimeline;
