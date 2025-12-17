/**
 * Procedure API Client
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 */

import { apiRequest, ApiResponse } from './client';
import type {
  ProcedureStage,
  ProcedureStageCreate,
  ProcedureStageUpdate,
  ProcedureTimelineResponse,
  TransitionToNextStage,
  TransitionResponse,
  NextStageOption,
  UpcomingDeadlinesResponse,
} from '@/types/procedure';

/**
 * Get procedure timeline for a case
 */
export async function getProcedureTimeline(
  caseId: string
): Promise<ApiResponse<ProcedureTimelineResponse>> {
  return apiRequest<ProcedureTimelineResponse>(`/cases/${caseId}/procedure`, {
    method: 'GET',
  });
}

/**
 * Initialize procedure timeline for a case
 * Creates all stages in pending status
 */
export async function initializeProcedureTimeline(
  caseId: string,
  startFiled: boolean = true
): Promise<ApiResponse<ProcedureTimelineResponse>> {
  const params = startFiled ? '?start_filed=true' : '?start_filed=false';
  return apiRequest<ProcedureTimelineResponse>(`/cases/${caseId}/procedure/initialize${params}`, {
    method: 'POST',
  });
}

/**
 * Create a new procedure stage
 */
export async function createProcedureStage(
  caseId: string,
  data: ProcedureStageCreate
): Promise<ApiResponse<ProcedureStage>> {
  return apiRequest<ProcedureStage>(`/cases/${caseId}/procedure/stages`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get a specific procedure stage
 */
export async function getProcedureStage(
  caseId: string,
  stageId: string
): Promise<ApiResponse<ProcedureStage>> {
  return apiRequest<ProcedureStage>(`/cases/${caseId}/procedure/stages/${stageId}`, {
    method: 'GET',
  });
}

/**
 * Update a procedure stage
 */
export async function updateProcedureStage(
  caseId: string,
  stageId: string,
  data: ProcedureStageUpdate
): Promise<ApiResponse<ProcedureStage>> {
  return apiRequest<ProcedureStage>(`/cases/${caseId}/procedure/stages/${stageId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a procedure stage
 */
export async function deleteProcedureStage(
  caseId: string,
  stageId: string
): Promise<ApiResponse<void>> {
  return apiRequest<void>(`/cases/${caseId}/procedure/stages/${stageId}`, {
    method: 'DELETE',
  });
}

/**
 * Mark a procedure stage as completed
 */
export async function completeProcedureStage(
  caseId: string,
  stageId: string,
  outcome?: string
): Promise<ApiResponse<ProcedureStage>> {
  const params = outcome ? `?outcome=${encodeURIComponent(outcome)}` : '';
  return apiRequest<ProcedureStage>(`/cases/${caseId}/procedure/stages/${stageId}/complete${params}`, {
    method: 'POST',
  });
}

/**
 * Skip a procedure stage
 */
export async function skipProcedureStage(
  caseId: string,
  stageId: string,
  reason?: string
): Promise<ApiResponse<ProcedureStage>> {
  const params = reason ? `?reason=${encodeURIComponent(reason)}` : '';
  return apiRequest<ProcedureStage>(`/cases/${caseId}/procedure/stages/${stageId}/skip${params}`, {
    method: 'POST',
  });
}

/**
 * Transition to the next procedure stage
 */
export async function transitionToNextStage(
  caseId: string,
  data: TransitionToNextStage
): Promise<ApiResponse<TransitionResponse>> {
  return apiRequest<TransitionResponse>(`/cases/${caseId}/procedure/transition`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Get valid next stages from current position
 */
export async function getValidNextStages(
  caseId: string
): Promise<ApiResponse<NextStageOption[]>> {
  return apiRequest<NextStageOption[]>(`/cases/${caseId}/procedure/next-stages`, {
    method: 'GET',
  });
}

/**
 * Get upcoming procedure deadlines
 */
export async function getUpcomingDeadlines(
  daysAhead: number = 7
): Promise<ApiResponse<UpcomingDeadlinesResponse>> {
  return apiRequest<UpcomingDeadlinesResponse>(`/procedure/deadlines?days_ahead=${daysAhead}`, {
    method: 'GET',
  });
}
