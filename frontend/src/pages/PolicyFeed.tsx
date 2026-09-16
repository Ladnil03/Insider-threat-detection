import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPolicyViolations } from '../api/policy';
import { PolicyViolation } from '../types';
import { Column, DataTable } from '../components/DataTable';

export const PolicyFeed: React.FC = () => {
  const navigate = useNavigate();
  const [violations, setViolations] = useState<PolicyViolation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchViolations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getPolicyViolations(150);
      setViolations(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch policy violations.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchViolations();
  }, []);

  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  const filteredViolations = violations.filter((v) => {
    const matchesSeverity =
      selectedSeverity === 'ALL' ||
      (v.severity || '').toUpperCase() === selectedSeverity;

    const matchesSearch =
      searchQuery === '' ||
      v.user_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.rule_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.rule_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (v.action || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (v.description || '').toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSeverity && matchesSearch;
  });

  const columns: Column<PolicyViolation>[] = [
    {
      header: 'Timestamp',
      accessor: 'timestamp',
      render: (v) => (
        <span className="font-mono text-xs text-slate-400">
          {new Date(v.timestamp).toLocaleString()}
        </span>
      ),
    },
    {
      header: 'Employee ID',
      accessor: 'user_id',
      render: (v) => (
        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/users/${v.user_id}`);
          }}
          className="font-mono font-bold text-blue-400 hover:underline hover:text-blue-300"
        >
          {v.user_id}
        </button>
      ),
    },
    {
      header: 'Policy Rule',
      render: (v) => (
        <div>
          <div className="font-semibold text-slate-200">{v.rule_name}</div>
          <div className="font-mono text-[11px] text-slate-400">{v.rule_id}</div>
        </div>
      ),
    },
    {
      header: 'Severity',
      accessor: 'severity',
      render: (v) => {
        const sev = (v.severity || 'HIGH').toUpperCase();
        const colors: Record<string, string> = {
          CRITICAL: 'bg-rose-950/80 text-rose-300 border-rose-800',
          HIGH: 'bg-orange-950/80 text-orange-300 border-orange-800',
          MEDIUM: 'bg-amber-950/80 text-amber-300 border-amber-800',
          LOW: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
        };
        return (
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold border ${
              colors[sev] || colors.HIGH
            }`}
          >
            {sev}
          </span>
        );
      },
    },
    {
      header: 'Automated Containment Action',
      accessor: 'action',
      render: (v) => (
        <span className="font-mono text-xs text-cyan-300 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/50">
          {v.action}
        </span>
      ),
    },
    {
      header: 'Context / Rationale',
      accessor: 'description',
      render: (v) => (
        <span className="text-xs text-slate-300 max-w-sm truncate block" title={v.description || ''}>
          {v.description || '—'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5 gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl">
            Automated Policy Containment Feed
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Real-time audit log of rule triggers and simulated SOAR remediation actions.
          </p>
        </div>

        <button
          onClick={fetchViolations}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-700 hover:text-white transition"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Feed
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Severity Tabs */}
        <div className="flex flex-wrap items-center gap-1 rounded-lg border border-slate-800 bg-slate-900/80 p-1">
          {severities.map((sev) => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              className={`rounded px-3 py-1 text-xs font-semibold transition ${
                selectedSeverity === sev
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>

        {/* Free-text Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Filter by user, rule, action..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:w-64 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-lg border border-rose-800 bg-rose-950/40 p-4 text-xs text-rose-300">
          <span className="font-semibold">Unable to fetch policy events: </span>
          {error}
        </div>
      )}

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={filteredViolations}
        keyExtractor={(v) => v.id}
        isLoading={isLoading}
        onRowClick={(v) => navigate(`/users/${v.user_id}`)}
        emptyMessage={
          searchQuery || selectedSeverity !== 'ALL'
            ? 'No policy violations matching current filters.'
            : 'No automated containment policy violations recorded yet.'
        }
      />
    </div>
  );
};

export default PolicyFeed;
