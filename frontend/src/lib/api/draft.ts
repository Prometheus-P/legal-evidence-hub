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

export interface DraftPreviewRequest {
  sections?: string[];
  language?: string;
  style?: string;
}

export interface DraftPreviewResponse {
  case_id: string;
  draft_text: string;
  citations: DraftCitation[];
  generated_at: string;
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
