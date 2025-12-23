/**
 * Consultation API Client
 * Issue #399: 상담내역 API
 */

import { apiRequest, ApiResponse } from './client';
import type {
  Consultation,
  ConsultationCreate,
  ConsultationUpdate,
  ConsultationListResponse,
  LinkEvidenceRequest,
  LinkEvidenceResponse,
} from '@/types/consultation';

/**
 * Create a new consultation
 */
export async function createConsultation(
  caseId: string,
  data: ConsultationCreate
): Promise<ApiResponse<Consultation>> {
  return apiRequest<Consultation>(`/cases/${caseId}/consultations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

/**
 * Get list of consultations for a case
 */
export async function getConsultations(
  caseId: string,
  params?: { limit?: number; offset?: number }
): Promise<ApiResponse<ConsultationListResponse>> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.append('limit', params.limit.toString());
  if (params?.offset) searchParams.append('offset', params.offset.toString());

  const queryString = searchParams.toString();
  const url = `/cases/${caseId}/consultations${queryString ? `?${queryString}` : ''}`;

  return apiRequest<ConsultationListResponse>(url, {
    method: 'GET',
  });
}

/**
 * Get a single consultation by ID
 */
export async function getConsultation(
  caseId: string,
  consultationId: string
): Promise<ApiResponse<Consultation>> {
  return apiRequest<Consultation>(`/cases/${caseId}/consultations/${consultationId}`, {
    method: 'GET',
  });
}

/**
 * Update a consultation
 */
export async function updateConsultation(
  caseId: string,
  consultationId: string,
  data: ConsultationUpdate
): Promise<ApiResponse<Consultation>> {
  return apiRequest<Consultation>(`/cases/${caseId}/consultations/${consultationId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

/**
 * Delete a consultation
 */
export async function deleteConsultation(
  caseId: string,
  consultationId: string
): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/cases/${caseId}/consultations/${consultationId}`, {
    method: 'DELETE',
  });
}

/**
 * Link evidence to a consultation
 */
export async function linkEvidence(
  caseId: string,
  consultationId: string,
  evidenceIds: string[]
): Promise<ApiResponse<LinkEvidenceResponse>> {
  const data: LinkEvidenceRequest = { evidence_ids: evidenceIds };

  return apiRequest<LinkEvidenceResponse>(
    `/cases/${caseId}/consultations/${consultationId}/evidence`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }
  );
}

/**
 * Unlink evidence from a consultation
 */
export async function unlinkEvidence(
  caseId: string,
  consultationId: string,
  evidenceId: string
): Promise<ApiResponse<void>> {
  return apiRequest<void>(
    `/cases/${caseId}/consultations/${consultationId}/evidence/${evidenceId}`,
    {
      method: 'DELETE',
    }
  );
}
