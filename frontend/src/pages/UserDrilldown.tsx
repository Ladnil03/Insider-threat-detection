import React from 'react';

export const UserDrilldown: React.FC = () => {
  return (
    <div className="p-4 bg-slate-800 rounded">
      <h2 className="text-xl font-bold">User Risk Drill-down</h2>
      <p className="text-slate-400">Detailed metric breakdown and SHAP attribution for selected user.</p>
    </div>
  );
};
