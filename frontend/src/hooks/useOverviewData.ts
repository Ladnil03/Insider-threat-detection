import { useCallback, useEffect, useState } from 'react';
import { getMonitoredUsers } from '../api/scoring';
import { getPolicyViolations } from '../api/policy';
import { OverviewMetrics, PolicyViolation, RiskLevel, UserSummaryResponse } from '../types';

interface UseOverviewDataResult {
  data: OverviewMetrics | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  violations: PolicyViolation[];
}

export const useOverviewData = (): UseOverviewDataResult => {
  const [data, setData] = useState<OverviewMetrics | null>(null);
  const [violations, setViolations] = useState<PolicyViolation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [users, rawViolations] = await Promise.all([
        getMonitoredUsers(),
        getPolicyViolations(100),
      ]);

      setViolations(rawViolations);

      // 1. Calculate risk distribution buckets
      const riskCounts: Record<RiskLevel, number> = {
        LOW: 0,
        MODERATE: 0,
        HIGH: 0,
        CRITICAL: 0,
      };

      let totalScore = 0;
      let highRiskCount = 0;

      users.forEach((u: UserSummaryResponse) => {
        const rawLevel = String(u.risk_level).toUpperCase();
        const lvl: RiskLevel =
          rawLevel === 'MEDIUM' || rawLevel === 'MODERATE'
            ? 'MODERATE'
            : rawLevel === 'HIGH'
              ? 'HIGH'
              : rawLevel === 'CRITICAL'
                ? 'CRITICAL'
                : 'LOW';

        if (riskCounts[lvl] !== undefined) {
          riskCounts[lvl] += 1;
        } else {
          riskCounts.LOW += 1;
        }

        totalScore += u.latest_score;
        if (lvl === 'HIGH' || lvl === 'CRITICAL') {
          highRiskCount += 1;
        }
      });

      const riskDistribution = [
        { level: 'LOW' as RiskLevel, count: riskCounts.LOW, color: '#10b981' },
        { level: 'MODERATE' as RiskLevel, count: riskCounts.MODERATE, color: '#f59e0b' },
        { level: 'HIGH' as RiskLevel, count: riskCounts.HIGH, color: '#f97316' },
        { level: 'CRITICAL' as RiskLevel, count: riskCounts.CRITICAL, color: '#f43f5e' },
      ];

      // 2. Aggregate violations by severity
      const severityCounts: Record<string, number> = {
        CRITICAL: 0,
        HIGH: 0,
        MEDIUM: 0,
        LOW: 0,
      };

      rawViolations.forEach((v: PolicyViolation) => {
        const sev = (v.severity || 'HIGH').toUpperCase();
        if (severityCounts[sev] !== undefined) {
          severityCounts[sev] += 1;
        } else {
          severityCounts.HIGH += 1;
        }
      });

      const violationsBySeverity = [
        { severity: 'CRITICAL', count: severityCounts.CRITICAL, color: '#f43f5e' },
        { severity: 'HIGH', count: severityCounts.HIGH, color: '#f97316' },
        { severity: 'MEDIUM', count: severityCounts.MEDIUM, color: '#f59e0b' },
        { severity: 'LOW', count: severityCounts.LOW, color: '#10b981' },
      ];

      // 3. Top 10 highest-risk users sorted descending by latest_score
      const sortedUsers = [...users].sort(
        (a, b) => b.latest_score - a.latest_score
      );
      const topRiskUsers = sortedUsers.slice(0, 10);

      const meanFleetRisk =
        users.length > 0 ? Number((totalScore / users.length).toFixed(4)) : 0;

      setData({
        totalMonitoredUsers: users.length,
        highRiskCount,
        meanFleetRisk,
        activeViolationsCount: rawViolations.length,
        riskDistribution,
        violationsBySeverity,
        topRiskUsers,
      });
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Failed to retrieve insider risk overview telemetry.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    violations,
    isLoading,
    error,
    refetch: fetchData,
  };
};

export default useOverviewData;
