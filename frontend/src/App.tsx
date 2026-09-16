import React from 'react';
import { BrowserRouter, Link, NavLink, Route, Routes } from 'react-router-dom';
import { Overview } from './pages/Overview';
import { UserDrilldown } from './pages/UserDrilldown';
import { PolicyFeed } from './pages/PolicyFeed';
import { FeedbackPanel } from './pages/FeedbackPanel';
import { ErrorBoundary } from './components/ErrorBoundary';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col bg-[#0b0f19] text-slate-100 selection:bg-blue-600 selection:text-white">
        {/* Top SOC Navbar */}
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-900/90 backdrop-blur-md">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
            <div className="flex items-center gap-6">
              <Link to="/" className="flex items-center gap-2.5 group">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                  <span className="font-mono text-base font-black text-white">IR</span>
                </div>
                <div>
                  <span className="text-base font-bold tracking-tight text-white group-hover:text-blue-400 transition-colors">
                    OpenIRM
                  </span>
                  <span className="ml-1.5 rounded bg-blue-950/80 px-1.5 py-0.5 text-[10px] font-semibold text-blue-300 border border-blue-800/60 uppercase">
                    v0.1-MVP
                  </span>
                </div>
              </Link>

              {/* Primary Navigation Links */}
              <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
                <NavLink
                  to="/"
                  end
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md transition-all ${
                      isActive
                        ? 'bg-slate-800 text-blue-400 font-semibold shadow-inner'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`
                  }
                >
                  Overview
                </NavLink>
                <NavLink
                  to="/users"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md transition-all ${
                      isActive
                        ? 'bg-slate-800 text-blue-400 font-semibold shadow-inner'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`
                  }
                >
                  User Drilldown
                </NavLink>
                <NavLink
                  to="/policies"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md transition-all ${
                      isActive
                        ? 'bg-slate-800 text-blue-400 font-semibold shadow-inner'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`
                  }
                >
                  Policy Feed
                </NavLink>
                <NavLink
                  to="/feedback"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md transition-all ${
                      isActive
                        ? 'bg-slate-800 text-blue-400 font-semibold shadow-inner'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`
                  }
                >
                  Analyst Feedback
                </NavLink>
              </nav>
            </div>

            {/* Right Header Status Bar */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/80 px-3 py-1 text-xs">
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-slate-400">FastAPI</span>
                <span className="font-mono text-emerald-400 text-[11px]">8000</span>
              </div>
              <a
                href="https://github.com/Ladnil03/Insider-threat-detection"
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-slate-800 bg-slate-800/50 p-2 text-slate-400 transition hover:bg-slate-700 hover:text-white"
                title="GitHub Repository"
              >
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  />
                </svg>
              </a>
            </div>
          </div>
        </header>

        {/* Main Routed Content */}
        <main className="mx-auto flex-1 w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/users" element={<UserDrilldown />} />
              <Route path="/users/:userId" element={<UserDrilldown />} />
              <Route path="/policies" element={<PolicyFeed />} />
              <Route path="/feedback" element={<FeedbackPanel />} />
            </Routes>
          </ErrorBoundary>
        </main>

        {/* Minimal Footer */}
        <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 text-center text-xs text-slate-400">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>
              OpenIRM © 2026 — Based on Koli et al. (arXiv:2505.03796) + Novel SHAP Explainability Layer
            </span>
            <span className="font-mono text-slate-400 text-[11px]">
              MIT License • Free Tier Architecture
            </span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
