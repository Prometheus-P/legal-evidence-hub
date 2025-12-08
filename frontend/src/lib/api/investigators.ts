/**
 * Investigators API Client
 * 005-lawyer-portal-pages Feature - US3
 *
 * API functions for lawyer's investigator management.
 */

import { apiClient, ApiResponse } from './client';
import {
  InvestigatorItem,
  InvestigatorListResponse,
  InvestigatorFilter,
  InvestigatorDetail,
} from '@/types/investigator';

/**
 * Get list of investigators assigned to lawyer's cases
 */
export async function getInvestigators(
  filters?: InvestigatorFilter
): Promise<ApiResponse<InvestigatorListResponse>> {
  const params = new URLSearchParams();

  if (filters) {
    if (filters.search) params.append('search', filters.search);
    if (filters.availability && filters.availability !== 'all') {
      params.append('availability', filters.availability);
    }
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);
    if (filters.page) params.append('page', String(filters.page));
    if (filters.page_size) params.append('page_size', String(filters.page_size));
  }

  const queryString = params.toString();
  const url = queryString ? `/lawyer/investigators?${queryString}` : '/lawyer/investigators';

  return apiClient.get<InvestigatorListResponse>(url);
}

/**
 * Get investigator details by ID
 */
export async function getInvestigatorDetail(
  investigatorId: string
): Promise<ApiResponse<InvestigatorDetail>> {
  return apiClient.get<InvestigatorDetail>(`/lawyer/investigators/${investigatorId}`);
}

// Re-export types for convenience
export type {
  InvestigatorItem,
  InvestigatorListResponse,
  InvestigatorFilter,
  InvestigatorDetail,
};
