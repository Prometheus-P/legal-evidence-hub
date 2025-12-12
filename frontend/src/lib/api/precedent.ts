/**
 * Precedent Search API Client
 * 012-precedent-integration: T025
 */

import type { PrecedentSearchResponse, PrecedentSearchOptions } from '@/types/precedent';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || '';

/**
 * 유사 판례 검색 API
 * @param caseId 검색 대상 사건 ID
 * @param options 검색 옵션 (limit, min_score)
 */
export async function searchSimilarPrecedents(
  caseId: string,
  options: PrecedentSearchOptions = {}
): Promise<PrecedentSearchResponse> {
  const { limit = 10, min_score = 0.5 } = options;

  const params = new URLSearchParams({
    limit: limit.toString(),
    min_score: min_score.toString(),
  });

  const response = await fetch(
    `${API_BASE}/api/cases/${caseId}/similar-precedents?${params}`,
    {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('인증이 필요합니다.');
    }
    if (response.status === 403) {
      throw new Error('사건 접근 권한이 없습니다.');
    }
    if (response.status === 404) {
      throw new Error('사건을 찾을 수 없습니다.');
    }
    if (response.status === 503) {
      // Qdrant 연결 실패 시에도 fallback 데이터가 반환됨
      console.warn('Qdrant 연결 실패, fallback 데이터 사용');
    }
    throw new Error(`판례 검색 실패: ${response.statusText}`);
  }

  return response.json();
}
