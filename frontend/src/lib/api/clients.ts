/**
 * Clients API Client
 * 005-lawyer-portal-pages Feature - US2
 *
 * API functions for lawyer's client management.
 */

import { apiClient, ApiResponse } from './client';
import {
  ClientItem,
  ClientListResponse,
  ClientFilter,
  ClientDetail,
} from '@/types/client';

/**
 * Get list of lawyer's clients with filters
 */
export async function getClients(
  filters?: ClientFilter
): Promise<ApiResponse<ClientListResponse>> {
  const params = new URLSearchParams();

  if (filters) {
    if (filters.search) params.append('search', filters.search);
    if (filters.status && filters.status !== 'all') params.append('status', filters.status);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);
    if (filters.page) params.append('page', String(filters.page));
    if (filters.page_size) params.append('page_size', String(filters.page_size));
  }

  const queryString = params.toString();
  const url = queryString ? `/lawyer/clients?${queryString}` : '/lawyer/clients';

  return apiClient.get<ClientListResponse>(url);
}

/**
 * Get client details by ID
 */
export async function getClientDetail(
  clientId: string
): Promise<ApiResponse<ClientDetail>> {
  return apiClient.get<ClientDetail>(`/lawyer/clients/${clientId}`);
}

// Re-export types for convenience
export type { ClientItem, ClientListResponse, ClientFilter, ClientDetail };
