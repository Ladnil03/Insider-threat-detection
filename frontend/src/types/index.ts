export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface ScoreResponse {
  user_id: string;
  prism_score: number;
  airs_score: number;
  composite_score: number;
  risk_level: RiskLevel;
}

export interface ExplainResponse {
  user_id: string;
  base_value: number;
  attributions: Record<string, number>;
}

export interface RecommendResponse {
  user_id: string;
  recommendation: string;
  provider: string;
}

export interface PolicyViolation {
  user_id: string;
  rule_id: string;
  action_taken: string;
  timestamp: string;
}
