import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useOverviewData } from '../hooks/useOverviewData';
import { RiskBadge } from '../components/RiskBadge';
import { DataTable, Column } from '../components/DataTable';
import { StatCard } from '../components/StatCard';
import { UserSummaryResponse } from '../types';

export const Overview: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading, error, refetch } = useOverviewData();

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-4">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        <p className="text-sm font-medium text-slate-400">
          Aggregating real-time telemetry from PRISM & AIRS engines...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-rose-800/60 bg-rose-950/30 p-8 text-center backdrop-blur">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-900/60 text-rose-300">
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-bold text-rose-200">Failed to Load Dashboard Data</h3>
        <p className="mt-2 text-sm text-slate-300 max-w-md mx-auto">{error}</p>
        <button
          onClick={() => refetch()}
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:bg-rose-500 active:scale-95"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Retry Connection
        </button>
      </div>
    );
  }

  const columns: Column<UserSummaryResponse>[] = [
    {
      header: 'Employee / User ID',
      accessor: 'user_id',
      render: (u) => (
        <div>
          <div className="font-semibold text-slate-100">{u.user_name || u.user_id}</div>
          <div className="text-xs font-mono text-slate-400">{u.user_id}</div>
        </div>
      ),
    },
    {
      header: 'Role & Dept',
      render: (u) => (
        <div>
          <div className="text-slate-200">{u.role || 'Employee'}</div>
          <div className="text-xs text-slate-400">{u.department || 'General'}</div>
        </div>
      ),
    },
    {
      header: 'Ensemble Risk Score',
      accessor: 'latest_score',
      render: (u) => (
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-slate-200">
            {u.latest_score.toFixed(4)}
          </span>
          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-800">
            <div
              className={`h-full ${
                u.latest_score >= 0.8
                  ? 'bg-rose-500'
                  : u.latest_score >= 0.6
                    ? 'bg-orange-500'
                    : u.latest_score >= 0.3
                      ? 'bg-amber-500'
                      : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(u.latest_score * 100, 100)}%` }}
            />
          </div>
        </div>
      ),
    },
    {
      header: 'Risk Level',
      render: (u) => <RiskBadge level={u.risk_level} />,
    },
    {
      header: 'Policy Alerts',
      accessor: 'violation_count',
      render: (u) => (
        <span
          className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
            u.violation_count > 0
              ? 'bg-rose-950/80 text-rose-300 border border-rose-800/60'
              : 'bg-slate-800 text-slate-400'
          }`}
        >
          {u.violation_count} alert{u.violation_count === 1 ? '' : 's'}
        </span>
      ),
    },
    {
      header: 'Actions',
      render: (u) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/users/${u.user_id}`);
          }}
          className="inline-flex items-center gap-1 rounded bg-blue-600/20 px-2.5 py-1 text-xs font-medium text-blue-300 border border-blue-500/30 transition hover:bg-blue-600/40 hover:border-blue-400"
        >
          <span>Drilldown</span>
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Header & Live Status */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-100 sm:text-3xl">
              SOC Threat Operations
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-950/60 px-2 py-0.5 text-[11px] font-semibold text-emerald-400 border border-emerald-800/60">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Live Telemetry
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Real-time insider threat detection powered by PRISM heuristics & AIRS autoencoder reconstruction anomaly scoring.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2 text-xs font-medium text-slate-300 shadow-sm transition hover:bg-slate-700 hover:text-white active:scale-95"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Feed
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Monitored Entities"
          value={data?.totalMonitoredUsers ?? 0}
          subtitle="CERT r4.2 sampled cohort"
          badge="Active"
          accentColor="blue"
        />
        <StatCard
          title="Elevated Threats"
          value={data?.highRiskCount ?? 0}
          subtitle="High & Critical risk users"
          badge={data?.highRiskCount ? 'Urgent' : 'Nominal'}
          accentColor={data?.highRiskCount ? 'rose' : 'emerald'}
        />
        <StatCard
          title="Mean Fleet Risk"
          value={data?.meanFleetRisk.toFixed(3) ?? '0.000'}
          subtitle="Ensemble risk [0.0 - 1.0]"
          badge="Ensemble"
          accentColor="amber"
        />
        <StatCard
          title="Active Policy Alerts"
          value={data?.activeViolationsCount ?? 0}
          subtitle="Automated containment logs"
          badge="Rules"
          accentColor="rose"
        />
      </div>

      {/* Visual Analytics Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Risk Distribution Chart */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                Risk Tier Distribution
              </h2>
              <p className="text-xs text-slate-400">
                User cohort breakdown across calibrated threat thresholds
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              N = {data?.totalMonitoredUsers ?? 0}
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.riskDistribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="level" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.5rem',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                  cursor={{ fill: 'rgba(51, 65, 85, 0.2)' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {data?.riskDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Policy Alerts by Severity Chart */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl backdrop-blur">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                Policy Violations by Severity
              </h2>
              <p className="text-xs text-slate-400">
                Automated containment rule trigger distribution
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Total = {data?.activeViolationsCount ?? 0}
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.violationsBySeverity}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="severity"
                >
                  {data?.violationsBySeverity.map((entry, index) => (
                    <Cell key={`pie-cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.5rem',
                    color: '#f8fafc',
                    fontSize: '12px',
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top 10 High-Risk Users Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100">
              Top Elevated Risk Entities
            </h2>
            <p className="text-xs text-slate-400">
              Highest scoring employees prioritized for SOC review and SHAP attribution analysis
            </p>
          </div>
          <span className="rounded bg-slate-800 px-2.5 py-1 text-xs font-mono text-slate-300 border border-slate-700">
            Top 10 Flagged
          </span>
        </div>

        <DataTable
          columns={columns}
          data={data?.topRiskUsers || []}
          keyExtractor={(u) => u.user_id}
          onRowClick={(u) => navigate(`/users/${u.user_id}`)}
          emptyMessage="No monitored users registered in system."
        />
      </div>
    </div>
  );
};

export default Overview;
