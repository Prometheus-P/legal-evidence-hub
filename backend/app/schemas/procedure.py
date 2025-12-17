"""
Pydantic schemas for Procedure Stage management
US3 - 절차 단계 관리 (Procedure Stage Tracking)

Based on Korean Family Litigation Act procedure stages
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================
class ProcedureStageType(str, Enum):
    """Korean family litigation procedure stages"""
    FILED = "filed"                       # 소장 접수
    SERVED = "served"                     # 송달
    ANSWERED = "answered"                 # 답변서
    MEDIATION = "mediation"               # 조정 회부
    MEDIATION_CLOSED = "mediation_closed" # 조정 종결
    TRIAL = "trial"                       # 본안 이행
    JUDGMENT = "judgment"                 # 판결 선고
    APPEAL = "appeal"                     # 항소심
    FINAL = "final"                       # 확정


class StageStatus(str, Enum):
    """Procedure stage status"""
    PENDING = "pending"           # 대기
    IN_PROGRESS = "in_progress"   # 진행중
    COMPLETED = "completed"       # 완료
    SKIPPED = "skipped"           # 건너뜀


# Stage order for navigation
STAGE_ORDER = [
    ProcedureStageType.FILED,
    ProcedureStageType.SERVED,
    ProcedureStageType.ANSWERED,
    ProcedureStageType.MEDIATION,
    ProcedureStageType.MEDIATION_CLOSED,
    ProcedureStageType.TRIAL,
    ProcedureStageType.JUDGMENT,
    ProcedureStageType.APPEAL,
    ProcedureStageType.FINAL,
]

# Stage Korean labels
STAGE_LABELS = {
    ProcedureStageType.FILED: "소장 접수",
    ProcedureStageType.SERVED: "송달",
    ProcedureStageType.ANSWERED: "답변서",
    ProcedureStageType.MEDIATION: "조정 회부",
    ProcedureStageType.MEDIATION_CLOSED: "조정 종결",
    ProcedureStageType.TRIAL: "본안 이행",
    ProcedureStageType.JUDGMENT: "판결 선고",
    ProcedureStageType.APPEAL: "항소심",
    ProcedureStageType.FINAL: "확정",
}

STATUS_LABELS = {
    StageStatus.PENDING: "대기",
    StageStatus.IN_PROGRESS: "진행중",
    StageStatus.COMPLETED: "완료",
    StageStatus.SKIPPED: "건너뜀",
}


# ============================================
# Document Schema
# ============================================
class StageDocument(BaseModel):
    """Document attached to a procedure stage"""
    name: str
    s3_key: str
    uploaded_at: datetime


# ============================================
# Request Schemas
# ============================================
class ProcedureStageCreate(BaseModel):
    """Schema for creating a new procedure stage"""
    stage: ProcedureStageType
    status: StageStatus = StageStatus.PENDING
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    court_reference: Optional[str] = Field(None, max_length=100)
    judge_name: Optional[str] = Field(None, max_length=50)
    court_room: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    documents: Optional[List[StageDocument]] = None
    outcome: Optional[str] = Field(None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "stage": "filed",
                "status": "completed",
                "scheduled_date": "2024-01-15T09:00:00Z",
                "completed_date": "2024-01-15T10:30:00Z",
                "court_reference": "2024드합1234",
                "judge_name": "김판사",
                "notes": "소장 접수 완료"
            }
        }


class ProcedureStageUpdate(BaseModel):
    """Schema for updating an existing procedure stage"""
    status: Optional[StageStatus] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    court_reference: Optional[str] = Field(None, max_length=100)
    judge_name: Optional[str] = Field(None, max_length=50)
    court_room: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    documents: Optional[List[StageDocument]] = None
    outcome: Optional[str] = Field(None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "completed_date": "2024-01-20T14:00:00Z",
                "outcome": "조정성립"
            }
        }


class TransitionToNextStage(BaseModel):
    """Schema for transitioning to the next procedure stage"""
    next_stage: ProcedureStageType
    outcome: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "next_stage": "mediation_closed",
                "outcome": "조정불성립",
                "notes": "조정 불성립으로 본안 진행 예정"
            }
        }


# ============================================
# Response Schemas
# ============================================
class ProcedureStageResponse(BaseModel):
    """Response schema for a single procedure stage"""
    id: str
    case_id: str
    stage: ProcedureStageType
    stage_label: str = ""
    status: StageStatus
    status_label: str = ""
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    court_reference: Optional[str] = None
    judge_name: Optional[str] = None
    court_room: Optional[str] = None
    notes: Optional[str] = None
    documents: Optional[List[StageDocument]] = None
    outcome: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_labels(cls, obj):
        """Create response with Korean labels"""
        data = {
            "id": obj.id,
            "case_id": obj.case_id,
            "stage": obj.stage,
            "stage_label": STAGE_LABELS.get(obj.stage, str(obj.stage)),
            "status": obj.status,
            "status_label": STATUS_LABELS.get(obj.status, str(obj.status)),
            "scheduled_date": obj.scheduled_date,
            "completed_date": obj.completed_date,
            "court_reference": obj.court_reference,
            "judge_name": obj.judge_name,
            "court_room": obj.court_room,
            "notes": obj.notes,
            "documents": obj.documents or [],
            "outcome": obj.outcome,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
            "created_by": obj.created_by,
        }
        return cls(**data)


class ProcedureTimelineResponse(BaseModel):
    """Response schema for procedure timeline (all stages for a case)"""
    case_id: str
    current_stage: Optional[ProcedureStageType] = None
    current_stage_label: str = ""
    stages: List[ProcedureStageResponse]
    completed_count: int = 0
    total_count: int = 9  # Total number of stages in the workflow

    @property
    def progress_percentage(self) -> int:
        """Calculate progress as percentage"""
        return int((self.completed_count / self.total_count) * 100)


class UpcomingDeadline(BaseModel):
    """Schema for upcoming deadline notification"""
    case_id: str
    case_title: str
    stage: ProcedureStageType
    stage_label: str
    scheduled_date: datetime
    days_until: int
    court_reference: Optional[str] = None


class UpcomingDeadlinesResponse(BaseModel):
    """Response schema for upcoming deadlines"""
    deadlines: List[UpcomingDeadline]
    total_count: int
