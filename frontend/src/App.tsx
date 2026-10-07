import React, { useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Overview } from './pages/Overview';
import { UserDrilldown } from './pages/UserDrilldown';
import { PolicyFeed } from './pages/PolicyFeed';
import { FeedbackPanel } from './pages/FeedbackPanel';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { ScoringSimulatorModal } from './components/ScoringSimulatorModal';
import { TooltipProvider } from './components/ui/tooltip';
import { Toaster } from './components/ui/sonner';

export const App: React.FC = () => {
  const [isSimulatorOpen, setIsSimulatorOpen] = useState<boolean>(false);

  return (
    <BrowserRouter>
      <TooltipProvider>
        <div className="flex min-h-screen flex-col bg-background text-foreground font-body soc-grid-bg selection:bg-primary selection:text-primary-foreground">
        {/* Top SOC Command Bar */}
        <Navbar onOpenSimulator={() => setIsSimulatorOpen(true)} />

        {/* Tactical Mission Layout Shell: Sidebar + Main Content */}
        <div className="flex flex-1 w-full max-w-[1920px] mx-auto overflow-hidden">
          {/* Collapsible Mission Rail */}
          <Sidebar />

          {/* Dynamic Routed Content */}
          <main className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 overflow-y-auto">
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
        </div>

        {/* Global Telemetry Simulator Modal */}
        <ScoringSimulatorModal
          isOpen={isSimulatorOpen}
          onClose={() => setIsSimulatorOpen(false)}
        />

        {/* SOC Terminal Footer */}
        <footer className="border-t border-border bg-card/60 py-3 text-xs text-muted-foreground font-mono">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-risk-low" />
              <span>OpenIRM Sentinel © 2026 — AI insider risk management</span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-[11px] text-muted-foreground">
              <span>PRISM rule engine</span>
              <span>AIRS autoencoder</span>
              <span>Game-theoretic SHAP XAI</span>
              <span>Groq / Ollama</span>
            </div>
          </div>
        </footer>

        <Toaster theme="dark" position="bottom-right" richColors />
        </div>
      </TooltipProvider>
    </BrowserRouter>
  );
};

export default App;
