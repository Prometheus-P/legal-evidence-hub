/**
 * useCaseDetail Hook Tests
 * Tests for case detail fetching with role-based API paths
 *
 * Covers:
 * - Data fetching and loading states
 * - Role-based API path selection
 * - Error handling
 * - Authentication redirects
 * - Refetch functionality
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useCaseDetail } from '@/hooks/useCaseDetail';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock the API client
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

// Mock the case detail mapper
jest.mock('@/lib/utils/caseDetailMapper', () => ({
  mapApiCaseDetailToCaseDetail: jest.fn((data) => ({
    id: data.id,
    title: data.title,
    description: data.description,
    status: data.status,
    createdAt: data.created_at,
    updatedAt: data.updated_at,
  })),
}));

import { apiClient } from '@/lib/api/client';
import { mapApiCaseDetailToCaseDetail } from '@/lib/utils/caseDetailMapper';

const mockApiGet = apiClient.get as jest.Mock;
const mockMapper = mapApiCaseDetailToCaseDetail as jest.Mock;

// Sample API response
const mockApiResponse = {
  id: 'case-123',
  title: '김OO vs 이OO 이혼 소송',
  description: '테스트 케이스입니다.',
  status: 'in_progress',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

describe('useCaseDetail', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockMapper.mockImplementation((data) => ({
      id: data.id,
      title: data.title,
      description: data.description,
      status: data.status,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
    }));
  });

  describe('Initial State and Loading', () => {
    it('starts with loading state', () => {
      mockApiGet.mockImplementation(() => new Promise(() => {})); // Never resolves

      const { result } = renderHook(() => useCaseDetail('case-123'));

      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeNull();
    });

    it('handles null caseId gracefully', async () => {
      const { result } = renderHook(() => useCaseDetail(null));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiGet).not.toHaveBeenCalled();
      expect(result.current.data).toBeNull();
    });
  });

  describe('Successful Data Fetching', () => {
    it('fetches case detail successfully', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-123');
      expect(result.current.data).toEqual({
        id: 'case-123',
        title: '김OO vs 이OO 이혼 소송',
        description: '테스트 케이스입니다.',
        status: 'in_progress',
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-15T00:00:00Z',
      });
      expect(result.current.error).toBeNull();
    });

    it('maps API response through mapper', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockMapper).toHaveBeenCalledWith(mockApiResponse);
    });
  });

  describe('Role-based API Paths', () => {
    it('uses /lawyer path by default', async () => {
      mockApiGet.mockResolvedValue({ data: mockApiResponse, status: 200 });

      renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-123');
      });
    });

    it('uses /client path when specified', async () => {
      mockApiGet.mockResolvedValue({ data: mockApiResponse, status: 200 });

      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/client' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/client/cases/case-123');
      });
    });

    it('uses /detective path when specified', async () => {
      mockApiGet.mockResolvedValue({ data: mockApiResponse, status: 200 });

      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/detective' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/detective/cases/case-123');
      });
    });

    it('uses /staff path when specified', async () => {
      mockApiGet.mockResolvedValue({ data: mockApiResponse, status: 200 });

      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/staff' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/staff/cases/case-123');
      });
    });
  });

  describe('Error Handling', () => {
    it('handles API error response', async () => {
      mockApiGet.mockResolvedValue({
        error: '케이스를 찾을 수 없습니다.',
        status: 404,
        data: null,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('케이스를 찾을 수 없습니다.');
      expect(result.current.data).toBeNull();
    });

    it('handles API exception', async () => {
      mockApiGet.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.data).toBeNull();
    });

    it('handles non-Error exceptions', async () => {
      mockApiGet.mockRejectedValue('String error');

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('오류가 발생했습니다.');
    });

    it('uses default error message when API error is empty', async () => {
      mockApiGet.mockResolvedValue({
        error: '',
        status: 500,
        data: null,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('케이스 정보를 불러오는데 실패했습니다.');
    });
  });

  describe('Authentication Handling', () => {
    it('redirects to login on 401 response', async () => {
      mockApiGet.mockResolvedValue({
        error: 'Unauthorized',
        status: 401,
        data: null,
      });

      renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });

    it('does not set error on 401 redirect', async () => {
      mockApiGet.mockResolvedValue({
        error: 'Unauthorized',
        status: 401,
        data: null,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login');
      });

      // Error should not be set since we're redirecting
      expect(result.current.error).toBeNull();
    });
  });

  describe('Refetch Functionality', () => {
    it('provides refetch function', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(typeof result.current.refetch).toBe('function');
    });

    it('refetch fetches data again', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiGet).toHaveBeenCalledTimes(1);

      // Update mock response
      const updatedResponse = {
        ...mockApiResponse,
        title: 'Updated Title',
      };
      mockApiGet.mockResolvedValue({
        data: updatedResponse,
        status: 200,
      });

      await act(async () => {
        await result.current.refetch();
      });

      expect(mockApiGet).toHaveBeenCalledTimes(2);
      expect(result.current.data?.title).toBe('Updated Title');
    });

    it('refetch clears previous error', async () => {
      // First call fails
      mockApiGet.mockResolvedValueOnce({
        error: 'Server error',
        status: 500,
        data: null,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.error).toBe('Server error');
      });

      // Second call succeeds
      mockApiGet.mockResolvedValueOnce({
        data: mockApiResponse,
        status: 200,
      });

      await act(async () => {
        await result.current.refetch();
      });

      expect(result.current.error).toBeNull();
      expect(result.current.data).not.toBeNull();
    });
  });

  describe('CaseId Changes', () => {
    it('refetches when caseId changes', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { result, rerender } = renderHook(
        ({ caseId }) => useCaseDetail(caseId),
        { initialProps: { caseId: 'case-1' } }
      );

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-1');

      // Change caseId
      rerender({ caseId: 'case-2' });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-2');
      });
    });

    it('refetches when apiBasePath changes', async () => {
      mockApiGet.mockResolvedValue({
        data: mockApiResponse,
        status: 200,
      });

      const { rerender } = renderHook(
        ({ caseId, apiBasePath }) => useCaseDetail(caseId, { apiBasePath }),
        { initialProps: { caseId: 'case-123', apiBasePath: '/lawyer' as const } }
      );

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-123');
      });

      // Change apiBasePath
      rerender({ caseId: 'case-123', apiBasePath: '/client' as const });

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/client/cases/case-123');
      });
    });
  });

  describe('Cleanup on Unmount', () => {
    it('does not update state after unmount', async () => {
      let resolvePromise: (value: unknown) => void;
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockApiGet.mockReturnValue(pendingPromise);

      const { result, unmount } = renderHook(() => useCaseDetail('case-123'));

      expect(result.current.isLoading).toBe(true);

      // Unmount before promise resolves
      unmount();

      // Resolve the promise after unmount
      await act(async () => {
        resolvePromise!({
          data: mockApiResponse,
          status: 200,
        });
      });

      // No error should be thrown - cleanup should prevent state updates
      // This test primarily ensures no console errors about unmounted components
    });
  });
});
