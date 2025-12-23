"""
Evidence Schemas - Upload, Analysis, Review
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


# ============================================
# Article 840 Categories
# ============================================
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


# ============================================
# Upload Schemas
# ============================================
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


class ExifMetadataInput(BaseModel):
    """EXIF metadata input from client-side extraction"""
    gps_latitude: Optional[float] = Field(None, description="GPS latitude in decimal degrees")
    gps_longitude: Optional[float] = Field(None, description="GPS longitude in decimal degrees")
    gps_altitude: Optional[float] = Field(None, description="GPS altitude in meters")
    datetime_original: Optional[str] = Field(None, description="Original capture datetime (ISO format)")
    camera_make: Optional[str] = Field(None, description="Camera manufacturer")
    camera_model: Optional[str] = Field(None, description="Camera model")


class UploadCompleteRequest(BaseModel):
    """Upload complete request schema"""
    case_id: str
    evidence_temp_id: str
    s3_key: str
    file_size: int = 0  # File size in bytes
    note: Optional[str] = None
    exif_metadata: Optional[ExifMetadataInput] = Field(
        None,
        description="EXIF metadata extracted from image on client side (for detective uploads)"
    )


class UploadCompleteResponse(BaseModel):
    """Upload complete response schema"""
    evidence_id: str
    case_id: str
    filename: str
    s3_key: str
    status: str  # pending (waiting for AI processing)
    review_status: Optional[str] = None  # pending_review for client uploads, None for internal uploads
    created_at: datetime


# ============================================
# Evidence List/Detail Schemas
# ============================================
class EvidenceSummary(BaseModel):
    """Evidence summary schema (for list view)"""
    id: str
    case_id: str
    type: str  # text, image, audio, video, pdf
    filename: str
    size: int  # File size in bytes
    created_at: datetime
    status: str  # pending, processing, done, error
    ai_summary: Optional[str] = None  # AI-generated summary
    article_840_tags: Optional[Article840Tags] = None  # Article 840 tagging
    # 015-evidence-speaker-mapping: Speaker mapping status
    has_speaker_mapping: bool = Field(default=False, description="Whether speaker mapping is configured")


class EvidenceListResponse(BaseModel):
    """Evidence list response wrapper (matches frontend expectation)"""
    evidence: list[EvidenceSummary]
    total: int


class EvidenceReviewRequest(BaseModel):
    """Evidence review request schema (for lawyer approval)"""
    action: str = Field(..., pattern="^(approve|reject)$", description="Review action: approve or reject")
    comment: Optional[str] = Field(None, max_length=500, description="Optional review comment")


class EvidenceReviewResponse(BaseModel):
    """Evidence review response schema"""
    evidence_id: str
    case_id: str
    review_status: str  # approved, rejected
    reviewed_by: str
    reviewed_at: datetime
    comment: Optional[str] = None


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
    labels: Optional[list[str]] = None  # Mapped from article_840_tags.categories
    insights: Optional[list[str]] = None
    content: Optional[str] = None  # Full STT/OCR text
    speaker: Optional[str] = None  # For audio/video
    timestamp: Optional[datetime] = None  # Event timestamp in evidence
    qdrant_id: Optional[str] = None  # RAG index reference (Qdrant point ID)
    article_840_tags: Optional[Article840Tags] = None  # Article 840 tagging

    # 015-evidence-speaker-mapping: Speaker mapping fields
    speaker_mapping: Optional[Dict[str, "SpeakerMappingItem"]] = None
    speaker_mapping_updated_at: Optional[datetime] = None


# ============================================
# Speaker Mapping Schemas (015-evidence-speaker-mapping)
# ============================================
class SpeakerMappingItem(BaseModel):
    """Individual speaker mapping item"""
    party_id: str = Field(..., description="PartyNode ID from relationship graph")
    party_name: str = Field(..., description="Party name for display")


class SpeakerMappingUpdateRequest(BaseModel):
    """Speaker mapping update request"""
    speaker_mapping: Dict[str, SpeakerMappingItem] = Field(
        default_factory=dict,
        description="Speaker label to party mapping. Empty dict clears mapping.",
        json_schema_extra={
            "examples": [{
                "나": {"party_id": "party_001", "party_name": "김동우"},
                "상대방": {"party_id": "party_002", "party_name": "김도연"}
            }]
        }
    )


class SpeakerMappingResponse(BaseModel):
    """Speaker mapping update response"""
    evidence_id: str
    speaker_mapping: Optional[Dict[str, SpeakerMappingItem]] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


# Update forward reference for EvidenceDetail
EvidenceDetail.model_rebuild()
