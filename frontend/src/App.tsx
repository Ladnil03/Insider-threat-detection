import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-blue-400">OpenIRM Dashboard</h1>
        <p className="text-slate-400">AI-Driven Insider Risk Management System</p>
      </header>
      <main>
        <div className="p-6 bg-slate-800 rounded-lg border border-slate-700">
          <p className="text-slate-300">System initialization complete. Dashboard views under development.</p>
        </div>
      </main>
    </div>
  );
};

export default App;
