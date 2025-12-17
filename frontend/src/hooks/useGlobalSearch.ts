/**
 * useGlobalSearch hook for LEH Lawyer Portal v1
 * User Story 6: Global Search
 */

'use client';
import { logger } from '@/lib/logger';

import { useState, useCallback, useEffect, useRef } from 'react';
import type { SearchResultItem, SearchCategory, QuickAccessEvent } from '@/types/search';
import { search, getQuickAccess, getRecentSearches } from '@/lib/api/search';

interface UseGlobalSearchOptions {
  debounceMs?: number;
  minQueryLength?: number;
}

interface UseGlobalSearchReturn {
  query: string;
  setQuery: (query: string) => void;
  results: SearchResultItem[];
  isLoading: boolean;
  error: string | null;
  quickAccess: {
    todaysEvents: QuickAccessEvent[];
    recentSearches: string[];
  };
  isLoadingQuickAccess: boolean;
  searchByCategory: (category: SearchCategory) => SearchResultItem[];
  clearResults: () => void;
  executeSearch: (searchQuery?: string) => Promise<void>;
}

export function useGlobalSearch(options?: UseGlobalSearchOptions): UseGlobalSearchReturn {
  const { debounceMs = 300, minQueryLength = 2 } = options || {};

  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quickAccess, setQuickAccess] = useState<{
    todaysEvents: QuickAccessEvent[];
    recentSearches: string[];
  }>({ todaysEvents: [], recentSearches: [] });
  const [isLoadingQuickAccess, setIsLoadingQuickAccess] = useState(false);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Load quick access data on mount
  useEffect(() => {
    const loadQuickAccess = async () => {
      setIsLoadingQuickAccess(true);
      try {
        const [quickAccessData, recentSearchesData] = await Promise.all([
          getQuickAccess(),
          getRecentSearches(),
        ]);
        setQuickAccess({
          todaysEvents: quickAccessData.todays_events,
          recentSearches: recentSearchesData,
        });
      } catch {
        // Quick access is optional, don't show error
        logger.error('Failed to load quick access data');
      } finally {
        setIsLoadingQuickAccess(false);
      }
    };

    loadQuickAccess();
  }, []);

  // Execute search
  const executeSearch = useCallback(
    async (searchQuery?: string) => {
      const q = searchQuery ?? query;

      if (q.length < minQueryLength) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await search(q);
        setResults(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : '검색에 실패했습니다.');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    },
    [query, minQueryLength]
  );

  // Debounced search on query change
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (query.length < minQueryLength) {
      setResults([]);
      return;
    }

    debounceTimerRef.current = setTimeout(() => {
      executeSearch(query);
    }, debounceMs);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, debounceMs, minQueryLength, executeSearch]);

  // Filter results by category
  const searchByCategory = useCallback(
    (category: SearchCategory) => results.filter((r) => r.category === category),
    [results]
  );

  // Clear results
  const clearResults = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
  }, []);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
    quickAccess,
    isLoadingQuickAccess,
    searchByCategory,
    clearResults,
    executeSearch,
  };
}
