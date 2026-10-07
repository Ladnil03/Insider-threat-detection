import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { scoreActivity } from '../api/scoring';
import { ScoreResponse } from '../types';
import { RiskBadge } from './RiskBadge';

interface ScoringSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScoreSuccess?: (res: ScoreResponse) => void;
}

interface ScenarioPreset {
  name: string;
  description: string;
  userId: string;
  userRole: string;
  features: Record<string, number>;
}

const PRESETS: ScenarioPreset[] = [
  {
    name: 'Routine Office Operations',
    description: 'Compliant daytime developer activity within normal fleet baselines.',
    userId: 'USR_DEV_04',
    userRole: 'Software Engineer',
    features: {
      n_file_deletions_off_hours: 0,
      usb_bytes_out: 0,
      http_suspicious_domain_count: 0,
      logon_off_hours: 0,
      email_external_count: 2,
      file_copy_count: 12,
      privilege_escalation_sudo_count: 0,
    },
  },
  {
    name: 'Off-Hours Mass Exfiltration & Wiping',
    description: 'Severe anomaly: 4,000 files deleted at 03:00 UTC with massive USB egress.',
    userId: 'ACM2278',
    userRole: 'Lead AI Engineer',
    features: {
      n_file_deletions_off_hours: 4200,
      usb_bytes_out: 48000000000,
      http_suspicious_domain_count: 15,
      logon_off_hours: 8,
      email_external_count: 45,
      file_copy_count: 1400,
      privilege_escalation_sudo_count: 5,
    },
  },
  {
    name: 'Privilege Escalation & Cloud Sync',
    description: 'Multiple failed su/sudo calls followed by outbound transfers to untrusted hosts.',
    userId: 'VNC3104',
    userRole: 'DevOps Administrator',
    features: {
      n_file_deletions_off_hours: 240,
      usb_bytes_out: 1200000,
      http_suspicious_domain_count: 22,
      logon_off_hours: 4,
      email_external_count: 8,
      file_copy_count: 65,
      privilege_escalation_sudo_count: 9,
    },
  },
];

