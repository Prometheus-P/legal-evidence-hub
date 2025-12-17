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

/**
 * 라인 기반 초안 템플릿 (line-based draft)
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
    template_type?: string;  // default: "이혼소장_라인"
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
