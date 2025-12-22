"""
Draft Schemas - Preview, CRUD, Export, Line-based Templates
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# Draft Preview Schemas
# ============================================
class DraftPreviewRequest(BaseModel):
    """Draft preview request schema"""
    sections: list[str] = Field(default=["청구취지", "청구원인"])
    language: str = "ko"
    style: str = "법원 제출용_표준"


class DraftCitation(BaseModel):
    """Draft citation schema"""
    evidence_id: str
    snippet: str
    labels: list[str]


class PrecedentCitation(BaseModel):
    """판례 인용 스키마 (012-precedent-integration: T034)"""
    case_ref: str  # 사건번호 (예: 2020다12345)
    court: str  # 법원명
    decision_date: str  # 선고일 (ISO 8601)
    summary: str  # 판결 요지
    key_factors: list[str] = []  # 주요 요인
    similarity_score: float  # 유사도 점수
    source_url: Optional[str] = None  # 국가법령정보센터 원문 링크


class DraftPreviewResponse(BaseModel):
    """Draft preview response schema"""
    case_id: str
    draft_text: str
    citations: list[DraftCitation]
    precedent_citations: list[PrecedentCitation] = []  # 012-precedent-integration: T034
    generated_at: datetime
    preview_disclaimer: str = "본 문서는 AI가 생성한 미리보기 초안입니다. 법적 효력이 없으며, 변호사의 검토 및 수정이 필수입니다."


class DraftExportFormat(str, Enum):
    """Draft export format options"""
    DOCX = "docx"
    PDF = "pdf"


# ============================================
# Line-Based Draft Schemas (라인별 JSON 템플릿)
# ============================================
class LineBasedDraftRequest(BaseModel):
    """라인 기반 초안 생성 요청 스키마"""
    template_type: str = Field(default="이혼소장_라인", description="사용할 템플릿 타입")
    case_data: dict = Field(default_factory=dict, description="플레이스홀더 채울 데이터 (원고이름, 피고이름 등)")


class LineFormatInfo(BaseModel):
    """라인 포맷 정보"""
    align: Optional[str] = "left"
    indent: Optional[int] = 0
    bold: Optional[bool] = False
    font_size: Optional[int] = 12
    spacing_after: Optional[int] = 0


class DraftLine(BaseModel):
    """초안 라인 스키마"""
    line: int
    text: str
    section: Optional[str] = None
    format: Optional[LineFormatInfo] = None
    is_placeholder: Optional[bool] = False


class LineBasedDraftResponse(BaseModel):
    """라인 기반 초안 응답 스키마"""
    case_id: str
    template_type: str
    generated_at: datetime
    lines: list[dict]  # DraftLine 리스트 (유연한 타입)
    text_preview: str = Field(description="렌더링된 텍스트 미리보기")
    preview_disclaimer: str = "본 문서는 AI가 생성한 미리보기 초안입니다. 법적 효력이 없으며, 변호사의 검토 및 수정이 필수입니다."


# ============================================
# Draft CRUD Schemas
# ============================================
class DraftDocumentType(str, Enum):
    """Draft document type options"""
    COMPLAINT = "complaint"      # 소장
    MOTION = "motion"            # 신청서
    BRIEF = "brief"              # 준비서면
    RESPONSE = "response"        # 답변서


class DraftDocumentStatus(str, Enum):
    """Draft document status options"""
    DRAFT = "draft"              # Initial AI-generated
    REVIEWED = "reviewed"        # Lawyer has reviewed/edited
    EXPORTED = "exported"        # Has been exported at least once


class DraftContentSection(BaseModel):
    """Draft content section schema"""
    title: str
    content: str
    order: int


class DraftContent(BaseModel):
    """Structured draft content schema"""
    header: Optional[dict] = None
    sections: List[DraftContentSection] = Field(default_factory=list)
    citations: List[DraftCitation] = Field(default_factory=list)
    footer: Optional[dict] = None


class DraftCreate(BaseModel):
    """Draft creation request schema"""
    title: str = Field(..., min_length=1, max_length=255)
    document_type: DraftDocumentType = DraftDocumentType.BRIEF
    content: DraftContent


class DraftUpdate(BaseModel):
    """Draft update request schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    document_type: Optional[DraftDocumentType] = None
    content: Optional[DraftContent] = None
    status: Optional[DraftDocumentStatus] = None


class DraftResponse(BaseModel):
    """Draft response schema"""
    id: str
    case_id: str
    title: str
    document_type: DraftDocumentType
    content: dict  # Structured content with sections
    version: int
    status: DraftDocumentStatus
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftListItem(BaseModel):
    """Draft list item schema (summary)"""
    id: str
    case_id: str
    title: str
    document_type: DraftDocumentType
    version: int
    status: DraftDocumentStatus
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftListResponse(BaseModel):
    """Draft list response schema"""
    drafts: List[DraftListItem]
    total: int


# ============================================
# Async Draft Preview Schemas (API Gateway 30s timeout 우회)
# ============================================
class DraftJobStatus(str, Enum):
    """Draft job status enum"""
    QUEUED = "queued"        # 대기 중
    PROCESSING = "processing"  # 처리 중
    COMPLETED = "completed"    # 완료
    FAILED = "failed"          # 실패


class DraftJobCreateResponse(BaseModel):
    """비동기 초안 생성 시작 응답"""
    job_id: str
    case_id: str
    status: DraftJobStatus = DraftJobStatus.QUEUED
    message: str = "초안 생성이 시작되었습니다. 잠시 후 결과를 확인해주세요."
    created_at: datetime


class DraftJobStatusResponse(BaseModel):
    """비동기 초안 생성 상태 조회 응답"""
    job_id: str
    case_id: str
    status: DraftJobStatus
    progress: int = 0  # 0-100
    result: Optional[DraftPreviewResponse] = None  # 완료 시 결과
    error_message: Optional[str] = None  # 실패 시 에러 메시지
    created_at: datetime
    completed_at: Optional[datetime] = None
