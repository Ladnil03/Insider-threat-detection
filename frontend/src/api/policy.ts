import { apiClient } from './client';
import { PolicyViolation } from '../types';

export const fetchPolicyViolations = async (): Promise<PolicyViolation[]> => {
  const response = await apiClient.get<PolicyViolation[]>('/policy-violations');
  return response.data;
};
