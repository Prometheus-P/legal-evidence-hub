"""
Procedure Repository - Data access layer for procedure stages
US3 - 절차 단계 관리
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import ProcedureStageRecord, ProcedureStageType, StageStatus


class ProcedureRepository:
    """Repository for procedure stage data access"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, stage_id: str) -> Optional[ProcedureStageRecord]:
        """Get a procedure stage by ID"""
        return self.db.query(ProcedureStageRecord).filter(
            ProcedureStageRecord.id == stage_id
        ).first()

    def get_by_case_and_stage(
        self, case_id: str, stage: ProcedureStageType
    ) -> Optional[ProcedureStageRecord]:
        """Get a specific stage for a case"""
        return self.db.query(ProcedureStageRecord).filter(
            and_(
                ProcedureStageRecord.case_id == case_id,
                ProcedureStageRecord.stage == stage
            )
        ).first()

    def get_all_by_case(self, case_id: str) -> List[ProcedureStageRecord]:
        """Get all procedure stages for a case, ordered by stage"""
        stages = self.db.query(ProcedureStageRecord).filter(
            ProcedureStageRecord.case_id == case_id
        ).all()

        # Sort by stage order
        stage_order = {
            ProcedureStageType.FILED: 0,
            ProcedureStageType.SERVED: 1,
            ProcedureStageType.ANSWERED: 2,
            ProcedureStageType.MEDIATION: 3,
            ProcedureStageType.MEDIATION_CLOSED: 4,
            ProcedureStageType.TRIAL: 5,
            ProcedureStageType.JUDGMENT: 6,
            ProcedureStageType.APPEAL: 7,
            ProcedureStageType.FINAL: 8,
        }
        return sorted(stages, key=lambda s: stage_order.get(s.stage, 99))

    def get_current_stage(self, case_id: str) -> Optional[ProcedureStageRecord]:
        """Get the current (in_progress) stage for a case"""
        return self.db.query(ProcedureStageRecord).filter(
            and_(
                ProcedureStageRecord.case_id == case_id,
                ProcedureStageRecord.status == StageStatus.IN_PROGRESS
            )
        ).first()

    def get_upcoming_deadlines(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> List[ProcedureStageRecord]:
        """Get upcoming scheduled stages within specified days"""
        now = datetime.now(timezone.utc)
        deadline = now + timedelta(days=days_ahead)

        return self.db.query(ProcedureStageRecord).filter(
            and_(
                ProcedureStageRecord.scheduled_date.isnot(None),
                ProcedureStageRecord.scheduled_date >= now,
                ProcedureStageRecord.scheduled_date <= deadline,
                ProcedureStageRecord.status.in_([
                    StageStatus.PENDING,
                    StageStatus.IN_PROGRESS
                ])
            )
        ).order_by(ProcedureStageRecord.scheduled_date.asc()).all()

    def create(
        self,
        case_id: str,
        stage: ProcedureStageType,
        status: StageStatus = StageStatus.PENDING,
        scheduled_date: Optional[datetime] = None,
        completed_date: Optional[datetime] = None,
        court_reference: Optional[str] = None,
        judge_name: Optional[str] = None,
        court_room: Optional[str] = None,
        notes: Optional[str] = None,
        documents: Optional[list] = None,
        outcome: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> ProcedureStageRecord:
        """Create a new procedure stage record"""
        record = ProcedureStageRecord(
            case_id=case_id,
            stage=stage,
            status=status,
            scheduled_date=scheduled_date,
            completed_date=completed_date,
            court_reference=court_reference,
            judge_name=judge_name,
            court_room=court_room,
            notes=notes,
            documents=documents or [],
            outcome=outcome,
            created_by=created_by
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(
        self,
        stage_id: str,
        **kwargs
    ) -> Optional[ProcedureStageRecord]:
        """Update a procedure stage record"""
        record = self.get_by_id(stage_id)
        if not record:
            return None

        for key, value in kwargs.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)

        record.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, stage_id: str) -> bool:
        """Delete a procedure stage record"""
        record = self.get_by_id(stage_id)
        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        return True

    def delete_all_by_case(self, case_id: str) -> int:
        """Delete all procedure stages for a case"""
        count = self.db.query(ProcedureStageRecord).filter(
            ProcedureStageRecord.case_id == case_id
        ).delete()
        self.db.commit()
        return count

    def count_completed_stages(self, case_id: str) -> int:
        """Count completed stages for a case"""
        return self.db.query(ProcedureStageRecord).filter(
            and_(
                ProcedureStageRecord.case_id == case_id,
                ProcedureStageRecord.status == StageStatus.COMPLETED
            )
        ).count()

    def initialize_stages_for_case(
        self,
        case_id: str,
        created_by: Optional[str] = None
    ) -> List[ProcedureStageRecord]:
        """Initialize all stages for a new case with default pending status"""
        stages = []
        stage_types = [
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

        for stage_type in stage_types:
            record = ProcedureStageRecord(
                case_id=case_id,
                stage=stage_type,
                status=StageStatus.PENDING,
                created_by=created_by
            )
            self.db.add(record)
            stages.append(record)

        self.db.commit()
        for stage in stages:
            self.db.refresh(stage)

        return stages
