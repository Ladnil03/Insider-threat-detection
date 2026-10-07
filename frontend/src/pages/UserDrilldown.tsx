import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { getExplanation, getMonitoredUsers, getRecommendation, getUserHistory } from '../api/scoring';
import {
  ExplainResponse,
  RecommendationResponse,
  UserActivityHistoryItem,
  UserHistoryResponse,
  UserSummaryResponse,
} from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { RiskGauge } from '../components/RiskGauge';
import { ActivityTimeline } from '../components/ActivityTimeline';
import { ShapExplanationPanel } from '../components/ShapExplanationPanel';
import { RecommendationCard } from '../components/RecommendationCard';
import { FeedbackPanel } from './FeedbackPanel';

export const UserDrilldown: React.FC = () => {
  const { userId: routeUserId } = useParams<{ userId: string }>();
  const [searchParams] = useSearchParams();
  const searchFilterParam = searchParams.get('search') || '';
  const navigate = useNavigate();

  // User list for selector
  const [users, setUsers] = useState<UserSummaryResponse[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>(routeUserId || '');
  const [userSearchQuery, setUserSearchQuery] = useState<string>(searchFilterParam);

  // Target user detailed history
  const [userHistory, setUserHistory] = useState<UserHistoryResponse | null>(null);
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Active selected activity state
  const [selectedActivity, setSelectedActivity] = useState<UserActivityHistoryItem | null>(null);

  // SHAP and Recommendation responses for active activity
  const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
  const [isExplainLoading, setIsExplainLoading] = useState<boolean>(false);

  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [isRecommendLoading, setIsRecommendLoading] = useState<boolean>(false);
  const [recommendError, setRecommendError] = useState<string | null>(null);

  // Active view tab for the forensic analysis area
  const [activeTab, setActiveTab] = useState<'xai' | 'llm' | 'feedback'>('xai');

  // Quick containment notification state
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // 1. Fetch available monitored users directory
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getMonitoredUsers();
        setUsers(data);
        if (!selectedUserId && data.length > 0) {
          // If search filter matches a user, pick that one
          if (searchFilterParam) {
            const match = data.find(
              (u) =>
                u.user_id.toLowerCase().includes(searchFilterParam.toLowerCase()) ||
                u.user_name.toLowerCase().includes(searchFilterParam.toLowerCase())
            );
            if (match) {
              setSelectedUserId(match.user_id);
              return;
            }
          }
          // Default to highest risk user
          const sorted = [...data].sort((a, b) => b.latest_score - a.latest_score);
          setSelectedUserId(sorted[0].user_id);
        }
      } catch (err) {
        console.error('Failed to load users directory:', err);
      }
    };
    fetchUsers();
  }, [selectedUserId, searchFilterParam]);

  // Sync route param changes
  useEffect(() => {
    if (routeUserId && routeUserId !== selectedUserId) {
      setSelectedUserId(routeUserId);
    }
  }, [routeUserId, selectedUserId]);

  // 2. Load target user history when selectedUserId changes
  const loadUserHistory = useCallback(async (targetId: string) => {
    if (!targetId) return;
    setIsHistoryLoading(true);
    setHistoryError(null);
    setSelectedActivity(null);
    setExplanation(null);
    setRecommendation(null);

    try {
      const historyData = await getUserHistory(targetId);
      setUserHistory(historyData);

      // Auto-select latest activity if available
      if (historyData.history && historyData.history.length > 0) {
        const latest = historyData.history[historyData.history.length - 1];
        setSelectedActivity(latest);
      }
    } catch (err: unknown) {
      setHistoryError(err instanceof Error ? err.message : `Failed to load history for user ${targetId}.`);
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      loadUserHistory(selectedUserId);
    }
  }, [selectedUserId, loadUserHistory]);

  // 3. Load SHAP and LLM Recommendation when selectedActivity changes
  useEffect(() => {
    if (!selectedActivity) return;

    const activityId = selectedActivity.activity_id;

    // Fetch SHAP explainability
    setIsExplainLoading(true);
    getExplanation(activityId)
      .then((data) => setExplanation(data))
      .catch((err) => {
        console.warn('SHAP attribution fetch warning:', err);
        setExplanation(null);
      })
      .finally(() => setIsExplainLoading(false));

    // Fetch Groq LLM Recommendation
    setIsRecommendLoading(true);
    setRecommendError(null);
    getRecommendation(activityId)
      .then((data) => setRecommendation(data))
      .catch((err: unknown) => {
        setRecommendError(err instanceof Error ? err.message : 'Recommendation failed.');
        setRecommendation(null);
      })
      .finally(() => setIsRecommendLoading(false));
  }, [selectedActivity]);

  const handleSelectUser = (id: string) => {
    setSelectedUserId(id);
    navigate(`/users/${id}`);
  };

  const handleTriggerContainment = (action: string) => {
    setStatusMessage(`Containment Protocol Dispatched: ${action} for ${selectedUserId}.`);
    setTimeout(() => setStatusMessage(null), 5000);
  };

  const filteredUsers = users.filter(
    (u) =>
      u.user_id.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
      u.user_name.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
      u.role.toLowerCase().includes(userSearchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header & Entity Selector */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between border-b border-outline-variant/30 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-headline font-black tracking-wider text-slate-100 uppercase">
              User Forensics & Risk Drilldown
            </h1>
            {userHistory && (
              <RiskBadge
                level={userHistory.current_risk_level}
                score={userHistory.current_risk_score}
                showScore={true}
              />
            )}
          </div>
          <p className="mt-1 text-xs text-on-surface-variant font-body">
            Deep forensic telemetry, autoencoder anomaly decomposition, and open-weight LLM reasoning.
          </p>
        </div>

        {/* Searchable User Selector Dropdown */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
          <div className="relative">
            <input
              type="text"
              placeholder="Search employee..."
              value={userSearchQuery}
              onChange={(e) => setUserSearchQuery(e.target.value)}
              className="w-full sm:w-44 rounded-lg border border-outline-variant/40 bg-surface-container px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-primary focus:outline-none font-mono"
            />
          </div>

          <select
            value={selectedUserId}
            onChange={(e) => handleSelectUser(e.target.value)}
            className="rounded-lg border border-outline-variant/40 bg-surface-container px-3 py-1.5 text-xs font-headline font-semibold text-slate-200 focus:border-primary focus:outline-none"
          >
            {filteredUsers.map((u) => (
              <option key={u.user_id} value={u.user_id}>
                {u.user_name} ({u.user_id}) — {u.risk_level} ({(u.latest_score || 0).toFixed(2)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Containment notification */}
      {statusMessage && (
        <div className="rounded-xl border border-error/50 bg-error/15 p-3 text-xs font-mono text-error flex items-center justify-between shadow-glow-danger animate-pulse">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-base">emergency</span>
            <span>{statusMessage}</span>
          </div>
          <button onClick={() => setStatusMessage(null)} className="text-slate-400 hover:text-white">
            <span className="material-symbols-outlined text-sm">close</span>
          </button>
        </div>
      )}

      {/* Error state */}
      {historyError && (
        <div className="rounded-xl border border-error/50 bg-error/10 p-5 text-center text-xs font-mono text-error">
          {historyError}
        </div>
      )}

      {/* Loading state */}
      {isHistoryLoading && (
        <div className="flex min-h-[40vh] flex-col items-center justify-center space-y-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent shadow-glow-primary" />
          <p className="text-xs font-mono text-slate-400">
            Reconstructing longitudinal telemetry for {selectedUserId}...
          </p>
        </div>
      )}

      {/* Subject Profile & Multi-Model Gauges Header */}
      {userHistory && !isHistoryLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
          {/* Subject Profile Card */}
          <div className="lg:col-span-2 rounded-xl border border-outline-variant/30 bg-surface-container/90 p-5 shadow-xl backdrop-blur-md flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-outline-variant/20 pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-surface-container-high border border-primary/40 flex items-center justify-center font-headline font-extrabold text-base text-primary shadow-glow-primary">
                    {userHistory.user_name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <div className="font-headline font-bold text-base text-slate-100 flex items-center gap-2">
                      <span>{userHistory.user_name}</span>
                      <span className="text-xs font-mono text-tertiary">({userHistory.user_id})</span>
                    </div>
                    <div className="text-xs text-on-surface-variant font-body">
                      {userHistory.role} • {userHistory.department}
                    </div>
                  </div>
                </div>

                <span
                  className={`rounded-full px-2.5 py-1 text-[10px] font-mono font-bold uppercase border ${
                    userHistory.current_risk_score >= 0.8
                      ? 'bg-rose-950/80 text-rose-300 border-rose-800'
                      : 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                  }`}
                >
                  {userHistory.current_risk_score >= 0.8 ? 'QUARANTINED' : 'ACTIVE MONITORING'}
                </span>
              </div>

              {/* Meta Specs Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs font-mono">
                <div className="rounded-lg bg-surface-container-high/60 p-2.5 border border-outline-variant/20">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Clearance Tier</span>
                  <span className="font-bold text-slate-200">Alpha-TopSecret</span>
                </div>
                <div className="rounded-lg bg-surface-container-high/60 p-2.5 border border-outline-variant/20">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Endpoint IP</span>
                  <span className="font-bold text-tertiary">192.168.4.120</span>
                </div>
                <div className="rounded-lg bg-surface-container-high/60 p-2.5 border border-outline-variant/20">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Policy Alerts</span>
                  <span className="font-bold text-error">
                    {userHistory.policy_violations ? userHistory.policy_violations.length : 0} Logged
                  </span>
                </div>
                <div className="rounded-lg bg-surface-container-high/60 p-2.5 border border-outline-variant/20">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Telemetry Status</span>
                  <span className="font-bold text-emerald-400">99.8% Heartbeat</span>
                </div>
              </div>
            </div>

            {/* Tactical Actions Strip */}
            <div className="pt-4 border-t border-outline-variant/20 flex flex-wrap gap-2 items-center">
              <button
                onClick={() => handleTriggerContainment('ISOLATE_NETWORK_TUNNEL')}
                className="px-3 py-1.5 rounded-lg bg-error/20 text-error border border-error/40 text-xs font-headline font-bold uppercase tracking-wider hover:bg-error/30 transition active:scale-95 flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-sm">lock</span>
                <span>Suspend Access</span>
              </button>
              <button
                onClick={() => handleTriggerContainment('CAPTURE_ENDPOINT_MEMORY_SNAPSHOT')}
                className="px-3 py-1.5 rounded-lg bg-surface-container-high text-slate-200 border border-outline-variant/40 text-xs font-headline font-semibold hover:bg-surface-container-highest transition active:scale-95 flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-sm">memory</span>
                <span>Snapshot Memory</span>
              </button>
              <button
                onClick={() => setActiveTab('feedback')}
                className="px-3 py-1.5 rounded-lg bg-primary/20 text-primary border border-primary/40 text-xs font-headline font-semibold hover:bg-primary/30 transition active:scale-95 flex items-center gap-1.5 ml-auto"
              >
                <span className="material-symbols-outlined text-sm">tune</span>
                <span>Calibrate Risk</span>
              </button>
            </div>
          </div>

          {/* Risk Dial & Multi-Model Breakdown */}
          <div className="rounded-xl border border-outline-variant/30 bg-surface-container/90 p-4 shadow-xl backdrop-blur-md flex flex-col items-center justify-between">
            <RiskGauge
              score={userHistory.current_risk_score}
              title="Ensemble Risk Score"
              size="md"
              trendText="+18.4% vs 7d Mean"
            />
            <div className="w-full grid grid-cols-2 gap-2 pt-2 border-t border-outline-variant/20 font-mono text-center text-xs">
              <div className="rounded bg-surface-container-high p-2 border border-outline-variant/20">
                <span className="text-[10px] text-tertiary block">PRISM Heuristic</span>
                <span className="text-sm font-bold text-slate-100">
                  {selectedActivity ? selectedActivity.prism_score.toFixed(3) : '0.000'}
                </span>
              </div>
              <div className="rounded bg-surface-container-high p-2 border border-outline-variant/20">
                <span className="text-[10px] text-secondary block">AIRS Autoencoder</span>
                <span className="text-sm font-bold text-slate-100">
                  {selectedActivity ? selectedActivity.airs_score.toFixed(3) : '0.000'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Activity Timeline */}
      {userHistory && !isHistoryLoading && (
        <ActivityTimeline
          history={userHistory.history}
          selectedActivityId={selectedActivity?.activity_id}
          onSelectActivity={(act) => setSelectedActivity(act)}
        />
      )}

      {/* Forensic Deep Dive Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-outline-variant/30 pb-2">
        <button
          onClick={() => setActiveTab('xai')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-headline font-bold uppercase tracking-wider transition ${
            activeTab === 'xai'
              ? 'bg-primary text-black shadow-glow-primary'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-white'
          }`}
        >
          <span className="material-symbols-outlined text-sm">waterfall_chart</span>
          <span>SHAP Explainability (XAI)</span>
        </button>

        <button
          onClick={() => setActiveTab('llm')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-headline font-bold uppercase tracking-wider transition ${
            activeTab === 'llm'
              ? 'bg-primary text-black shadow-glow-primary'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-white'
          }`}
        >
          <span className="material-symbols-outlined text-sm">smart_toy</span>
          <span>AI Threat Narrative & Playbook</span>
        </button>

        <button
          onClick={() => setActiveTab('feedback')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-headline font-bold uppercase tracking-wider transition ${
            activeTab === 'feedback'
              ? 'bg-primary text-black shadow-glow-primary'
              : 'text-on-surface-variant hover:bg-surface-container hover:text-white'
          }`}
        >
          <span className="material-symbols-outlined text-sm">tune</span>
          <span>Analyst Calibration Feedback</span>
        </button>
      </div>

      {/* Active Tab Content Area */}
      <div>
        {activeTab === 'xai' && (
          <ShapExplanationPanel
            features={explanation?.features || []}
            baseValue={explanation?.base_value}
            reconstructionError={explanation?.reconstruction_error}
            saiScore={explanation?.sai_score}
            summary={explanation?.human_readable_summary}
            topRiskDrivers={explanation?.top_risk_drivers}
            isLoading={isExplainLoading}
          />
        )}

        {activeTab === 'llm' && (
          <RecommendationCard
            recommendation={recommendation}
            isLoading={isRecommendLoading}
            error={recommendError}
            onTriggerContainment={handleTriggerContainment}
          />
        )}

        {activeTab === 'feedback' && (
          <FeedbackPanel
            initialUserId={selectedUserId}
            initialActivityId={selectedActivity?.activity_id || 1}
            initialScore={selectedActivity?.ensemble_score || 0.5}
            isEmbedded={true}
            onFeedbackSubmitted={(res) => {
              setStatusMessage(`Human calibration committed: New blended score = ${res.blended_score.toFixed(3)}.`);
              loadUserHistory(selectedUserId);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default UserDrilldown;
