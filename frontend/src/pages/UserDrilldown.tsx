import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getExplanation, getMonitoredUsers, getRecommendation, getUserHistory } from '../api/scoring';
import { ExplainResponse, RecommendationResponse, UserActivityHistoryItem, UserHistoryResponse, UserSummaryResponse } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { ActivityTimeline } from '../components/ActivityTimeline';
import { ShapExplanationPanel } from '../components/ShapExplanationPanel';
import { RecommendationCard } from '../components/RecommendationCard';
import { FeedbackPanel } from './FeedbackPanel';

export const UserDrilldown: React.FC = () => {
  const { userId: routeUserId } = useParams<{ userId: string }>();
  const navigate = useNavigate();

  // User list for selector
  const [users, setUsers] = useState<UserSummaryResponse[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>(routeUserId || '');
  const [userSearchQuery, setUserSearchQuery] = useState<string>('');

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

  // Active view tab for the activity analysis area
  const [activeTab, setActiveTab] = useState<'xai' | 'llm' | 'feedback'>('xai');

  // 1. Fetch available monitored users directory
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getMonitoredUsers();
        setUsers(data);
        if (!selectedUserId && data.length > 0) {
          // Default to highest risk user if none specified in route
          const sorted = [...data].sort((a, b) => b.latest_score - a.latest_score);
          setSelectedUserId(sorted[0].user_id);
        }
      } catch (err) {
        console.error('Failed to load users directory:', err);
      }
    };
    fetchUsers();
  }, [selectedUserId]);

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

  const filteredUsers = users.filter(
    (u) =>
      u.user_id.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
      u.user_name.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
      u.role.toLowerCase().includes(userSearchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8">
      {/* Top Header & Entity Selector */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black tracking-tight text-slate-100 sm:text-3xl">
              Entity Risk Drilldown
            </h1>
            {userHistory && (
              <RiskBadge
                level={userHistory.current_risk_level}
                score={userHistory.current_risk_score}
                showScore={true}
              />
            )}
          </div>
          <p className="mt-1 text-sm text-slate-400">
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
              className="w-full sm:w-44 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <select
            value={selectedUserId}
            onChange={(e) => handleSelectUser(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 focus:border-blue-500 focus:outline-none"
          >
            {filteredUsers.map((u) => (
              <option key={u.user_id} value={u.user_id}>
                {u.user_name} ({u.user_id}) — {u.risk_level} ({(u.latest_score || 0).toFixed(2)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Entity Profile Meta Card */}
      {userHistory && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-xs">
          <div>
            <span className="text-slate-400 uppercase tracking-wider text-[10px] block font-semibold">
              Employee Name
            </span>
            <span className="text-sm font-bold text-slate-100">{userHistory.user_name}</span>
          </div>
          <div>
            <span className="text-slate-400 uppercase tracking-wider text-[10px] block font-semibold">
              Role & Department
            </span>
            <span className="text-sm font-bold text-slate-200">
              {userHistory.role} • {userHistory.department}
            </span>
          </div>
          <div>
            <span className="text-slate-400 uppercase tracking-wider text-[10px] block font-semibold">
              Active Policy Alerts
            </span>
            <span
              className={`text-sm font-bold ${
                userHistory.policy_violations.length > 0 ? 'text-rose-400' : 'text-slate-300'
              }`}
            >
              {userHistory.policy_violations.length} triggered
            </span>
          </div>
          <div>
            <span className="text-slate-400 uppercase tracking-wider text-[10px] block font-semibold">
              Telemetry Days
            </span>
            <span className="text-sm font-mono font-bold text-blue-400">
              {userHistory.history.length} daily user-records
            </span>
          </div>
        </div>
      )}

      {/* History Loading / Error States */}
      {isHistoryLoading && (
        <div className="flex min-h-[30vh] flex-col items-center justify-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
          <p className="text-xs text-slate-400">Retrieving longitudinal telemetry history...</p>
        </div>
      )}

      {historyError && (
        <div className="rounded-xl border border-rose-800 bg-rose-950/40 p-6 text-center text-xs text-rose-300">
          <p className="font-semibold">Unable to load entity history:</p>
          <p className="mt-1">{historyError}</p>
          <button
            onClick={() => loadUserHistory(selectedUserId)}
            className="mt-4 rounded bg-rose-600 px-3 py-1 text-white font-semibold hover:bg-rose-500"
          >
            Retry
          </button>
        </div>
      )}

      {/* Longitudinal Timeline Section */}
      {!isHistoryLoading && userHistory && (
        <ActivityTimeline
          history={userHistory.history}
          selectedActivityId={selectedActivity?.activity_id}
          onSelectActivity={(item) => setSelectedActivity(item)}
        />
      )}

      {/* Active Activity Deep Dive Section */}
      {selectedActivity && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-3 gap-2">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-100">
                  Event Analysis: Activity #{selectedActivity.activity_id}
                </h2>
                <span className="font-mono text-xs text-slate-400">
                  [{selectedActivity.date_day || new Date(selectedActivity.timestamp).toLocaleDateString()}]
                </span>
                <RiskBadge level={selectedActivity.risk_level} />
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Ensemble: {selectedActivity.ensemble_score.toFixed(4)} | AIRS Anomaly: {selectedActivity.airs_score.toFixed(4)} | PRISM Rules: {selectedActivity.prism_score.toFixed(4)}
              </p>
            </div>

            {/* Analysis Tabs */}
            <div className="flex rounded-lg border border-slate-800 bg-slate-950 p-1 text-xs font-semibold">
              <button
                onClick={() => setActiveTab('xai')}
                className={`rounded-md px-3 py-1 transition ${
                  activeTab === 'xai'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                SHAP Explainability
              </button>
              <button
                onClick={() => setActiveTab('llm')}
                className={`rounded-md px-3 py-1 transition ${
                  activeTab === 'llm'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                AI Recommendation
              </button>
              <button
                onClick={() => setActiveTab('feedback')}
                className={`rounded-md px-3 py-1 transition ${
                  activeTab === 'feedback'
                    ? 'bg-blue-600 text-white shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Analyst Calibration
              </button>
            </div>
          </div>

          {/* Active Tab Panel */}
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
            />
          )}

          {activeTab === 'feedback' && (
            <FeedbackPanel
              initialUserId={selectedUserId}
              initialActivityId={selectedActivity.activity_id}
              initialScore={selectedActivity.ensemble_score}
              isEmbedded={true}
              onFeedbackSubmitted={(result) => {
                // Update active activity score in place
                setSelectedActivity((prev) =>
                  prev ? { ...prev, ensemble_score: result.blended_score } : null
                );
              }}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default UserDrilldown;