export const ScoringSimulatorModal: React.FC<ScoringSimulatorModalProps> = ({
  isOpen,
  onClose,
  onScoreSuccess,
}) => {
  const navigate = useNavigate();
  const [selectedPreset, setSelectedPreset] = useState<number>(1);
  const [userId, setUserId] = useState<string>(PRESETS[1].userId);
  const [userRole, setUserRole] = useState<string>(PRESETS[1].userRole);
  const [features, setFeatures] = useState<Record<string, number>>({ ...PRESETS[1].features });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSelectPreset = (index: number) => {
    setSelectedPreset(index);
    const p = PRESETS[index];
    setUserId(p.userId);
    setUserRole(p.userRole);
    setFeatures({ ...p.features });
    setResult(null);
    setError(null);
  };

  const handleFeatureChange = (key: string, val: number) => {
    setFeatures((prev) => ({ ...prev, [key]: val }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await scoreActivity({
        user_id: userId.trim(),
        user_role: userRole.trim(),
        date_day: new Date().toISOString().split('T')[0],
        metrics: features,
      });
      setResult(response);
      onScoreSuccess?.(response);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Scoring engine failed to compute.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="relative w-full max-w-3xl rounded-2xl border border-outline-variant/40 bg-surface-container-low shadow-2xl p-6 sm:p-8 space-y-6 my-8">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-outline-variant/30 pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/20 border border-primary/40 text-primary">
              <span className="material-symbols-outlined text-2xl font-bold">science</span>
            </div>
            <div>
              <h2 className="text-lg font-headline font-bold text-on-surface">
                Telemetry Threat Simulator
              </h2>
              <p className="text-xs text-on-surface-variant font-body">
                Inject synthetic activity features directly into PRISM, AIRS Autoencoder, and Policy Engine.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-surface-container-high hover:text-white transition"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        {/* Preset Selector Chips */}
        <div>
          <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">
            Select Threat Scenario Preset
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {PRESETS.map((p, idx) => (
              <button
                key={p.name}
                type="button"
                onClick={() => handleSelectPreset(idx)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  selectedPreset === idx
                    ? 'border-primary bg-primary/10 shadow-glow-primary text-on-surface'
                    : 'border-outline-variant/30 bg-surface-container hover:bg-surface-container-high text-on-surface-variant'
                }`}
              >
                <div className="font-headline text-xs font-bold">{p.name}</div>
                <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">{p.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Simulation Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Subject Employee ID
              </label>
              <input
                type="text"
                required
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full rounded-lg border border-outline-variant/40 bg-surface-container px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Enterprise Role
              </label>
              <input
                type="text"
                value={userRole}
                onChange={(e) => setUserRole(e.target.value)}
                className="w-full rounded-lg border border-outline-variant/40 bg-surface-container px-3 py-2 text-xs font-mono text-on-surface focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          {/* Telemetry Feature Sliders / Inputs */}
          <div className="rounded-xl border border-outline-variant/30 bg-surface-container/70 p-4 space-y-3">
            <span className="text-xs font-headline font-bold text-slate-200 block">
              Behavioral & Security Telemetry Features
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="flex justify-between text-slate-400 mb-1 font-mono">
                  <span>Off-Hours Deletions:</span>
                  <span className="font-bold text-primary">
                    {features.n_file_deletions_off_hours} files
                  </span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="5000"
                  step="50"
                  value={features.n_file_deletions_off_hours || 0}
                  onChange={(e) =>
                    handleFeatureChange('n_file_deletions_off_hours', Number(e.target.value))
                  }
                  className="w-full accent-primary h-1.5 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-400 mb-1 font-mono">
                  <span>USB Outbound Bytes:</span>
                  <span className="font-bold text-primary">
                    {((features.usb_bytes_out || 0) / 1000000).toFixed(1)} MB
                  </span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="50000000000"
                  step="100000000"
                  value={features.usb_bytes_out || 0}
                  onChange={(e) =>
                    handleFeatureChange('usb_bytes_out', Number(e.target.value))
                  }
                  className="w-full accent-primary h-1.5 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-400 mb-1 font-mono">
                  <span>Suspicious HTTP Domains:</span>
                  <span className="font-bold text-primary">
                    {features.http_suspicious_domain_count} hits
                  </span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="30"
                  step="1"
                  value={features.http_suspicious_domain_count || 0}
                  onChange={(e) =>
                    handleFeatureChange('http_suspicious_domain_count', Number(e.target.value))
                  }
                  className="w-full accent-primary h-1.5 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              <div>
                <label className="flex justify-between text-slate-400 mb-1 font-mono">
                  <span>Sudo Privilege Escalations:</span>
                  <span className="font-bold text-primary">
                    {features.privilege_escalation_sudo_count} attempts
                  </span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="15"
                  step="1"
                  value={features.privilege_escalation_sudo_count || 0}
                  onChange={(e) =>
                    handleFeatureChange('privilege_escalation_sudo_count', Number(e.target.value))
                  }
                  className="w-full accent-primary h-1.5 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-primary py-3 text-xs font-headline font-bold uppercase tracking-wider text-black shadow-glow-primary hover:brightness-110 active:scale-95 disabled:opacity-50 transition"
          >
            {isSubmitting ? 'Evaluating AI Ensemble...' : 'Execute Multi-Model Scoring Engine'}
          </button>
        </form>

        {/* Error state */}
        {error && (
          <div className="rounded-lg border border-error/40 bg-error/10 p-3 text-xs text-error font-mono">
            {error}
          </div>
        )}

        {/* Scoring Engine Live Results */}
        {result && (
          <div className="rounded-xl border border-primary/40 bg-surface-container/90 p-5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-3">
              <div>
                <div className="text-xs font-headline font-bold text-slate-200">
                  Computed Multi-Model Telemetry Result
                </div>
                <div className="text-[10px] font-mono text-slate-400">
                  Activity ID: #{result.activity_id} • User: {result.user_id}
                </div>
              </div>
              <RiskBadge level={result.risk_level} />
            </div>

            {/* Scores Grid */}
            <div className="grid grid-cols-3 gap-3 text-center font-mono">
              <div className="rounded-lg bg-surface-container-high p-3 border border-outline-variant/20">
                <div className="text-[10px] text-tertiary">PRISM Rule Score</div>
                <div className="text-lg font-bold text-slate-100">{result.prism_score.toFixed(3)}</div>
              </div>
              <div className="rounded-lg bg-surface-container-high p-3 border border-outline-variant/20">
                <div className="text-[10px] text-secondary">AIRS Autoencoder</div>
                <div className="text-lg font-bold text-slate-100">{result.airs_score.toFixed(3)}</div>
              </div>
              <div className="rounded-lg bg-primary/10 p-3 border border-primary/40">
                <div className="text-[10px] text-primary">Ensemble Risk</div>
                <div className="text-lg font-bold text-primary">{result.ensemble_score.toFixed(3)}</div>
              </div>
            </div>

            {/* Policy Actions */}
            {result.triggered_policies && result.triggered_policies.length > 0 ? (
              <div className="space-y-2">
                <div className="text-xs font-mono uppercase text-error font-bold flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm">gavel</span>
                  <span>Automated Containment Policies Triggered ({result.triggered_policies.length})</span>
                </div>
                <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                  {result.triggered_policies.map((act, i) => (
                    <div
                      key={i}
                      className="rounded bg-error/10 border border-error/30 p-2 text-xs flex items-center justify-between"
                    >
                      <div>
                        <span className="font-mono font-bold text-error mr-2">{act.rule_id}</span>
                        <span className="text-slate-200 font-semibold">{act.rule_name}</span>
                        <p className="text-[11px] text-slate-400">{act.description}</p>
                      </div>
                      <span className="rounded bg-error/20 px-2 py-0.5 text-[10px] font-mono font-bold text-error border border-error/40 uppercase">
                        {act.action}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 rounded p-2 text-center">
                ✓ No automated security policy thresholds breached for this activity.
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  onClose();
                  navigate(`/users/${result.user_id}`);
                }}
                className="inline-flex items-center gap-1.5 rounded-lg bg-surface-container-high px-4 py-2 text-xs font-headline font-semibold text-primary border border-primary/30 hover:bg-surface-container-highest transition"
              >
                <span>Open in Forensics Drilldown</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
