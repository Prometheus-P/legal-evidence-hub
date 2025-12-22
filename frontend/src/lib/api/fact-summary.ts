/**
 * Fact Summary API Client
 * 사건 전체 사실관계 요약 API
 * Feature: 014-case-fact-summary
 */

import { apiRequest, ApiResponse } from './client';
import {
  FactSummary,
  FactSummaryGenerateRequest,
  FactSummaryGenerateResponse,
  FactSummaryUpdateRequest,
  FactSummaryUpdateResponse,
} from '@/types/fact-summary';

/**
 * 사실관계 조회 (GET /cases/{case_id}/fact-summary)
 * T014: 저장된 사실관계 조회
 */
export async function getFactSummary(
  caseId: string
): Promise<ApiResponse<FactSummary>> {
  return apiRequest<FactSummary>(`/cases/${caseId}/fact-summary`, {
    method: 'GET',
  });
}

/**
 * 사실관계 생성 (POST /cases/{case_id}/fact-summary/generate)
 * T013: AI 기반 사실관계 자동 생성
 * T032: API Gateway 30초 타임아웃 대응
 */
export async function generateFactSummary(
  caseId: string,
  request: FactSummaryGenerateRequest = {}
): Promise<ApiResponse<FactSummaryGenerateResponse>> {
  // T032: AbortController for 30s timeout (API Gateway limit)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await apiRequest<FactSummaryGenerateResponse>(
      `/cases/${caseId}/fact-summary/generate`,
      {
        method: 'POST',
        body: JSON.stringify({
          force_regenerate: request.force_regenerate ?? false,
        }),
        signal: controller.signal,
      }
    );
    return response;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return {
        error: '요청 시간이 초과되었습니다. 증거가 많은 경우 시간이 더 걸릴 수 있습니다. 잠시 후 다시 시도해 주세요.',
        status: 408,
      };
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * 사실관계 수정 (PATCH /cases/{case_id}/fact-summary)
 * T019: 변호사 수정 사실관계 저장
 */
export async function updateFactSummary(
  caseId: string,
  request: FactSummaryUpdateRequest
): Promise<ApiResponse<FactSummaryUpdateResponse>> {
  return apiRequest<FactSummaryUpdateResponse>(`/cases/${caseId}/fact-summary`, {
    method: 'PATCH',
    body: JSON.stringify(request),
  });
}
