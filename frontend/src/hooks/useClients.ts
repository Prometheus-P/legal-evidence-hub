/**
 * useClients Hook
 * 005-lawyer-portal-pages Feature - US2 (T025)
 *
 * Hook for lawyer's client management.
 */

import { useState, useEffect, useCallback } from 'react';
import { getClients, getClientDetail } from '@/lib/api/clients';
import type {
  ClientItem,
  ClientFilter,
  ClientDetail,
} from '@/types/client';

interface UseClientsOptions {
  initialFilters?: ClientFilter;
  autoFetch?: boolean;
}

interface UseClientsReturn {
  clients: ClientItem[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  filters: ClientFilter;
  setFilters: (filters: ClientFilter) => void;
  setPage: (page: number) => void;
  refetch: () => Promise<void>;
  getDetail: (clientId: string) => Promise<ClientDetail | null>;
}

export function useClients(options: UseClientsOptions = {}): UseClientsReturn {
  const { initialFilters = {}, autoFetch = true } = options;

  const [clients, setClients] = useState<ClientItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(initialFilters.page ?? 1);
  const [pageSize] = useState(initialFilters.page_size ?? 20);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<ClientFilter>(initialFilters);

  const fetchClients = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const { data, error: apiError } = await getClients({
        ...filters,
        page,
        page_size: pageSize,
      });

      if (apiError) {
        setError(apiError);
        setClients([]);
        setTotal(0);
        setTotalPages(0);
      } else if (data) {
        setClients(data.items);
        setTotal(data.total);
        setTotalPages(data.total_pages);
      }
    } catch {
      setError('의뢰인 목록을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => {
    if (autoFetch) {
      fetchClients();
    }
  }, [fetchClients, autoFetch]);

  const handleSetFilters = useCallback((newFilters: ClientFilter) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  }, []);

  const getDetail = useCallback(async (clientId: string): Promise<ClientDetail | null> => {
    try {
      const { data, error: apiError } = await getClientDetail(clientId);

      if (apiError || !data) {
        setError(apiError || '의뢰인 정보를 불러올 수 없습니다.');
        return null;
      }

      return data;
    } catch {
      setError('의뢰인 정보를 불러오는 중 오류가 발생했습니다.');
      return null;
    }
  }, []);

  return {
    clients,
    total,
    page,
    pageSize,
    totalPages,
    isLoading,
    error,
    filters,
    setFilters: handleSetFilters,
    setPage,
    refetch: fetchClients,
    getDetail,
  };
}

// Helper function to get status badge style
export function getClientStatusStyle(status: string): string {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-700';
    case 'inactive':
      return 'bg-gray-100 text-gray-700';
    default:
      return 'bg-gray-100 text-gray-700';
  }
}

// Helper function to get status label in Korean
export function getClientStatusLabel(status: string): string {
  switch (status) {
    case 'active':
      return '활성';
    case 'inactive':
      return '비활성';
    default:
      return status;
  }
}
