/* Shared TypeScript types mirroring backend Pydantic schemas. */

export interface RiskScore {
  userId: string;
  prismScore: number;
  airsScore: number;
  blendedScore: number;
  severityBucket: "low" | "medium" | "high" | "critical";
}

export interface ShapExplanation {
  feature: string;
  value: number;
  contribution: number;
}

export interface Recommendation {
  userId: string;
  text: string;
  generatedAt: string;
}

export interface Feedback {
  userId: string;
  scoreAdjustment: number;
  comment: string;
}

export interface PolicyViolation {
  id: number;
  userId: string;
  ruleName: string;
  severity: string;
  reason: string;
  timestamp: string;
}
