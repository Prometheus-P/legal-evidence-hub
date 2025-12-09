/**
 * AI Recommendations Hook
 * 009-calm-control-design-system
 *
 * Fetches AI-suggested tasks for the lawyer dashboard
 */

'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import type { AIRecommendation } from '@/components/lawyer/AIRecommendationCard';

interface UseAIRecommendationsResult {
  recommendations: AIRecommendation[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useAIRecommendations(): UseAIRecommendationsResult {
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Try to fetch from API
      const response = await apiClient.get<{ recommendations: AIRecommendation[] }>('/ai/recommendations');
      if (response.data) {
        setRecommendations(response.data.recommendations || []);
      }
    } catch {
      // API might not exist yet, use empty state for development
      const mockRecommendations: AIRecommendation[] = [];
      setRecommendations(mockRecommendations);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  return {
    recommendations,
    isLoading,
    error,
    refetch: fetchRecommendations,
  };
}
