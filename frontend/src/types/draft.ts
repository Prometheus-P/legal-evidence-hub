export interface DraftCitation {
    evidenceId: string;
    title: string;
    quote: string;
}

/**
 * 판례 인용 스키마 (012-precedent-integration: T035)
 */
export interface PrecedentCitation {
    case_ref: string;  // 사건번호 (예: 2020다12345)
    court: string;  // 법원명
    decision_date: string;  // 선고일 (ISO 8601)
    summary: string;  // 판결 요지
    key_factors: string[];  // 주요 요인
    similarity_score: number;  // 유사도 점수
    source_url?: string;  // 국가법령정보센터 원문 링크
}

export interface DraftPreviewState {
    draftText: string;
    citations: DraftCitation[];
    precedent_citations?: PrecedentCitation[];  // 012-precedent-integration: T035
}

export interface DraftTemplate {
    id: string;
    name: string;
    updatedAt: string;
}
