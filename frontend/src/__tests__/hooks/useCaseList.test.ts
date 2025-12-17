/**
 * useCaseList Hook Tests
 * Tests case list fetching, filtering, pagination, sorting, and bulk actions
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useCaseList } from '@/hooks/useCaseList';
import { apiClient } from '@/lib/api/client';

// Mock apiClient
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

const mockApiGet = apiClient.get as jest.Mock;
const mockApiPost = apiClient.post as jest.Mock;

// Helper to create mock case data
const createMockCase = (overrides?: Partial<Record<string, unknown>>) => ({
  id: 'case-1',
  title: 'Test Case',
  client_name: 'Test Client',
  status: 'active',
  description: 'Test description',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
  evidence_count: 5,
  member_count: 2,
  progress: 50,
  days_since_update: 3,
  owner_name: 'Test Lawyer',
  last_activity: '2024-01-15T00:00:00Z',
  ...overrides,
});

// Helper to create mock API response
const createMockListResponse = (
  cases: ReturnType<typeof createMockCase>[] = [],
  overrides?: Partial<Record<string, unknown>>
) => ({
  data: {
    items: cases,
    total: cases.length,
    page: 1,
    page_size: 20,
    total_pages: 1,
    status_counts: { active: cases.length },
    ...overrides,
  },
});

describe('useCaseList Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State and Data Fetching', () => {
    it('starts with loading state', async () => {
      // Never resolve to keep loading state
      mockApiGet.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() => useCaseList());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.cases).toEqual([]);
      expect(result.current.error).toBeNull();
    });

    it('fetches cases on mount and transforms response', async () => {
      const mockCases = [
        createMockCase({ id: 'case-1', title: 'Case 1' }),
        createMockCase({ id: 'case-2', title: 'Case 2' }),
      ];

      mockApiGet.mockResolvedValue(createMockListResponse(mockCases));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.cases).toHaveLength(2);
      expect(result.current.cases[0].id).toBe('case-1');
      expect(result.current.cases[0].title).toBe('Case 1');
      // Check field transformation (snake_case to camelCase)
      expect(result.current.cases[0].clientName).toBe('Test Client');
      expect(result.current.cases[0].evidenceCount).toBe(5);
      expect(result.current.cases[0].daysSinceUpdate).toBe(3);
      expect(result.current.error).toBeNull();
    });

    it('sets pagination state from response', async () => {
      const mockCases = [createMockCase()];
      const response = createMockListResponse(mockCases, {
        total: 50,
        page: 1,
        page_size: 20,
        total_pages: 3,
      });

      mockApiGet.mockResolvedValue(response);

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.pagination.total).toBe(50);
      expect(result.current.pagination.totalPages).toBe(3);
    });

    it('sets status counts from response', async () => {
      const response = createMockListResponse([createMockCase()], {
        status_counts: { active: 10, closed: 5, pending: 3 },
      });

      mockApiGet.mockResolvedValue(response);

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.statusCounts).toEqual({
        active: 10,
        closed: 5,
        pending: 3,
      });
    });

    it('handles API error', async () => {
      mockApiGet.mockResolvedValue({
        error: '케이스 목록을 불러오는데 실패했습니다.',
        status: 500,
      });

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.cases).toEqual([]);
      expect(result.current.error).toBe('케이스 목록을 불러오는데 실패했습니다.');
    });

    it('handles network error', async () => {
      mockApiGet.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.cases).toEqual([]);
      expect(result.current.error).toBe('Network error');
    });

    it('handles null/undefined values in response gracefully', async () => {
      const mockCase = {
        id: 'case-1',
        title: 'Minimal Case',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
        // Missing optional fields
      };

      mockApiGet.mockResolvedValue(createMockListResponse([mockCase]));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Should default to 0 for missing numeric fields
      expect(result.current.cases[0].evidenceCount).toBe(0);
      expect(result.current.cases[0].memberCount).toBe(0);
      expect(result.current.cases[0].progress).toBe(0);
      expect(result.current.cases[0].daysSinceUpdate).toBe(0);
    });
  });

  describe('Pagination', () => {
    beforeEach(() => {
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));
    });

    it('changes page and refetches', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      mockApiGet.mockClear();

      act(() => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('page=2')
      );
    });

    it('changes page size, resets to page 1, and refetches', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // First change to page 2
      act(() => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        expect(result.current.pagination.page).toBe(2);
      });

      mockApiGet.mockClear();

      // Then change page size - should reset to page 1
      act(() => {
        result.current.setPageSize(50);
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('page_size=50')
      );
      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('page=1')
      );
    });

    it('clears selection when changing page', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1', 'case-2']);
      });

      expect(result.current.selectedIds).toEqual(['case-1', 'case-2']);

      act(() => {
        result.current.setPage(2);
      });

      expect(result.current.selectedIds).toEqual([]);
    });
  });

  describe('Filtering', () => {
    beforeEach(() => {
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));
    });

    it('applies search filter', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      mockApiGet.mockClear();

      act(() => {
        result.current.setFilters({
          search: 'divorce',
          status: [],
          clientName: '',
        });
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('search=divorce')
      );
    });

    it('applies status filter', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      mockApiGet.mockClear();

      act(() => {
        result.current.setFilters({
          search: '',
          status: ['active', 'pending'],
          clientName: '',
        });
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('status=active')
      );
      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('status=pending')
      );
    });

    it('applies client name filter', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      mockApiGet.mockClear();

      act(() => {
        result.current.setFilters({
          search: '',
          status: [],
          clientName: 'John Doe',
        });
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      // URLSearchParams encodes spaces as '+'
      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('client_name=John+Doe')
      );
    });

    it('resets filters to default', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Apply filters
      act(() => {
        result.current.setFilters({
          search: 'test',
          status: ['active'],
          clientName: 'Client',
        });
      });

      await waitFor(() => {
        expect(result.current.filters.search).toBe('test');
      });

      mockApiGet.mockClear();

      // Reset filters
      act(() => {
        result.current.resetFilters();
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(result.current.filters).toEqual({
        search: '',
        status: [],
        clientName: '',
      });
    });

    it('resets to page 1 when filters change', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Go to page 2
      act(() => {
        result.current.setPage(2);
      });

      await waitFor(() => {
        expect(result.current.pagination.page).toBe(2);
      });

      // Apply filter
      act(() => {
        result.current.setFilters({
          search: 'test',
          status: [],
          clientName: '',
        });
      });

      // Should reset to page 1
      expect(result.current.pagination.page).toBe(1);
    });
  });

  describe('Sorting', () => {
    beforeEach(() => {
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));
    });

    it('applies sort by field', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      mockApiGet.mockClear();

      act(() => {
        result.current.setSort('title');
      });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalled();
      });

      expect(mockApiGet).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=title')
      );
    });

    it('toggles sort order when clicking same field', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Default is 'updated_at' desc
      expect(result.current.sort.sortBy).toBe('updated_at');
      expect(result.current.sort.sortOrder).toBe('desc');

      // Click same field toggles to asc
      act(() => {
        result.current.setSort('updated_at');
      });

      expect(result.current.sort.sortOrder).toBe('asc');

      // Click again toggles back to desc
      act(() => {
        result.current.setSort('updated_at');
      });

      expect(result.current.sort.sortOrder).toBe('desc');
    });

    it('resets to desc when sorting by different field', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Toggle to asc on default field
      act(() => {
        result.current.setSort('updated_at');
      });

      expect(result.current.sort.sortOrder).toBe('asc');

      // Sort by different field - should be desc
      act(() => {
        result.current.setSort('title');
      });

      expect(result.current.sort.sortBy).toBe('title');
      expect(result.current.sort.sortOrder).toBe('desc');
    });
  });

  describe('Selection', () => {
    beforeEach(() => {
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));
    });

    it('sets selected IDs', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1', 'case-2', 'case-3']);
      });

      expect(result.current.selectedIds).toEqual(['case-1', 'case-2', 'case-3']);
    });

    it('clears selection', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1', 'case-2']);
      });

      expect(result.current.selectedIds).toHaveLength(2);

      act(() => {
        result.current.clearSelection();
      });

      expect(result.current.selectedIds).toEqual([]);
    });
  });

  describe('Bulk Actions', () => {
    beforeEach(() => {
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));
    });

    it('executes bulk action and returns results', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Select cases
      act(() => {
        result.current.setSelectedIds(['case-1', 'case-2']);
      });

      mockApiPost.mockResolvedValue({
        data: {
          results: [
            { case_id: 'case-1', success: true, message: 'Archived' },
            { case_id: 'case-2', success: true, message: 'Archived' },
          ],
          successful: 2,
          failed: 0,
          total_requested: 2,
        },
      });

      let actionResults: unknown[];
      await act(async () => {
        actionResults = await result.current.executeBulkAction('archive');
      });

      expect(mockApiPost).toHaveBeenCalledWith('/lawyer/cases/bulk-action', {
        case_ids: ['case-1', 'case-2'],
        action: 'archive',
        params: undefined,
      });

      expect(actionResults!).toHaveLength(2);
      expect(actionResults![0]).toEqual({
        caseId: 'case-1',
        success: true,
        message: 'Archived',
        error: undefined,
      });
    });

    it('passes params to bulk action', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1']);
      });

      mockApiPost.mockResolvedValue({
        data: {
          results: [{ case_id: 'case-1', success: true }],
          successful: 1,
          failed: 0,
          total_requested: 1,
        },
      });

      await act(async () => {
        await result.current.executeBulkAction('change_status', { status: 'closed' });
      });

      expect(mockApiPost).toHaveBeenCalledWith('/lawyer/cases/bulk-action', {
        case_ids: ['case-1'],
        action: 'change_status',
        params: { status: 'closed' },
      });
    });

    it('returns empty array when no cases selected', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // No selection
      expect(result.current.selectedIds).toEqual([]);

      let actionResults: unknown[];
      await act(async () => {
        actionResults = await result.current.executeBulkAction('archive');
      });

      expect(actionResults!).toEqual([]);
      expect(mockApiPost).not.toHaveBeenCalled();
    });

    it('sets bulk action loading state correctly', async () => {
      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1']);
      });

      // Setup mock for bulk action that includes the subsequent refresh
      mockApiPost.mockResolvedValue({
        data: {
          results: [{ case_id: 'case-1', success: true }],
          successful: 1,
          failed: 0,
          total_requested: 1,
        },
      });

      expect(result.current.isBulkActionLoading).toBe(false);

      await act(async () => {
        await result.current.executeBulkAction('archive');
      });

      // After completion, loading should be false
      expect(result.current.isBulkActionLoading).toBe(false);
    });

    it('clears selection after successful bulk action', async () => {
      // Ensure mock is set for both initial load and refresh after bulk action
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1', 'case-2']);
      });

      expect(result.current.selectedIds).toHaveLength(2);

      mockApiPost.mockResolvedValue({
        data: {
          results: [
            { case_id: 'case-1', success: true },
            { case_id: 'case-2', success: true },
          ],
          successful: 2,
          failed: 0,
          total_requested: 2,
        },
      });

      await act(async () => {
        await result.current.executeBulkAction('archive');
      });

      expect(result.current.selectedIds).toEqual([]);
    });

    it('handles bulk action error', async () => {
      // Ensure mock is set for initial load
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setSelectedIds(['case-1']);
      });

      mockApiPost.mockResolvedValue({
        error: '작업 실행에 실패했습니다.',
        status: 500,
      });

      let actionResults: unknown[];
      await act(async () => {
        actionResults = await result.current.executeBulkAction('archive');
      });

      expect(actionResults!).toEqual([]);
      expect(result.current.error).toBe('작업 실행에 실패했습니다.');
    });
  });

  describe('Refresh', () => {
    it('refetches data when refresh is called', async () => {
      // Set up mock response
      mockApiGet.mockResolvedValue(createMockListResponse([createMockCase()]));

      const { result } = renderHook(() => useCaseList());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Initial fetch should have happened
      expect(mockApiGet).toHaveBeenCalled();
      const initialCallCount = mockApiGet.mock.calls.length;

      // Call refresh
      act(() => {
        result.current.refresh();
      });

      // Wait for refresh to complete
      await waitFor(() => {
        expect(mockApiGet.mock.calls.length).toBeGreaterThan(initialCallCount);
      });
    });
  });
});
