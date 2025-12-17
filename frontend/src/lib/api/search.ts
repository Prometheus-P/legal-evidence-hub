/**
 * Search API client for LEH Lawyer Portal v1
 * User Story 6: Global Search
 */

import { apiClient } from './client';
import type {
  SearchResponse,
  QuickAccessResponse,
  RecentSearchesResponse,
  SearchCategory,
} from '@/types/search';

/**
 * Perform global search across cases, clients, evidence, and events
 */
export async function search(
  query: string,
  categories?: SearchCategory[],
  limit = 20
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });

  if (categories && categories.length > 0) {
    params.set('categories', categories.join(','));
  }

  const response = await apiClient.get<SearchResponse>(`/search?${params.toString()}`);

  if (!response.data) {
    throw new Error(response.error || '검색에 실패했습니다.');
  }

  return response.data;
}

/**
 * Get quick access items (today's events, etc.)
 */
export async function getQuickAccess(): Promise<QuickAccessResponse> {
  const response = await apiClient.get<QuickAccessResponse>('/search/quick-access');

  if (!response.data) {
    throw new Error(response.error || '바로가기 정보를 불러오는데 실패했습니다.');
  }

  return response.data;
}

/**
 * Get recent search history
 */
export async function getRecentSearches(limit = 5): Promise<string[]> {
  const response = await apiClient.get<RecentSearchesResponse>(
    `/search/recent?limit=${limit}`
  );

  if (!response.data) {
    return [];
  }

  return response.data.recent_searches;
}
