import React from 'react';
import { RecommendationResponse, RiskDriver } from '../types';

interface RecommendationCardProps {
  recommendation: RecommendationResponse | null;
  isLoading?: boolean;
  error?: string | null;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  isLoading = false,
  error = null,
}) => {
  if (isLoading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-slate-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent mb-2" />
        <span className="text-xs">Generating Groq LLM Threat Intelligence Assessment...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-rose-800/60 bg-rose-950/20 p-6 text-center text-slate-400">
        <p className="text-xs text-rose-300">LLM Recommendation unavailable: {error}</p>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-center text-slate-400">
        <p className="text-xs">Select an activity to view AI-generated analyst insights and containment recommendations.</p>
      </div>
    );
  }

  const urgencyColors: Record<string, { bg: string; text: string; border: string }> = {
    CRITICAL: { bg: 'bg-rose-950/80', text: 'text-rose-300', border: 'border-rose-800/80' },
    HIGH: { bg: 'bg-orange-950/80', text: 'text-orange-300', border: 'border-orange-800/80' },
    MEDIUM: { bg: 'bg-amber-950/80', text: 'text-amber-300', border: 'border-amber-800/80' },
    LOW: { bg: 'bg-emerald-950/80', text: 'text-emerald-300', border: 'border-emerald-800/80' },
  };

  const urgencyKey = (recommendation.urgency || 'MEDIUM').toUpperCase();
  const urgencyStyle = urgencyColors[urgencyKey] || urgencyColors.MEDIUM;

  return (
    <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur">
      {/* Header with Model & Urgency */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800/80 pb-4 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              AI Threat Intelligence & Action Guidance
            </h3>
            <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-[10px] font-semibold text-cyan-300 border border-cyan-800/60 uppercase">
              Groq Cloud LLM
            </span>
          </div>
          <p className="mt-0.5 text-xs text-slate-400">
            Open-weight reasoning synthesized from PRISM, AIRS, and SHAP features
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold border ${urgencyStyle.bg} ${urgencyStyle.text} ${urgencyStyle.border}`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />
            Urgency: {recommendation.urgency || 'MEDIUM'}
          </span>
          {recommendation.model && (
            <span className="hidden sm:inline-block font-mono text-[10px] text-slate-400 bg-slate-800/60 px-2 py-1 rounded border border-slate-700/60">
              {recommendation.model}
            </span>
          )}
        </div>
      </div>

      {/* Recommended Action Callout Banner */}
      <div className="rounded-xl border border-blue-500/30 bg-blue-950/30 p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-blue-600/20 p-2 text-blue-400 border border-blue-500/30">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-300">
              Recommended Containment Action:
            </span>
            <p className="mt-0.5 text-sm font-semibold text-white">
              {recommendation.recommended_action}
            </p>
          </div>
        </div>
      </div>

      {/* Incident Narrative Summary */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
          Incident Narrative & Context
        </h4>
        <p className="rounded-lg border border-slate-800 bg-slate-950/60 p-3.5 text-xs text-slate-200 leading-relaxed">
          {recommendation.summary}
        </p>
      </div>

      {/* Risk Drivers Breakdown */}
      {recommendation.risk_drivers && recommendation.risk_drivers.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Identified Threat Vectors
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {recommendation.risk_drivers.map((d: RiskDriver, idx: number) => (
              <div
                key={idx}
                className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">{d.feature}</span>
                  <span className="rounded bg-rose-950/80 px-1.5 py-0.5 text-[10px] font-bold text-rose-300 border border-rose-800/60 uppercase">
                    {d.impact}
                  </span>
                </div>
                <p className="mt-1 text-[11px] text-slate-400">{d.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;
