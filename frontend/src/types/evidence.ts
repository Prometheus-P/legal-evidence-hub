export type EvidenceType = 'text' | 'image' | 'audio' | 'video' | 'pdf';
export type EvidenceStatus = 'uploading' | 'queued' | 'processing' | 'review_needed' | 'completed' | 'failed';
export type SpeakerType = '원고' | '피고' | '제3자' | 'unknown';

/**
 * 민법 840조 이혼 사유 카테고리
 * Korean Civil Code Article 840 - Grounds for Divorce
 */
export type Article840Category =
    | 'adultery'                  // 제1호: 배우자의 부정행위
    | 'desertion'                 // 제2호: 악의의 유기
    | 'mistreatment_by_inlaws'    // 제3호: 배우자 직계존속의 부당대우
    | 'harm_to_own_parents'       // 제4호: 자기 직계존속 피해
    | 'unknown_whereabouts'       // 제5호: 생사불명 3년
    | 'irreconcilable_differences' // 제6호: 혼인 지속 곤란사유
    | 'general';                  // 일반 증거

/**
 * Article 840 태깅 결과
 */
export interface Article840Tags {
    categories: Article840Category[];
    confidence: number; // 0.0 ~ 1.0
    matchedKeywords: string[];
}

/**
 * AI 분석 인사이트
 */
export interface AIInsight {
    id: string;
    evidenceId: string;
    type: 'summary' | 'legal_relevance' | 'risk_factor' | 'recommendation';
    title: string;
    content: string;
    confidence: number;
    createdAt: string;
}

/**
 * 015-evidence-speaker-mapping: 개별 화자 매핑 항목
 */
export interface SpeakerMappingItem {
    party_id: string;
    party_name: string;
}

/**
 * 015-evidence-speaker-mapping: 화자 매핑 객체 (화자명 → 인물 정보)
 */
export type SpeakerMapping = Record<string, SpeakerMappingItem>;

/**
 * 015-evidence-speaker-mapping: 화자 매핑 업데이트 요청
 */
export interface SpeakerMappingUpdateRequest {
    speaker_mapping: SpeakerMapping;
}

/**
 * 015-evidence-speaker-mapping: 화자 매핑 업데이트 응답
 */
export interface SpeakerMappingUpdateResponse {
    evidence_id: string;
    speaker_mapping: SpeakerMapping | null;
    updated_at: string | null;
    updated_by: string | null;
}

export interface Evidence {
    id: string;
    caseId: string;
    filename: string;
    type: EvidenceType;
    status: EvidenceStatus;
    uploadDate: string; // ISO Date string
    summary?: string;
    size: number;
    downloadUrl?: string;
    content?: string; // STT/OCR 원문 텍스트

    // AI Worker generated fields (optional - populated after processing)
    speaker?: SpeakerType;
    labels?: string[]; // AI-generated labels (e.g., '폭언', '불륜', '유책사유')
    timestamp?: string; // ISO Date string - when the evidence was created/recorded
    s3Key?: string; // S3 storage path
    qdrantId?: string; // Vector store ID for RAG

    // Article 840 analysis (optional - populated after AI processing)
    article840Tags?: Article840Tags;
    insights?: AIInsight[];

    // 014-ui-settings-completion: Legal evidence numbering
    legalNumber?: string;  // 갑제1호증, 을제2호증, etc.
    submittedBy?: 'plaintiff' | 'defendant' | 'third_party';  // 갑/을/병
    evidenceTimestamp?: string;  // ISO Date - when evidence was created (not uploaded)

    // 015-evidence-speaker-mapping: 화자 매핑 필드
    speakerMapping?: SpeakerMapping;
    speakerMappingUpdatedAt?: string;
    speakerMappingUpdatedBy?: string;
    hasSpeakerMapping?: boolean; // 목록에서 매핑 상태 표시용
}
