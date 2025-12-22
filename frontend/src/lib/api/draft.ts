/**
 * Draft API Client
 * Handles draft generation and export operations
 */

import { apiRequest, ApiResponse } from './client';

export interface DraftCitation {
  evidence_id: string;
  snippet: string;
  labels: string[];
}

/**
 * 판례 인용 정보 (012-precedent-integration)
 */
export interface PrecedentCitation {
  case_ref: string;
  court: string;
  decision_date: string;
  summary: string;
  key_factors: string[];
  similarity_score: number;
  source_url?: string;
}

export interface DraftPreviewRequest {
  sections?: string[];
  language?: string;
  style?: string;
}

export interface DraftPreviewResponse {
  case_id: string;
  draft_text: string;
  citations: DraftCitation[];
  precedent_citations?: PrecedentCitation[];  // 판례 인용 (012-precedent-integration)
  generated_at: string;
  preview_disclaimer?: string;  // 미리보기 면책조항
}

/**
 * Generate draft preview using RAG + GPT-4o
 */
export async function generateDraftPreview(
  caseId: string,
  request: DraftPreviewRequest = {}
): Promise<ApiResponse<DraftPreviewResponse>> {
  return apiRequest<DraftPreviewResponse>(`/cases/${caseId}/draft-preview`, {
    method: 'POST',
    body: JSON.stringify({
      sections: request.sections || ['청구취지', '청구원인'],
      language: request.language || 'ko',
      style: request.style || '법원 제출용_표준',
    }),
  });
}

/**
 * 라인 기반 초안 타입
 */
export interface LineFormatInfo {
  align?: 'left' | 'center' | 'right';
  indent?: number;
  bold?: boolean;
  font_size?: number;
  spacing_before?: number;
  spacing_after?: number;
}

export interface DraftLine {
  line: number;
  text: string;
  section?: string;
  format?: LineFormatInfo;
  is_placeholder?: boolean;
  placeholder_key?: string;
}

export interface LineBasedDraftRequest {
  template_type?: string;
  case_data?: Record<string, string | number | boolean>;
}

export interface LineBasedDraftResponse {
  case_id: string;
  template_type: string;
  generated_at: string;
  lines: DraftLine[];
  text_preview: string;
  preview_disclaimer: string;
}

/**
 * Generate line-based draft preview using court-official template format
 * Returns draft with precise line formatting for legal documents
 */
export async function generateLineBasedDraftPreview(
  caseId: string,
  request: LineBasedDraftRequest = {}
): Promise<ApiResponse<LineBasedDraftResponse>> {
  return apiRequest<LineBasedDraftResponse>(`/cases/${caseId}/draft-preview-lines`, {
    method: 'POST',
    body: JSON.stringify({
      template_type: request.template_type || '이혼소장_라인',
      case_data: request.case_data || {},
    }),
  });
}

// ============================================
// Async Draft Preview (API Gateway 30s timeout 우회)
// ============================================

export type DraftJobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface DraftJobCreateResponse {
  job_id: string;
  case_id: string;
  status: DraftJobStatus;
  message: string;
  created_at: string;
}

export interface DraftJobStatusResponse {
  job_id: string;
  case_id: string;
  status: DraftJobStatus;
  progress: number;
  result?: DraftPreviewResponse;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

/**
 * Start async draft preview generation
 * Returns immediately with job_id for polling
 */
export async function startAsyncDraftPreview(
  caseId: string,
  request: DraftPreviewRequest = {}
): Promise<ApiResponse<DraftJobCreateResponse>> {
  return apiRequest<DraftJobCreateResponse>(`/cases/${caseId}/draft-preview-async`, {
    method: 'POST',
    body: JSON.stringify({
      sections: request.sections || ['청구취지', '청구원인'],
      language: request.language || 'ko',
      style: request.style || '법원 제출용_표준',
    }),
  });
}

/**
 * Get draft job status
 * Poll this endpoint until status is 'completed' or 'failed'
 */
export async function getDraftJobStatus(
  caseId: string,
  jobId: string
): Promise<ApiResponse<DraftJobStatusResponse>> {
  return apiRequest<DraftJobStatusResponse>(`/cases/${caseId}/draft-jobs/${jobId}`, {
    method: 'GET',
  });
}

/**
 * Generate draft preview with async fallback
 * Starts async job and polls until complete
 *
 * @param caseId - Case ID
 * @param request - Draft preview request
 * @param onProgress - Optional callback for progress updates
 * @param maxWaitMs - Maximum wait time in milliseconds (default: 120000 = 2 minutes)
 * @param pollIntervalMs - Poll interval in milliseconds (default: 1500)
 */
export async function generateDraftPreviewAsync(
  caseId: string,
  request: DraftPreviewRequest = {},
  onProgress?: (progress: number, status: DraftJobStatus) => void,
  maxWaitMs: number = 120000,
  pollIntervalMs: number = 1500
): Promise<ApiResponse<DraftPreviewResponse>> {
  // 1. Start async job
  const startResponse = await startAsyncDraftPreview(caseId, request);
  if (startResponse.status >= 400 || !startResponse.data) {
    return {
      status: startResponse.status,
      error: startResponse.error || '초안 생성 시작에 실패했습니다.',
    };
  }

  const jobId = startResponse.data.job_id;
  const startTime = Date.now();

  // 2. Poll for result
  while (Date.now() - startTime < maxWaitMs) {
    await new Promise(resolve => setTimeout(resolve, pollIntervalMs));

    const statusResponse = await getDraftJobStatus(caseId, jobId);
    if (statusResponse.status >= 400 || !statusResponse.data) {
      continue; // Retry on network error
    }

    const { status, progress, result, error_message } = statusResponse.data;

    // Report progress
    if (onProgress) {
      onProgress(progress, status);
    }

    // Check completion
    if (status === 'completed' && result) {
      return {
        status: 200,
        data: result,
      };
    }

    if (status === 'failed') {
      return {
        status: 500,
        error: error_message || '초안 생성에 실패했습니다.',
      };
    }
  }

  // Timeout
  return {
    status: 504,
    error: '초안 생성 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.',
  };
}
