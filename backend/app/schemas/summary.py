"""
Pydantic schemas for Case Summary Card
US8 - 진행 상태 요약 카드 (Progress Summary Cards)

Provides sharable case summary for client communication
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# ============================================
# Sub-schemas
# ============================================
class CompletedStageInfo(BaseModel):
    """Information about a completed procedure stage"""
    stage_label: str
    completed_date: Optional[datetime] = None


class NextSchedule(BaseModel):
    """Information about the next scheduled event"""
    event_type: str  # e.g., "조정기일", "변론기일"
    scheduled_date: datetime
    location: Optional[str] = None  # e.g., "서울가정법원 305호"
    notes: Optional[str] = None


class EvidenceStat(BaseModel):
    """Evidence statistics by category"""
    category: str
    count: int


class LawyerInfo(BaseModel):
    """Lawyer contact information"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None


# ============================================
# Main Response Schema
# ============================================
class CaseSummaryResponse(BaseModel):
    """
    Response schema for case summary card

    Contains all information needed to display a 1-page summary card
    for client communication.
    """
    # Case identification
    case_id: str
    case_title: str
    court_reference: Optional[str] = None  # e.g., "2024가합12345"
    client_name: Optional[str] = None

    # Current status
    current_stage: Optional[str] = None  # Korean label
    current_stage_status: Optional[str] = None  # e.g., "진행중"
    progress_percent: int = 0

    # Completed stages
    completed_stages: List[CompletedStageInfo] = []

    # Next schedule
    next_schedules: List[NextSchedule] = []

    # Evidence summary
    evidence_total: int = 0
    evidence_stats: List[EvidenceStat] = []

    # Lawyer info
    lawyer: Optional[LawyerInfo] = None

    # Metadata
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case_abc123",
                "case_title": "김○○ 이혼 사건",
                "court_reference": "2024가합12345",
                "client_name": "김민수",
                "current_stage": "조정 절차 진행 중",
                "current_stage_status": "진행중",
                "progress_percent": 33,
                "completed_stages": [
                    {"stage_label": "소장 접수", "completed_date": "2024-10-15T10:00:00Z"},
                    {"stage_label": "송달 완료", "completed_date": "2024-10-25T14:00:00Z"},
                    {"stage_label": "답변서 접수", "completed_date": "2024-11-20T09:00:00Z"},
                ],
                "next_schedules": [
                    {
                        "event_type": "조정기일",
                        "scheduled_date": "2024-12-11T14:00:00Z",
                        "location": "서울가정법원 305호"
                    }
                ],
                "evidence_total": 12,
                "evidence_stats": [
                    {"category": "부정행위 관련", "count": 8},
                    {"category": "재산분할 관련", "count": 4},
                ],
                "lawyer": {
                    "name": "홍길동",
                    "phone": "02-1234-5678",
                    "email": "hong@lawfirm.com"
                },
                "generated_at": "2024-12-09T10:00:00Z"
            }
        }


# ============================================
# Request Schemas
# ============================================
class ShareSummaryRequest(BaseModel):
    """Request to share summary via email"""
    recipient_email: EmailStr
    recipient_name: Optional[str] = None
    message: Optional[str] = Field(None, max_length=500)
    include_pdf: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "recipient_email": "client@example.com",
                "recipient_name": "김민수",
                "message": "이번 사건 진행 현황을 공유드립니다.",
                "include_pdf": True
            }
        }


class ShareSummaryResponse(BaseModel):
    """Response after sharing summary"""
    success: bool
    message: str
    sent_at: Optional[datetime] = None
