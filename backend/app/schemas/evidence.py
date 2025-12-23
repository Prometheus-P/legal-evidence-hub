"""
Evidence Schemas - Evidence + Article840
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Article840Category(str, Enum):
    """
    민법 840조 이혼 사유 카테고리

    Korean Civil Code Article 840 - Grounds for Divorce
    """
    ADULTERY = "adultery"  # 제1호: 배우자의 부정행위
    DESERTION = "desertion"  # 제2호: 악의의 유기
    MISTREATMENT_BY_INLAWS = "mistreatment_by_inlaws"  # 제3호: 배우자 직계존속의 부당대우
    HARM_TO_OWN_PARENTS = "harm_to_own_parents"  # 제4호: 자기 직계존속 피해
    UNKNOWN_WHEREABOUTS = "unknown_whereabouts"  # 제5호: 생사불명 3년
    IRRECONCILABLE_DIFFERENCES = "irreconcilable_differences"  # 제6호: 혼인 지속 곤란사유
    GENERAL = "general"  # 일반 증거 (특정 조항에 해당하지 않음)


class Article840Tags(BaseModel):
    """Article 840 tagging result schema"""
    categories: list[Article840Category] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)


class PresignedUrlRequest(BaseModel):
    """Presigned URL request schema"""
    case_id: str
    filename: str
    content_type: str


class PresignedUrlResponse(BaseModel):
    """Presigned URL response schema"""
    upload_url: str
    fields: dict
    evidence_temp_id: str
    s3_key: str


class UploadCompleteRequest(BaseModel):
    """Upload complete request schema"""
    case_id: str
    evidence_temp_id: str
    s3_key: str
    note: Optional[str] = None


class UploadCompleteResponse(BaseModel):
    """Upload complete response schema"""
    evidence_id: str
    case_id: str
    filename: str
    s3_key: str
    status: str  # pending (waiting for AI processing)
    created_at: datetime


class EvidenceSummary(BaseModel):
    """Evidence summary schema (for list view)"""
    id: str
    case_id: str
    type: str  # text, image, audio, video, pdf
    filename: str
    size: int  # File size in bytes
    created_at: datetime
    status: str  # pending, processing, done, error
    article_840_tags: Optional[Article840Tags] = None


class EvidenceDetail(BaseModel):
    """Evidence detail schema (for detail view with AI analysis)"""
    id: str
    case_id: str
    type: str
    filename: str
    size: int  # File size in bytes
    s3_key: str
    content_type: str
    created_at: datetime
    status: str

    # AI analysis results (available when status="done")
    ai_summary: Optional[str] = None
    labels: Optional[list[str]] = None
    insights: Optional[list[str]] = None
    content: Optional[str] = None
    speaker: Optional[str] = None
    timestamp: Optional[datetime] = None
    qdrant_id: Optional[str] = None
    article_840_tags: Optional[Article840Tags] = None
