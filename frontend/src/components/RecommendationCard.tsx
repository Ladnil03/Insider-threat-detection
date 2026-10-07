import React, { useState } from 'react';
import { RecommendationResponse, RiskDriver } from '../types';

interface RecommendationCardProps {
  recommendation: RecommendationResponse | null;
  isLoading?: boolean;
  error?: string | null;
  onTriggerContainment?: (action: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  isLoading = false,
  error = null,
  onTriggerContainment,
}) => {
  const [containmentTriggered, setContainmentTriggered] = useState<boolean>(false);

  if (isLoading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-outline-variant/30 bg-surface-container/60 p-6 text-slate-400">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent mb-2" />
        <span className="text-xs font-mono">Generating Groq / Llama-3-70B Threat Assessment...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-error/40 bg-error/10 p-6 text-center text-slate-400">
        <p className="text-xs text-error font-mono">LLM Recommendation unavailable: {error}</p>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="rounded-xl border border-outline-variant/30 bg-surface-container/60 p-6 text-center text-slate-400">
        <p className="text-xs font-mono">Select an activity to view AI-generated analyst insights and containment recommendations.</p>
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

  const handleActionClick = () => {
    setContainmentTriggered(true);
    onTriggerContainment?.(recommendation.recommended_action);
  };

  return (
    <div className="space-y-5 rounded-xl border border-outline-variant/30 bg-surface-container/90 p-5 lg:p-6 shadow-xl backdrop-blur-md">
      {/* Header with Model & Urgency */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-outline-variant/30 pb-4 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-headline font-bold uppercase tracking-wider text-slate-100">
              Autonomous AI Threat Narrative & Playbook
            </h3>
            <span className="rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-mono font-semibold text-primary border border-primary/30 uppercase">
              Groq Cloud LLM
            </span>
          </div>
          <p className="mt-0.5 text-xs text-on-surface-variant font-body">
            Open-weight reasoning synthesized from PRISM, AIRS, and SHAP features
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-mono font-semibold border ${urgencyStyle.bg} ${urgencyStyle.text} ${urgencyStyle.border}`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
            Urgency: {recommendation.urgency || 'MEDIUM'}
          </span>
          {recommendation.model && (
            <span className="hidden sm:inline-block font-mono text-[10px] text-slate-400 bg-surface-container-high px-2 py-1 rounded border border-outline-variant/30">
              {recommendation.model}
            </span>
          )}
        </div>
      </div>

      {/* Recommended Action Callout Banner */}
      <div className="rounded-xl border border-primary/40 bg-primary/10 p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="rounded-lg bg-primary/20 p-2 text-primary border border-primary/30">
              <span className="material-symbols-outlined text-xl">shield</span>
            </div>
            <div>
              <span className="text-[11px] font-headline font-bold uppercase tracking-wider text-primary block">
                Recommended Containment Action:
              </span>
              <p className="mt-0.5 text-sm font-semibold text-white">
                {recommendation.recommended_action}
              </p>
            </div>
          </div>

          <button
            onClick={handleActionClick}
            disabled={containmentTriggered}
            className={`px-3 py-1.5 rounded-lg text-xs font-headline font-bold uppercase tracking-wider transition active:scale-95 flex items-center gap-1.5 ${
              containmentTriggered
                ? 'bg-emerald-600/30 text-emerald-300 border border-emerald-500/50 cursor-default'
                : 'bg-primary text-black hover:brightness-110 shadow-glow-primary'
            }`}
          >
            <span className="material-symbols-outlined text-sm">
              {containmentTriggered ? 'check_circle' : 'bolt'}
            </span>
            <span>{containmentTriggered ? 'Dispatched' : 'Execute Policy'}</span>
          </button>
        </div>
      </div>

      {/* Incident Narrative Summary */}
      <div>
        <h4 className="text-xs font-headline font-bold uppercase tracking-wider text-slate-300 mb-1.5">
          Incident Narrative & Context
        </h4>
        <p className="rounded-lg border border-outline-variant/30 bg-surface-container-high/60 p-3.5 text-xs text-slate-200 leading-relaxed font-body">
          {recommendation.summary}
        </p>
      </div>

      {/* Risk Drivers Breakdown */}
      {recommendation.risk_drivers && recommendation.risk_drivers.length > 0 && (
        <div>
          <h4 className="text-xs font-headline font-bold uppercase tracking-wider text-slate-300 mb-2">
            Identified Threat Vectors
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {recommendation.risk_drivers.map((d: RiskDriver, idx: number) => (
              <div
                key={idx}
                className="rounded-lg border border-outline-variant/30 bg-surface-container-high/60 p-3 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200 font-headline">{d.feature}</span>
                  <span className="rounded bg-rose-950/80 px-1.5 py-0.5 text-[10px] font-mono font-bold text-rose-300 border border-rose-800/60 uppercase">
                    {d.impact}
                  </span>
                </div>
                <p className="mt-1 text-[11px] text-slate-400 font-body">{d.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecommendationCard;
