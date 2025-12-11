/**
 * useInvestigators Hook
 * 005-lawyer-portal-pages Feature - US3 (T039)
 *
 * Hook for lawyer's investigator management.
 */

import { useState, useEffect, useCallback } from 'react';
import { getInvestigators, getInvestigatorDetail } from '@/lib/api/investigators';
import type {
  InvestigatorItem,
  InvestigatorFilter,
  InvestigatorDetail,
  InvestigatorAvailability,
} from '@/types/investigator';

interface UseInvestigatorsOptions {
  initialFilters?: InvestigatorFilter;
  autoFetch?: boolean;
}

interface UseInvestigatorsReturn {
  investigators: InvestigatorItem[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: InvestigatorFilter;
  setFilters: (filters: InvestigatorFilter) => void;
  setPage: (page: number) => void;
  refetch: () => Promise<void>;
  getDetail: (investigatorId: string) => Promise<InvestigatorDetail | null>;
}

export function useInvestigators(options: UseInvestigatorsOptions = {}): UseInvestigatorsReturn {
  const { initialFilters = {}, autoFetch = true } = options;

  const [investigators, setInvestigators] = useState<InvestigatorItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialFilters.page ?? 1);
  const [pageSize] = useState(initialFilters.page_size ?? 20);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<InvestigatorFilter>(initialFilters);

  const fetchInvestigators = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { data, error: apiError } = await getInvestigators({
        ...filters,
        page,
        page_size: pageSize,
      });

      if (apiError) {
        setError(apiError);
        setInvestigators([]);
        setTotal(0);
        setTotalPages(0);
      } else if (data) {
        setInvestigators(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      }
    } catch {
      setError('조사원 목록을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoFetch) {
      fetchInvestigators();
    }
  }, [fetchInvestigators, autoFetch]);

  const handleSetFilters = useCallback((newFilters: InvestigatorFilter) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  }, []);

  const getDetail = useCallback(async (investigatorId: string): Promise<InvestigatorDetail | null> => {
    try {
      const { data, error: apiError } = await getInvestigatorDetail(investigatorId);

      if (apiError || !data) {
        setError(apiError || '조사원 정보를 불러올 수 없습니다.');
        return null;
      }

      return data;
    } catch {
      setError('조사원 정보를 불러오는 중 오류가 발생했습니다.');
      return null;
    }
  }, []);

  return {
    investigators,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters: handleSetFilters,
    setPage,
    refetch: fetchInvestigators,
    getDetail,
  };
}

// Helper function to get availability badge style
export function getAvailabilityStyle(availability: InvestigatorAvailability): string {
  switch (availability) {
    case 'available':
      return 'bg-green-100 text-green-700';
    case 'busy':
      return 'bg-yellow-100 text-yellow-700';
    case 'unavailable':
      return 'bg-red-100 text-red-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
}

// Helper function to get availability label in Korean
export function getAvailabilityLabel(availability: InvestigatorAvailability): string {
  switch (availability) {
    case 'available':
      return '배정 가능';
    case 'busy':
      return '바쁨';
    case 'unavailable':
      return '배정 불가';
    default:
      return availability;
  }
}
