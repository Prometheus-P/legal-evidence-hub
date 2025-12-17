/**
 * Search types for LEH Lawyer Portal v1
 * User Story 6: Global Search
 */

export type SearchCategory = 'cases' | 'clients' | 'evidence' | 'events';

export interface SearchResultItem {
  category: SearchCategory;
  id: string;
  title: string;
  subtitle: string | null;
  icon: string;
  url: string | null;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  results: SearchResultItem[];
  total: number;
  query: string;
}

export interface QuickAccessEvent {
  id: string;
  title: string;
  time: string;
  case_id: string | null;
}

export interface QuickAccessResponse {
  todays_events: QuickAccessEvent[];
  todays_events_count: number;
}

export interface RecentSearchesResponse {
  recent_searches: string[];
}

// Category display configuration
export const CATEGORY_CONFIG: Record<SearchCategory, {
  label: string;
  icon: string;
  color: string;
}> = {
  cases: {
    label: '사건',
    icon: '📁',
    color: 'text-blue-600',
  },
  clients: {
    label: '의뢰인',
    icon: '👤',
    color: 'text-green-600',
  },
  evidence: {
    label: '증거',
    icon: '📎',
    color: 'text-amber-600',
  },
  events: {
    label: '일정',
    icon: '📅',
    color: 'text-purple-600',
  },
};
