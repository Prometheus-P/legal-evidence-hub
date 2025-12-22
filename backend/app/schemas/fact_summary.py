"""
Fact Summary Schemas
014-case-fact-summary: Pydantic schemas for case fact summary API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FactSummaryBase(BaseModel):
    """사실관계 요약 기본 스키마"""
    ai_summary: str = Field(..., description="AI 생성 원본 사실관계")
    modified_summary: Optional[str] = Field(None, description="변호사 수정 사실관계")
    evidence_ids: List[str] = Field(default_factory=list, description="사용된 증거 ID 목록")
    fault_types: List[str] = Field(default_factory=list, description="추출된 유책사유")


class FactSummaryResponse(FactSummaryBase):
    """사실관계 조회 응답"""
    case_id: str
    created_at: datetime
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    has_previous_version: bool = Field(False, description="이전 버전 존재 여부")


class FactSummaryGenerateRequest(BaseModel):
    """사실관계 생성 요청"""
    force_regenerate: bool = Field(False, description="기존 요약 무시하고 재생성")


class FactSummaryGenerateResponse(BaseModel):
    """사실관계 생성 응답"""
    case_id: str
    ai_summary: str
    evidence_count: int
    fault_types: List[str]
    generated_at: datetime


class FactSummaryUpdateRequest(BaseModel):
    """사실관계 수정 요청"""
    modified_summary: str = Field(..., min_length=1, max_length=15000)


class FactSummaryUpdateResponse(BaseModel):
    """사실관계 수정 응답"""
    case_id: str
    modified_summary: str
    modified_at: datetime
    modified_by: str
