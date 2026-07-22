import apiClient from "./client";
import type { PolicyViolation } from "../types";

export async function fetchPolicyViolations(userId?: string): Promise<PolicyViolation[]> {
  const params = userId ? { userId } : {};
  const { data } = await apiClient.get<PolicyViolation[]>("/policy-violations", { params });
  return data;
}
