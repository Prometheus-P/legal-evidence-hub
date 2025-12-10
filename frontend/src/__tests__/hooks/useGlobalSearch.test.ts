/**
 * useGlobalSearch Hook Tests
 * User Story 6: Global Search
 *
 * Tests for global search functionality.
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useGlobalSearch } from '@/hooks/useGlobalSearch';
import * as searchApi from '@/lib/api/search';

// Mock the search API
jest.mock('@/lib/api/search', () => ({
  search: jest.fn(),
  getQuickAccess: jest.fn(),
  getRecentSearches: jest.fn(),
}));

const mockSearchResults = [
  {
    id: 'case-1',
    category: 'case' as const,
    title: '이혼 소송 - 홍길동',
    description: '서울가정법원 2024가합1234',
    url: '/cases/case-1',
    relevance: 0.95,
  },
  {
    id: 'evidence-1',
    category: 'evidence' as const,
    title: '녹음 파일',
    description: '2024-01-15 통화녹음',
    url: '/cases/case-1/evidence/evidence-1',
    relevance: 0.85,
  },
];

const mockQuickAccess = {
  todays_events: [
    {
      id: 'event-1',
      title: '재판 기일',
      time: '10:00',
      event_type: 'court' as const,
      case_id: 'case-1',
    },
  ],
};

const mockRecentSearches = ['이혼', '양육권', '재산분할'];

describe('useGlobalSearch', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    // Suppress console.error for expected errors
    jest.spyOn(console, 'error').mockImplementation(() => {});

    // Default mock implementations
    (searchApi.getQuickAccess as jest.Mock).mockResolvedValue(mockQuickAccess);
    (searchApi.getRecentSearches as jest.Mock).mockResolvedValue(mockRecentSearches);
  });

  afterEach(() => {
    jest.useRealTimers();
    (console.error as jest.Mock).mockRestore();
  });

  describe('Initial State', () => {
    it('should initialize with empty query and results', () => {
      const { result } = renderHook(() => useGlobalSearch());

      expect(result.current.query).toBe('');
      expect(result.current.results).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should load quick access data on mount', async () => {
      const { result } = renderHook(() => useGlobalSearch());

      await waitFor(() => {
        expect(result.current.isLoadingQuickAccess).toBe(false);
      });

      expect(result.current.quickAccess.todaysEvents).toEqual(mockQuickAccess.todays_events);
      expect(result.current.quickAccess.recentSearches).toEqual(mockRecentSearches);
    });
  });

  describe('Search Execution', () => {
    it('should not search when query is too short', async () => {
      const { result } = renderHook(() => useGlobalSearch({ minQueryLength: 2 }));

      act(() => {
        result.current.setQuery('이');
      });

      // Fast-forward timers
      act(() => {
        jest.advanceTimersByTime(500);
      });

      expect(searchApi.search).not.toHaveBeenCalled();
      expect(result.current.results).toEqual([]);
    });

    it('should search with debounce when query meets minimum length', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch({ debounceMs: 300, minQueryLength: 2 }));

      act(() => {
        result.current.setQuery('이혼');
      });

      // Before debounce
      expect(searchApi.search).not.toHaveBeenCalled();

      // After debounce
      act(() => {
        jest.advanceTimersByTime(300);
      });

      await waitFor(() => {
        expect(searchApi.search).toHaveBeenCalledWith('이혼');
      });

      await waitFor(() => {
        expect(result.current.results).toEqual(mockSearchResults);
      });
    });

    it('should handle search error', async () => {
      (searchApi.search as jest.Mock).mockRejectedValue(new Error('검색 실패'));

      const { result } = renderHook(() => useGlobalSearch({ debounceMs: 100 }));

      act(() => {
        result.current.setQuery('이혼');
      });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(result.current.error).toBe('검색 실패');
      });

      expect(result.current.results).toEqual([]);
    });

    it('should execute search directly with executeSearch', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch());

      await act(async () => {
        await result.current.executeSearch('이혼 소송');
      });

      expect(searchApi.search).toHaveBeenCalledWith('이혼 소송');
      expect(result.current.results).toEqual(mockSearchResults);
    });
  });

  describe('Filter by Category', () => {
    it('should filter results by category', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch());

      await act(async () => {
        await result.current.executeSearch('이혼');
      });

      const caseResults = result.current.searchByCategory('case');
      const evidenceResults = result.current.searchByCategory('evidence');

      expect(caseResults).toHaveLength(1);
      expect(caseResults[0].category).toBe('case');
      expect(evidenceResults).toHaveLength(1);
      expect(evidenceResults[0].category).toBe('evidence');
    });
  });

  describe('Clear Results', () => {
    it('should clear query, results, and error', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch());

      await act(async () => {
        await result.current.executeSearch('이혼');
      });

      expect(result.current.results.length).toBeGreaterThan(0);

      act(() => {
        result.current.clearResults();
      });

      expect(result.current.query).toBe('');
      expect(result.current.results).toEqual([]);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Custom Options', () => {
    it('should use custom debounce time', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch({ debounceMs: 500 }));

      act(() => {
        result.current.setQuery('이혼');
      });

      // At 300ms, search should not have been called yet
      act(() => {
        jest.advanceTimersByTime(300);
      });
      expect(searchApi.search).not.toHaveBeenCalled();

      // At 500ms, search should be called
      act(() => {
        jest.advanceTimersByTime(200);
      });

      await waitFor(() => {
        expect(searchApi.search).toHaveBeenCalled();
      });
    });

    it('should use custom minimum query length', async () => {
      (searchApi.search as jest.Mock).mockResolvedValue({ results: mockSearchResults });

      const { result } = renderHook(() => useGlobalSearch({ minQueryLength: 3, debounceMs: 100 }));

      act(() => {
        result.current.setQuery('이혼');
      });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      // Should not search with 2 characters
      expect(searchApi.search).not.toHaveBeenCalled();

      act(() => {
        result.current.setQuery('이혼소');
      });

      act(() => {
        jest.advanceTimersByTime(100);
      });

      await waitFor(() => {
        expect(searchApi.search).toHaveBeenCalled();
      });
    });
  });
});
