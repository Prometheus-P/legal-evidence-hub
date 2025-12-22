/**
 * useCaseDetail Hook Tests
 * Tests for case detail fetching with role-based API paths
 *
 * Covers:
 * - Data fetching and loading states
 * - Role-based API path selection
 * - Error handling
 * - Authentication redirects
 */

import { renderHook, waitFor } from '@testing-library/react';
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

const mockApiGet = apiClient.get as jest.Mock;

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
    mockPush.mockClear();
  });

  describe('Initial State', () => {
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

  describe('Role-based API Paths', () => {
    it('uses /lawyer path by default', async () => {
      mockApiGet.mockResolvedValueOnce({ data: mockApiResponse, status: 200 });
      renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/lawyer/cases/case-123');
      });
    });

    it('uses /client path when specified', async () => {
      mockApiGet.mockResolvedValueOnce({ data: mockApiResponse, status: 200 });
      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/client' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/client/cases/case-123');
      });
    });

    it('uses /detective path when specified', async () => {
      mockApiGet.mockResolvedValueOnce({ data: mockApiResponse, status: 200 });
      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/detective' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/detective/cases/case-123');
      });
    });

    it('uses /staff path when specified', async () => {
      mockApiGet.mockResolvedValueOnce({ data: mockApiResponse, status: 200 });
      renderHook(() => useCaseDetail('case-123', { apiBasePath: '/staff' }));

      await waitFor(() => {
        expect(mockApiGet).toHaveBeenCalledWith('/staff/cases/case-123');
      });
    });
  });

  describe('Successful Data Fetching', () => {
    it('fetches case detail and returns data', async () => {
      mockApiGet.mockResolvedValueOnce({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.data).not.toBeNull();
      });

      expect(result.current.data?.id).toBe('case-123');
      expect(result.current.data?.title).toBe('김OO vs 이OO 이혼 소송');
      expect(result.current.error).toBeNull();
    });
  });

  describe('Authentication Handling', () => {
    it('redirects to login on 401 response', async () => {
      mockApiGet.mockResolvedValueOnce({
        error: 'Unauthorized',
        status: 401,
        data: null,
      });

      renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });
  });

  describe('Refetch Functionality', () => {
    it('provides refetch function', async () => {
      mockApiGet.mockResolvedValueOnce({
        data: mockApiResponse,
        status: 200,
      });

      const { result } = renderHook(() => useCaseDetail('case-123'));

      await waitFor(() => {
        expect(result.current.data).not.toBeNull();
      });

      expect(typeof result.current.refetch).toBe('function');
    });
  });
});
