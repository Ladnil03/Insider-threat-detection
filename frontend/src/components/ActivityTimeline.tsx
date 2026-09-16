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
      <div className="flex h-72 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent mb-2" />
        <span className="text-xs">Loading longitudinal activity telemetry...</span>
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-8 text-center text-slate-400">
        <p className="text-sm">No historical activity records found for this user.</p>
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
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
            Longitudinal Threat Trajectory
          </h3>
          <p className="text-xs text-slate-400">
            Multi-model scoring over time (Click any point or item below to inspect)
          </p>
        </div>
        <span className="text-xs font-mono text-slate-400">
          {history.length} Event{history.length === 1 ? '' : 's'} Recorded
        </span>
      </div>

      {/* Recharts Multi-line Trend */}
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis domain={[0, 1]} stroke="#64748b" fontSize={11} tickLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-slate-700 bg-slate-900 p-2.5 shadow-xl text-xs">
                      <div className="font-bold text-slate-100 mb-1">{d.date}</div>
                      <div className="text-blue-400">
                        Ensemble Score: <span className="font-mono font-bold">{d.ensemble}</span>
                      </div>
                      <div className="text-amber-400">
                        AIRS Anomaly: <span className="font-mono">{d.airs}</span>
                      </div>
                      <div className="text-slate-400">
                        PRISM Rule: <span className="font-mono">{d.prism}</span>
                      </div>
                      <div className="text-slate-400 mt-1">Tier: {d.level}</div>
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
            <ReferenceLine y={0.8} stroke="#f43f5e" strokeDasharray="3 3" label={{ value: 'Critical', fill: '#f43f5e', fontSize: 10, position: 'right' }} />
            <ReferenceLine y={0.6} stroke="#f97316" strokeDasharray="3 3" label={{ value: 'High', fill: '#f97316', fontSize: 10, position: 'right' }} />

            <Line
              type="monotone"
              dataKey="ensemble"
              name="Ensemble (Weighted)"
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={{ r: 4, strokeWidth: 1, fill: '#1d4ed8' }}
              activeDot={{ r: 7 }}
            />
            <Line
              type="monotone"
              dataKey="airs"
              name="AIRS (Autoencoder)"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="prism"
              name="PRISM (Rules)"
              stroke="#64748b"
              strokeWidth={1.5}
              dot={{ r: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Clickable Event Pills Strip */}
      <div className="pt-2">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
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
                    ? 'border-blue-500 bg-blue-600/30 text-white shadow-md shadow-blue-500/20'
                    : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800/60'
                }`}
              >
                <span className="font-mono text-[11px]">
                  {item.date_day || new Date(item.timestamp).toLocaleDateString()}
                </span>
                <span
                  className={`font-mono font-bold ${
                    item.ensemble_score >= 0.8
                      ? 'text-rose-400'
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
