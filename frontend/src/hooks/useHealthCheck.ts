import { useEffect, useState } from 'react';
import axios from 'axios';

interface HealthStatus {
  isOnline: boolean;
  latencyMs: number | null;
  version: string | null;
  lastChecked: Date | null;
}

export const useHealthCheck = (intervalMs: number = 15000): HealthStatus => {
  const [status, setStatus] = useState<HealthStatus>({
    isOnline: false,
    latencyMs: null,
    version: null,
    lastChecked: null,
  });

  useEffect(() => {
    let isMounted = true;

    const check = async () => {
      const startTime = performance.now();
      try {
        // Use relative URL /health which is proxied to backend port 8000
        const healthUrl = import.meta.env.VITE_API_BASE_URL 
          ? import.meta.env.VITE_API_BASE_URL.replace(/\/api\/v1\/?$/, '/health') 
          : '/health';

        const res = await axios.get(healthUrl, { timeout: 4000 });
        const latency = Math.round(performance.now() - startTime);

        if (isMounted) {
          setStatus({
            isOnline: res.status === 200,
            latencyMs: latency,
            version: res.data?.version || '0.1.0',
            lastChecked: new Date(),
          });
        }
      } catch {
        if (isMounted) {
          setStatus({
            isOnline: false,
            latencyMs: null,
            version: null,
            lastChecked: new Date(),
          });
        }
      }
    };

    check();
    const interval = setInterval(check, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [intervalMs]);

  return status;
};
