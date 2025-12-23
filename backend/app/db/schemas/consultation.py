"""
Consultation Schemas - 상담내역 CRUD
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date as dt_date, time as dt_time, datetime


# ============================================
# Consultation Schemas
# ============================================
class ConsultationParticipantCreate(BaseModel):
    """참석자 생성 스키마"""
    name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = Field(None, max_length=50)  # 'client', 'lawyer', 'witness', 'other'


class ConsultationParticipantOut(BaseModel):
    """참석자 응답 스키마"""
    id: str
    name: str
    role: Optional[str] = None

    class Config:
        from_attributes = True


class ConsultationCreate(BaseModel):
    """상담 생성 요청 스키마"""
    date: dt_date = Field(..., description="상담 날짜")
    time: Optional[dt_time] = Field(None, description="상담 시간")
    type: Literal['phone', 'in_person', 'online'] = Field(default='phone', description="상담 유형")
    participants: List[str] = Field(default_factory=list, description="참석자 이름 목록")
    summary: str = Field(..., min_length=1, max_length=5000, description="상담 요약")
    notes: Optional[str] = Field(None, max_length=5000, description="추가 메모")


class ConsultationUpdate(BaseModel):
    """상담 수정 요청 스키마"""
    date: Optional[dt_date] = None
    time: Optional[dt_time] = None
    type: Optional[Literal['phone', 'in_person', 'online']] = None
    participants: Optional[List[str]] = None
    summary: Optional[str] = Field(None, min_length=1, max_length=5000)
    notes: Optional[str] = Field(None, max_length=5000)


class ConsultationOut(BaseModel):
    """상담 응답 스키마"""
    id: str
    case_id: str
    date: dt_date
    time: Optional[dt_time] = None
    type: str
    participants: List[str]  # 이름 목록으로 평탄화
    summary: str
    notes: Optional[str] = None
    created_by: str  # user_id
    created_by_name: Optional[str] = None  # user name
    created_at: datetime
    updated_at: datetime
    linked_evidence: List[str] = Field(default_factory=list)  # evidence_ids

    class Config:
        from_attributes = True


class ConsultationListResponse(BaseModel):
    """상담 목록 응답 스키마"""
    consultations: List[ConsultationOut]
    total: int


# ============================================
# Consultation Evidence Link Schemas
# ============================================
class LinkEvidenceRequest(BaseModel):
    """증거 연결 요청 스키마"""
    evidence_ids: List[str] = Field(..., min_length=1, description="연결할 증거 ID 목록")


class LinkEvidenceResponse(BaseModel):
    """증거 연결 응답 스키마"""
    consultation_id: str
    linked_evidence_ids: List[str]
    linked_at: datetime
