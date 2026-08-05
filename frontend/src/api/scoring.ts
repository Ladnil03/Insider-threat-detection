import { apiClient } from './client';
import { ScoreResponse, ExplainResponse, RecommendResponse } from '../types';

export const fetchUserScore = async (userId: string): Promise<ScoreResponse> => {
  const response = await apiClient.post<ScoreResponse>('/score', { user_id: userId });
  return response.data;
};

export const fetchUserExplanation = async (userId: string): Promise<ExplainResponse> => {
  const response = await apiClient.post<ExplainResponse>('/explain', { user_id: userId });
  return response.data;
};

export const fetchUserRecommendation = async (userId: string): Promise<RecommendResponse> => {
  const response = await apiClient.post<RecommendResponse>('/recommend', { user_id: userId });
  return response.data;
};
