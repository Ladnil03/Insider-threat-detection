/**
 * TypeScript definitions for OpenIRM Frontend.
 * Synchronized with backend Pydantic models in `backend/api/schemas/`.
 */

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';

export interface PolicyActionSummary {
  rule_id: string;
  rule_name: string;
  severity: string;
  action: string;
  description?: string | null;
}

export interface PolicyViolation {
  id: number;
  activity_id?: number | null;
  user_id: string;
  rule_id: string;
  rule_name: string;
  severity: string;
  action: string;
  description?: string | null;
  timestamp: string;
}

export interface ScoreRequest {
  user_id: string;
  date_day?: string | null;
  user_role?: string | null;
  metrics?: Record<string, number | string | boolean>;
}

export interface ScoreResponse {
  activity_id: number;
  user_id: string;
  prism_score: number;
  airs_score: number;
  ensemble_score: number;
  risk_level: RiskLevel;
  timestamp: string;
  triggered_policies: PolicyActionSummary[];
}

export interface FeatureAttribution {
  feature: string;
  raw_key: string;
  attribution: number;
  value: number;
  percentage: number;
  direction: 'increased' | 'decreased' | string;
}

export interface ExplainResponse {
  activity_id: number;
  user_id: string;
  base_value: number;
  reconstruction_error: number;
  sai_score: number;
  human_readable_summary: string;
  top_risk_drivers: Array<Record<string, unknown>>;
  features: FeatureAttribution[];
}

export interface RiskDriver {
  feature: string;
  impact: string;
  description: string;
}

export interface RecommendationResponse {
  activity_id: number;
  user_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  summary: string;
  risk_drivers: RiskDriver[];
  recommended_action: string;
  urgency: string;
  model?: string | null;
  provider?: string | null;
  status: string;
}

export interface FeedbackCreateRequest {
  activity_id: number;
  user_id: string;
  adjusted_score: number;
  notes?: string | null;
}

export interface FeedbackResponse {
  feedback_id: number;
  activity_id: number;
  user_id: string;
  original_score: number;
  adjusted_score: number;
  blended_score: number;
  notes?: string | null;
  retrain_threshold_reached: boolean;
  timestamp: string;
}

export interface ActivityResponse {
  id: number;
  user_id: string;
  date_day?: string | null;
  metrics: Record<string, unknown>;
  created_at: string;
}

export interface UserSummaryResponse {
  user_id: string;
  user_name: string;
  role: string;
  department: string;
  latest_score: number;
  risk_level: RiskLevel;
  latest_activity_date?: string | null;
  violation_count: number;
}

export interface UserActivityHistoryItem {
  activity_id: number;
  date_day?: string | null;
  timestamp: string;
  prism_score: number;
  airs_score: number;
  ensemble_score: number;
  risk_level: RiskLevel;
  metrics: Record<string, unknown>;
}

export interface UserHistoryResponse {
  user_id: string;
  user_name: string;
  role: string;
  department: string;
  current_risk_score: number;
  current_risk_level: RiskLevel;
  history: UserActivityHistoryItem[];
  policy_violations: PolicyViolation[];
}

export interface OverviewMetrics {
  totalMonitoredUsers: number;
  highRiskCount: number;
  meanFleetRisk: number;
  activeViolationsCount: number;
  riskDistribution: Array<{
    level: RiskLevel;
    count: number;
    color: string;
  }>;
  violationsBySeverity: Array<{
    severity: string;
    count: number;
    color: string;
  }>;
  topRiskUsers: UserSummaryResponse[];
}
