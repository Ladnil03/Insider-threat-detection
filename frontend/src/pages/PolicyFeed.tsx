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
          className="font-mono font-bold text-primary hover:underline hover:text-white"
        >
          {v.user_id}
        </button>
      ),
    },
    {
      header: 'Policy Rule',
      render: (v) => (
        <div>
          <div className="font-headline font-semibold text-slate-200">{v.rule_name}</div>
          <div className="font-mono text-[11px] text-tertiary">{v.rule_id}</div>
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
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-mono font-semibold border ${
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
        <span className="font-mono text-xs text-tertiary bg-tertiary/10 px-2 py-0.5 rounded border border-tertiary/30">
          {v.action}
        </span>
      ),
    },
    {
      header: 'Context / Rationale',
      accessor: 'description',
      render: (v) => (
        <span className="text-xs text-slate-300 max-w-sm truncate block font-body" title={v.description || ''}>
          {v.description || '—'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-outline-variant/30 pb-4 gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-headline font-black tracking-wider text-slate-100 uppercase">
            Automated Policy Containment Feed
          </h1>
          <p className="mt-1 text-xs text-on-surface-variant font-body">
            Real-time audit log of rule triggers and automated SOAR remediation actions.
          </p>
        </div>

        <button
          onClick={fetchViolations}
          className="inline-flex items-center gap-2 rounded-xl border border-outline-variant/40 bg-surface-container px-4 py-2 text-xs font-headline font-semibold text-slate-200 hover:bg-surface-container-high hover:text-white transition active:scale-95 shadow-sm"
        >
          <span className="material-symbols-outlined text-sm">sync</span>
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Severity Tabs */}
        <div className="flex flex-wrap items-center gap-1 rounded-xl border border-outline-variant/30 bg-surface-container/80 p-1">
          {severities.map((sev) => (
            <button
              key={sev}
              onClick={() => setSelectedSeverity(sev)}
              className={`rounded-lg px-3 py-1 text-xs font-headline font-bold uppercase transition ${
                selectedSeverity === sev
                  ? 'bg-primary text-black shadow-glow-primary'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
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
            className="w-full sm:w-64 rounded-xl border border-outline-variant/40 bg-surface-container px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-primary focus:outline-none font-mono"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-xl border border-error/50 bg-error/10 p-4 text-xs font-mono text-error">
          <span className="font-semibold">Unable to fetch policy events: </span>
          {error}
        </div>
      )}

      {/* Data Table */}
      <div className="rounded-xl border border-outline-variant/30 bg-surface-container/90 p-5 shadow-xl backdrop-blur-md">
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
    </div>
  );
};

export default PolicyFeed;
