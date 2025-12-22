/**
 * Fact Summary Types
 * 사건 전체 사실관계 요약 관련 타입 정의
 * Feature: 014-case-fact-summary
 */

/**
 * 사실관계 요약 응답 (GET /cases/{case_id}/fact-summary)
 */
export interface FactSummary {
  case_id: string;
  ai_summary: string;
  modified_summary: string | null;
  evidence_ids: string[];
  fault_types: string[];
  created_at: string;
  modified_at: string | null;
  modified_by: string | null;
  has_previous_version: boolean;
}

/**
 * 사실관계 생성 요청 (POST /cases/{case_id}/fact-summary/generate)
 */
export interface FactSummaryGenerateRequest {
  force_regenerate?: boolean;
}

/**
 * 사실관계 생성 응답
 */
export interface FactSummaryGenerateResponse {
  case_id: string;
  ai_summary: string;
  evidence_count: number;
  fault_types: string[];
  generated_at: string;
}

/**
 * 사실관계 수정 요청 (PATCH /cases/{case_id}/fact-summary)
 */
export interface FactSummaryUpdateRequest {
  modified_summary: string;
}

/**
 * 사실관계 수정 응답
 */
export interface FactSummaryUpdateResponse {
  case_id: string;
  modified_summary: string;
  modified_at: string;
  modified_by: string;
}

/**
 * 사실관계 패널 상태
 */
export type FactSummaryPanelState =
  | 'empty'        // 사실관계 없음
  | 'loading'      // 생성 중
  | 'generated'    // AI 생성 완료 (수정 전)
  | 'modified'     // 변호사 수정 완료
  | 'editing'      // 편집 모드
  | 'error';       // 에러 상태

/**
 * 사실관계 편집 상태
 */
export interface FactSummaryEditState {
  content: string;
  isDirty: boolean;
  isSaving: boolean;
}
