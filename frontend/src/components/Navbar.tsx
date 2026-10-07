import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useHealthCheck } from '../hooks/useHealthCheck';

interface NavbarProps {
  onOpenSimulator?: () => void;
  activeAlertsCount?: { critical: number; high: number };
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenSimulator,
  activeAlertsCount = { critical: 14, high: 42 },
}) => {
  const navigate = useNavigate();
  const health = useHealthCheck(12000);
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('24H');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/users?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-card">
      <div className="flex h-14 w-full items-center justify-between px-4 sm:px-6">
        {/* Left cluster: Branding & Health Status */}
        <div className="flex items-center gap-4 lg:gap-6">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-background border border-border text-primary">
              <span className="material-symbols-outlined text-lg">
                security
              </span>
            </div>
            <div>
              <div className="text-sm font-semibold text-foreground leading-tight">
                OpenIRM Sentinel
              </div>
              <div className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-risk-low" />
                Adaptive AI risk triage
              </div>
            </div>
          </Link>

          {/* Live Telemetry Health Pill */}
          <div className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded-md bg-background border border-border text-xs font-mono">
            <span
              className={`inline-block size-1.5 rounded-full ${
                health.isOnline ? 'bg-risk-low' : 'bg-risk-high'
              }`}
            />
            <span className="text-muted-foreground text-[11px]">
              FastAPI:{' '}
              <span className={health.isOnline ? 'text-foreground font-medium' : 'text-risk-high font-medium'}>
                {health.isOnline ? 'Connected' : 'Offline'}
              </span>
            </span>
            {health.isOnline && health.latencyMs !== null && (
              <>
                <span className="text-border">/</span>
                <span className="text-muted-foreground text-[11px] flex items-center gap-1">
                  <span>{health.latencyMs}ms</span>
                </span>
              </>
            )}
          </div>

          {/* Active Alerts Pill */}
          <Link
            to="/policies"
            className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-background border border-border text-xs font-mono hover:bg-muted/40 transition-colors"
            title="View Policy Feed"
          >
            <span className="size-1.5 rounded-full bg-risk-critical" />
            <span className="text-risk-high font-medium">{activeAlertsCount.critical} Critical</span>
            <span className="text-border">/</span>
            <span className="text-risk-medium font-medium">{activeAlertsCount.high} High</span>
          </Link>
        </div>

        {/* Center: Quick Time Range Selector */}
        <div className="hidden lg:flex items-center gap-1 bg-background p-1 rounded-md border border-border text-xs">
          {['1h', '6h', '24h', '7d'].map((range) => (
            <button
              key={range}
              onClick={() => setSelectedTimeRange(range.toUpperCase())}
              className={`px-2 py-0.5 rounded text-xs transition-colors font-mono ${
                selectedTimeRange === range.toUpperCase()
                  ? 'bg-muted text-foreground font-medium'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
              }`}
            >
              {range}
            </button>
          ))}
          <span className="px-1 text-[11px] font-mono text-muted-foreground">UTC</span>
        </div>

        {/* Right cluster: Search, Simulator trigger, Analyst profile */}
        <div className="flex items-center gap-3">
          {/* Global Quick Search */}
          <form onSubmit={handleSearchSubmit} className="relative hidden md:block">
            <span className="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">
              search
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search user, event, rule..."
              className="w-48 lg:w-56 pl-8 pr-8 py-1 text-xs bg-background text-foreground rounded-md border border-border focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-mono placeholder:text-muted-foreground"
            />
            <kbd className="absolute right-2 top-1/2 -translate-y-1/2 bg-muted text-muted-foreground text-[10px] font-mono px-1 py-0.2 rounded border border-border">
              ↵
            </kbd>
          </form>

          {/* Simulator Action CTA */}
          <button
            onClick={onOpenSimulator}
            className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
            title="Open Telemetry Simulation Sandbox"
          >
            <span className="material-symbols-outlined text-sm">tune</span>
            <span className="hidden sm:inline">Simulate telemetry</span>
          </button>

          {/* SOC Analyst Profile */}
          <div className="flex items-center gap-2 pl-2 sm:pl-3 border-l border-border">
            <div className="w-7 h-7 rounded-md bg-background border border-border flex items-center justify-center font-mono text-xs text-foreground font-medium">
              AV
            </div>
            <div className="hidden xl:block text-left">
              <p className="text-xs font-medium text-foreground leading-tight">Agent Vance</p>
              <p className="text-[10px] text-muted-foreground">Tier 3 forensics</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
