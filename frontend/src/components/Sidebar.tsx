import React from 'react';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = () => {
  const navItems = [
    {
      to: '/',
      label: 'SOC Dashboard',
      subtitle: 'Fleet Operations',
      icon: 'shield_with_heart',
      end: true,
    },
    {
      to: '/users',
      label: 'User Forensics',
      subtitle: 'Entity Watchlist',
      icon: 'person_search',
      end: false,
    },
    {
      to: '/policies',
      label: 'Policy Feed',
      subtitle: 'Automated Containment',
      icon: 'policy',
      end: false,
    },
    {
      to: '/feedback',
      label: 'Analyst Calibration',
      subtitle: 'Human-in-the-Loop',
      icon: 'tune',
      end: false,
    },
  ];

  return (
    <aside className="w-60 lg:w-64 min-h-[calc(100vh-3.5rem)] p-3 lg:p-4 flex flex-col justify-between bg-card border-r border-border flex-shrink-0">
      {/* Top Section: Cluster status & Navigation items */}
      <div className="space-y-4">
        {/* SOC Cluster State Banner */}
        <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-background border border-border">
          <div className="w-7 h-7 rounded-md bg-muted flex items-center justify-center text-primary">
            <span className="material-symbols-outlined text-base">
              memory
            </span>
          </div>
          <div>
            <div className="text-xs font-medium text-foreground">
              Enclave alpha
            </div>
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-muted-foreground">
              <span className="w-1.5 h-1.5 rounded-full bg-risk-low" />
              Secured / FIPS-140
            </div>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-background text-foreground border-l-2 border-primary'
                    : 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={`material-symbols-outlined text-lg ${
                      isActive ? 'text-primary' : 'text-muted-foreground'
                    }`}
                  >
                    {item.icon}
                  </span>
                  <div className="flex flex-col">
                    <span className="leading-tight">{item.label}</span>
                    <span className="text-[10px] font-mono text-muted-foreground">
                      {item.subtitle}
                    </span>
                  </div>
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom Section: Multi-Model Status Telemetry */}
      <div className="rounded-lg bg-background border border-border p-3 space-y-2 text-[11px] font-mono">
        <div className="text-xs text-muted-foreground border-b border-border pb-1 flex items-center justify-between font-sans">
          <span>AI engines</span>
          <span className="font-mono text-[10px]">v0.1-prod</span>
        </div>
        <div className="space-y-1.5 text-foreground/90">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">PRISM heuristics:</span>
            <span className="text-risk-low font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-risk-low" /> Active
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">AIRS autoencoder:</span>
            <span className="text-foreground font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary" /> PyTorch
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">SHAP explainability:</span>
            <span className="text-foreground font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary" /> Ready
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Threat reasoning:</span>
            <span className="text-foreground font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-risk-low" /> Groq/Ollama
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
