import apiClient from "./client";
import type { RiskScore, ShapExplanation, Recommendation } from "../types";

export async function fetchRiskScore(userId: string): Promise<RiskScore> {
  const { data } = await apiClient.post<RiskScore>("/score", { userId });
  return data;
}

export async function fetchExplanation(userId: string, activityId: string): Promise<ShapExplanation[]> {
  const { data } = await apiClient.post<ShapExplanation[]>("/explain", { userId, activityId });
  return data;
}

export async function fetchRecommendation(userId: string, activityId: string): Promise<Recommendation> {
  const { data } = await apiClient.post<Recommendation>("/recommend", { userId, activityId });
  return data;
}
