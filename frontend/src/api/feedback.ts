import { apiClient } from './client';
import { FeedbackCreateRequest, FeedbackResponse } from '../types';

/**
 * Submits analyst risk score adjustment feedback to the backend.
 * Feeds the incremental online fine-tuning buffer and mathematical score blending.
 */
export const submitFeedback = async (
  payload: FeedbackCreateRequest
): Promise<FeedbackResponse> => {
  const response = await apiClient.post<FeedbackResponse>('/feedback', payload);
  return response.data;
};
