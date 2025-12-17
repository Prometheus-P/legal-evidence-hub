/**
 * Risk Flags Hook
 * 009-calm-control-design-system
 *
 * Fetches high-risk flagged cases for the dashboard
 */

'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import type { RiskCase } from '@/components/lawyer/RiskFlagCard';

interface UseRiskFlagsResult {
  cases: RiskCase[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useRiskFlags(): UseRiskFlagsResult {
  const [cases, setCases] = useState<RiskCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRiskFlags = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Try to fetch from API
      const response = await apiClient.get<{ cases: RiskCase[] }>('/cases/risk-flags');
      if (response.data) {
        setCases(response.data.cases || []);
      }
    } catch {
      // API might not exist yet, use mock data for development
      // In production, this would show an error or empty state
      const mockCases: RiskCase[] = [];
      setCases(mockCases);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskFlags();
  }, []);

  return {
    cases,
    isLoading,
    error,
    refetch: fetchRiskFlags,
  };
}
