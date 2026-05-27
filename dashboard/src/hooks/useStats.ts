import { useState, useEffect } from 'react';

interface RouterStats {
  total_requests: number;
  requests_today: number;
  cost_today_usd: number;
  tier_distribution: Record<string, number>;
}

export const useStats = (apiUrl: string) => {
  const [stats, setStats] = useState<RouterStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${apiUrl}/status`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        setStats({
          total_requests: data.stats?.total_requests || 0,
          requests_today: data.stats?.requests_today || 0,
          cost_today_usd: data.stats?.cost_today_usd || 0,
          tier_distribution: data.stats?.tier_distribution || {},
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [apiUrl]);

  return { stats, loading, error };
};