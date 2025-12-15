'use client';

/**
 * useCaseList Hook
 * 003-role-based-ui Feature - US3
 *
 * Hook for managing case list state, filtering, and bulk actions.
 */

import { useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

interface CaseListApiResponse {
  items: Array<{
    id: string;
    title: string;
    client_name?: string;
    status: string;
    description?: string;
    created_at: string;
    updated_at: string;
    evidence_count?: number;
    member_count?: number;
    progress?: number;
    days_since_update?: number;
    owner_name?: string;
    last_activity?: string;
  }>;
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  status_counts?: Record<string, number>;
}

interface BulkActionApiResult {
  case_id: string;
  success: boolean;
  message?: string;
  error?: string;
}

interface BulkActionApiResponse {
  results: BulkActionApiResult[];
  failed: number;
  successful: number;
  total_requested: number;
}

interface CaseItem {
  id: string;
  title: string;
  clientName?: string;
  status: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  evidenceCount: number;
  memberCount: number;
  progress: number;
  daysSinceUpdate: number;
  ownerName?: string;
  lastActivity?: string;
}

interface FilterState {
  search: string;
  status: string[];
  clientName: string;
}

interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

interface SortState {
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

interface BulkActionResult {
  caseId: string;
  success: boolean;
  message?: string;
  error?: string;
}

interface UseCaseListReturn {
  // Data
  cases: CaseItem[];
  isLoading: boolean;
  error: string | null;

  // Pagination
  pagination: PaginationState;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;

  // Filtering
  filters: FilterState;
  statusCounts: Record<string, number>;
  setFilters: (filters: FilterState) => void;
  resetFilters: () => void;

  // Sorting
  sort: SortState;
  setSort: (field: string) => void;

  // Selection
  selectedIds: string[];
  setSelectedIds: (ids: string[]) => void;
  clearSelection: () => void;

  // Tab (active/closed)
  showClosed: boolean;
  setShowClosed: (show: boolean) => void;

  // Actions
  refresh: () => void;
  executeBulkAction: (action: string, params?: Record<string, string>) => Promise<BulkActionResult[]>;
  isBulkActionLoading: boolean;
  permanentDeleteCase: (caseId: string) => Promise<boolean>;
}

const defaultFilters: FilterState = {
  search: '',
  status: [],
  clientName: '',
};

const defaultPagination: PaginationState = {
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0,
};

const defaultSort: SortState = {
  sortBy: 'updated_at',
  sortOrder: 'desc',
};

export function useCaseList(): UseCaseListReturn {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationState>(defaultPagination);
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});
  const [sort, setSortState] = useState<SortState>(defaultSort);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isBulkActionLoading, setIsBulkActionLoading] = useState(false);
  const [showClosed, setShowClosedState] = useState(false);

  const fetchCases = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Build query params
      const params = new URLSearchParams();
      params.append('page', pagination.page.toString());
      params.append('page_size', pagination.pageSize.toString());
      params.append('sort_by', sort.sortBy);
      params.append('sort_order', sort.sortOrder);
      params.append('include_closed', showClosed.toString());

      if (filters.search) {
        params.append('search', filters.search);
      }
      if (filters.clientName) {
        params.append('client_name', filters.clientName);
      }
      filters.status.forEach((s) => {
        params.append('status', s);
      });

      const endpoint = `/lawyer/cases?${params.toString()}`;
      const response = await apiClient.get<CaseListApiResponse>(endpoint);

      if (response.error || !response.data) {
        throw new Error(response.error || '케이스 목록을 불러오는데 실패했습니다.');
      }

      const data = response.data;

      // Map API response to frontend format
      const mappedCases: CaseItem[] = data.items.map((item) => ({
        id: item.id,
        title: item.title,
        clientName: item.client_name,
        status: item.status,
        description: item.description,
        createdAt: item.created_at,
        updatedAt: item.updated_at,
        evidenceCount: item.evidence_count || 0,
        memberCount: item.member_count || 0,
        progress: item.progress || 0,
        daysSinceUpdate: item.days_since_update || 0,
        ownerName: item.owner_name,
        lastActivity: item.last_activity,
      }));

      setCases(mappedCases);
      setPagination((prev) => ({
        ...prev,
        total: data.total,
        totalPages: data.total_pages,
      }));
      setStatusCounts(data.status_counts || {});
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
      setCases([]);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.page, pagination.pageSize, sort.sortBy, sort.sortOrder, filters, showClosed]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }));
    setSelectedIds([]);
  }, []);

  const setPageSize = useCallback((pageSize: number) => {
    setPagination((prev) => ({ ...prev, pageSize, page: 1 }));
    setSelectedIds([]);
  }, []);

  const updateFilters = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
    setPagination((prev) => ({ ...prev, page: 1 }));
    setSelectedIds([]);
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
    setPagination((prev) => ({ ...prev, page: 1 }));
    setSelectedIds([]);
  }, []);

  const setSort = useCallback((field: string) => {
    setSortState((prev) => ({
      sortBy: field,
      sortOrder: prev.sortBy === field && prev.sortOrder === 'desc' ? 'asc' : 'desc',
    }));
    setSelectedIds([]);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedIds([]);
  }, []);

  const refresh = useCallback(() => {
    fetchCases();
  }, [fetchCases]);

  const setShowClosed = useCallback((show: boolean) => {
    setShowClosedState(show);
    setPagination((prev) => ({ ...prev, page: 1 }));
    setSelectedIds([]);
  }, []);

  const permanentDeleteCase = useCallback(async (caseId: string): Promise<boolean> => {
    setError(null);

    try {
      const response = await apiClient.delete(`/cases/${caseId}?permanent=true`);

      if (response.error) {
        throw new Error(response.error || '삭제에 실패했습니다.');
      }

      // Refresh list after deletion
      await fetchCases();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : '삭제 중 오류가 발생했습니다.');
      return false;
    }
  }, [fetchCases]);

  const executeBulkAction = useCallback(
    async (action: string, params?: Record<string, string>): Promise<BulkActionResult[]> => {
      if (selectedIds.length === 0) return [];

      setIsBulkActionLoading(true);
      setError(null);

      try {
        const response = await apiClient.post<BulkActionApiResponse>('/lawyer/cases/bulk-action', {
          case_ids: selectedIds,
          action,
          params,
        });

        if (response.error || !response.data) {
          throw new Error(response.error || '작업 실행에 실패했습니다.');
        }

        const data = response.data;

        // Refresh list after action
        await fetchCases();
        setSelectedIds([]);

        return data.results.map((r: BulkActionApiResult): BulkActionResult => ({
          caseId: r.case_id,
          success: r.success,
          message: r.message,
          error: r.error,
        }));
      } catch (err) {
        setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
        return [];
      } finally {
        setIsBulkActionLoading(false);
      }
    },
    [selectedIds, fetchCases]
  );

  return {
    cases,
    isLoading,
    error,
    pagination,
    setPage,
    setPageSize,
    filters,
    statusCounts,
    setFilters: updateFilters,
    resetFilters,
    sort,
    setSort,
    selectedIds,
    setSelectedIds,
    clearSelection,
    showClosed,
    setShowClosed,
    refresh,
    executeBulkAction,
    isBulkActionLoading,
    permanentDeleteCase,
  };
}

export default useCaseList;
