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

// ============== Detective Contact CRUD (US2 - Lawyer Portal) ==============

import type {
  DetectiveContact,
  DetectiveContactCreate,
  DetectiveContactUpdate,
  DetectiveContactListResponse,
  DetectiveContactQueryParams,
} from '@/types/investigator';

const DETECTIVE_CONTACTS_PATH = '/detectives';

/**
 * Get list of detective contacts
 */
export async function getDetectiveContacts(
  params?: DetectiveContactQueryParams
): Promise<ApiResponse<DetectiveContactListResponse>> {
  const searchParams = new URLSearchParams();

  if (params?.search) {
    searchParams.append('search', params.search);
  }
  if (params?.page) {
    searchParams.append('page', String(params.page));
  }
  if (params?.limit) {
    searchParams.append('limit', String(params.limit));
  }

  const queryString = searchParams.toString();
  const url = queryString ? `${DETECTIVE_CONTACTS_PATH}?${queryString}` : DETECTIVE_CONTACTS_PATH;

  return apiClient.get<DetectiveContactListResponse>(url);
}

/**
 * Get a single detective contact by ID
 */
export async function getDetectiveContact(
  detectiveId: string
): Promise<ApiResponse<DetectiveContact>> {
  return apiClient.get<DetectiveContact>(`${DETECTIVE_CONTACTS_PATH}/${detectiveId}`);
}

/**
 * Create a new detective contact
 */
export async function createDetectiveContact(
  data: DetectiveContactCreate
): Promise<ApiResponse<DetectiveContact>> {
  return apiClient.post<DetectiveContact>(DETECTIVE_CONTACTS_PATH, data);
}

/**
 * Update an existing detective contact
 */
export async function updateDetectiveContact(
  detectiveId: string,
  data: DetectiveContactUpdate
): Promise<ApiResponse<DetectiveContact>> {
  return apiClient.patch<DetectiveContact>(`${DETECTIVE_CONTACTS_PATH}/${detectiveId}`, data);
}

/**
 * Delete a detective contact
 */
export async function deleteDetectiveContact(
  detectiveId: string
): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.delete<{ success: boolean }>(`${DETECTIVE_CONTACTS_PATH}/${detectiveId}`);
}

// Re-export contact types
export type {
  DetectiveContact,
  DetectiveContactCreate,
  DetectiveContactUpdate,
  DetectiveContactListResponse,
  DetectiveContactQueryParams,
};
