import { apiClient } from './client';
import { PolicyViolation } from '../types';

/**
 * Retrieves the audit log of triggered automated containment policy violations.
 */
export const getPolicyViolations = async (
  limit = 50,
  severity?: string
): Promise<PolicyViolation[]> => {
  const params: Record<string, string | number> = { limit };
  if (severity) {
    params.severity = severity;
  }
  const response = await apiClient.get<PolicyViolation[]>('/policy-violations', {
    params,
  });
  return response.data;
};
