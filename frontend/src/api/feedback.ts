import { apiClient } from './client';

export interface FeedbackPayload {
  user_id: string;
  adjusted_score: number;
  notes?: string;
}

export const submitFeedback = async (payload: FeedbackPayload): Promise<{ status: string }> => {
  const response = await apiClient.post<{ status: string }>('/feedback', payload);
  return response.data;
};
