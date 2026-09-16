import { apiClient } from './client';
import {
  ExplainResponse,
  RecommendationResponse,
  ScoreRequest,
  ScoreResponse,
  UserHistoryResponse,
  UserSummaryResponse,
} from '../types';

/**
 * Submits user activity telemetry features for multi-model risk evaluation (PRISM + AIRS + Ensemble).
 */
export const scoreActivity = async (payload: ScoreRequest): Promise<ScoreResponse> => {
  const response = await apiClient.post<ScoreResponse>('/score', payload);
  return response.data;
};

/**
 * Retrieves SHAP feature attribution explanation for a scored activity record.
 */
export const getExplanation = async (activityId: number): Promise<ExplainResponse> => {
  const response = await apiClient.get<ExplainResponse>(`/explain/${activityId}`);
  return response.data;
};

/**
 * Retrieves natural-language LLM analyst recommendation and risk drivers for a scored activity.
 */
export const getRecommendation = async (activityId: number): Promise<RecommendationResponse> => {
  const response = await apiClient.get<RecommendationResponse>(`/recommend/${activityId}`);
  return response.data;
};

/**
 * Fetches directory of all monitored enterprise users with their latest computed risk scores.
 */
export const getMonitoredUsers = async (): Promise<UserSummaryResponse[]> => {
  const response = await apiClient.get<UserSummaryResponse[]>('/users');
  return response.data;
};

/**
 * Retrieves longitudinal timeline, scores, and policy violation history for a target employee.
 */
export const getUserHistory = async (userId: string): Promise<UserHistoryResponse> => {
  const response = await apiClient.get<UserHistoryResponse>(`/users/${encodeURIComponent(userId)}/history`);
  return response.data;
};
