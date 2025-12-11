"""
Procedure Service - Business logic for procedure stage management
US3 - 절차 단계 관리 (Procedure Stage Tracking)

Implements Korean Family Litigation Act procedure flow with state validation
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.db.models import ProcedureStageRecord, ProcedureStageType, StageStatus, Case
from app.repositories.procedure_repository import ProcedureRepository
from app.schemas.procedure import (
    ProcedureStageCreate,
    ProcedureStageUpdate,
    ProcedureStageResponse,
    ProcedureTimelineResponse,
    TransitionToNextStage,
    UpcomingDeadline,
    UpcomingDeadlinesResponse,
    STAGE_ORDER,
    STAGE_LABELS,
)


# Valid state transitions based on Korean family litigation procedure
VALID_TRANSITIONS = {
    ProcedureStageType.FILED: [ProcedureStageType.SERVED],
    ProcedureStageType.SERVED: [ProcedureStageType.ANSWERED],
    ProcedureStageType.ANSWERED: [
        ProcedureStageType.MEDIATION,
        ProcedureStageType.TRIAL,  # Skip mediation if not applicable
    ],
    ProcedureStageType.MEDIATION: [ProcedureStageType.MEDIATION_CLOSED],
    ProcedureStageType.MEDIATION_CLOSED: [
        ProcedureStageType.TRIAL,     # 조정불성립 → 본안
        ProcedureStageType.FINAL,     # 조정성립 → 확정
    ],
    ProcedureStageType.TRIAL: [ProcedureStageType.JUDGMENT],
    ProcedureStageType.JUDGMENT: [
        ProcedureStageType.APPEAL,    # 항소
        ProcedureStageType.FINAL,     # 확정 (항소 안함)
    ],
    ProcedureStageType.APPEAL: [ProcedureStageType.FINAL],
    ProcedureStageType.FINAL: [],  # Terminal state
}


class ProcedureService:
    """Service for procedure stage business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProcedureRepository(db)

    def get_stage(self, stage_id: str) -> Optional[ProcedureStageRecord]:
        """Get a procedure stage by ID"""
        return self.repository.get_by_id(stage_id)

    def get_timeline(self, case_id: str) -> ProcedureTimelineResponse:
        """Get complete procedure timeline for a case"""
        stages = self.repository.get_all_by_case(case_id)
        current = self.repository.get_current_stage(case_id)
        completed_count = self.repository.count_completed_stages(case_id)

        stage_responses = [
            ProcedureStageResponse.from_orm_with_labels(s) for s in stages
        ]

        current_stage = current.stage if current else None
        current_label = STAGE_LABELS.get(current_stage, "") if current_stage else ""

        return ProcedureTimelineResponse(
            case_id=case_id,
            current_stage=current_stage,
            current_stage_label=current_label,
            stages=stage_responses,
            completed_count=completed_count,
            total_count=len(STAGE_ORDER),
        )

    def create_stage(
        self,
        case_id: str,
        data: ProcedureStageCreate,
        user_id: Optional[str] = None
    ) -> ProcedureStageRecord:
        """Create a new procedure stage"""
        # Check if stage already exists
        existing = self.repository.get_by_case_and_stage(case_id, data.stage)
        if existing:
            raise ValueError(f"Stage '{data.stage}' already exists for this case")

        # Convert documents to dict format
        docs = None
        if data.documents:
            docs = [doc.model_dump() for doc in data.documents]

        return self.repository.create(
            case_id=case_id,
            stage=data.stage,
            status=data.status,
            scheduled_date=data.scheduled_date,
            completed_date=data.completed_date,
            court_reference=data.court_reference,
            judge_name=data.judge_name,
            court_room=data.court_room,
            notes=data.notes,
            documents=docs,
            outcome=data.outcome,
            created_by=user_id
        )

    def update_stage(
        self,
        stage_id: str,
        data: ProcedureStageUpdate
    ) -> Optional[ProcedureStageRecord]:
        """Update an existing procedure stage"""
        update_data = data.model_dump(exclude_unset=True)

        # Convert documents if present
        if "documents" in update_data and update_data["documents"] is not None:
            update_data["documents"] = [
                doc.model_dump() if hasattr(doc, "model_dump") else doc
                for doc in update_data["documents"]
            ]

        return self.repository.update(stage_id, **update_data)

    def complete_stage(
        self,
        stage_id: str,
        outcome: Optional[str] = None,
        completed_date: Optional[datetime] = None
    ) -> ProcedureStageRecord:
        """Mark a stage as completed"""
        record = self.repository.get_by_id(stage_id)
        if not record:
            raise ValueError("Stage not found")

        if record.status == StageStatus.COMPLETED:
            raise ValueError("Stage is already completed")

        update_data = {
            "status": StageStatus.COMPLETED,
            "completed_date": completed_date or datetime.now(timezone.utc)
        }
        if outcome:
            update_data["outcome"] = outcome

        return self.repository.update(stage_id, **update_data)

    def transition_to_next(
        self,
        case_id: str,
        data: TransitionToNextStage,
        user_id: Optional[str] = None
    ) -> Tuple[ProcedureStageRecord, ProcedureStageRecord]:
        """
        Transition from current stage to next stage
        Returns tuple of (completed_stage, new_stage)
        """
        current = self.repository.get_current_stage(case_id)
        if not current:
            # Find the last completed stage or start fresh
            all_stages = self.repository.get_all_by_case(case_id)
            completed = [s for s in all_stages if s.status == StageStatus.COMPLETED]
            if completed:
                current = completed[-1]  # Last completed
            else:
                # No stages yet, next should be FILED
                if data.next_stage != ProcedureStageType.FILED:
                    raise ValueError(
                        "첫 번째 단계는 '소장 접수'여야 합니다."
                    )
                # Create FILED stage directly
                return (None, self._create_next_stage(
                    case_id, data, user_id, start_in_progress=True
                ))

        # Validate transition
        valid_next = VALID_TRANSITIONS.get(current.stage, [])
        if data.next_stage not in valid_next:
            current_label = STAGE_LABELS.get(current.stage, current.stage)
            next_label = STAGE_LABELS.get(data.next_stage, data.next_stage)
            valid_labels = [STAGE_LABELS.get(s, s) for s in valid_next]
            raise ValueError(
                f"'{current_label}'에서 '{next_label}'로 이동할 수 없습니다. "
                f"유효한 다음 단계: {', '.join(valid_labels)}"
            )

        # Complete current stage if in progress
        if current.status == StageStatus.IN_PROGRESS:
            current = self.complete_stage(
                current.id,
                outcome=data.outcome,
                completed_date=datetime.now(timezone.utc)
            )

        # Create or activate next stage
        next_record = self._create_next_stage(case_id, data, user_id)

        return (current, next_record)

    def _create_next_stage(
        self,
        case_id: str,
        data: TransitionToNextStage,
        user_id: Optional[str] = None,
        start_in_progress: bool = True
    ) -> ProcedureStageRecord:
        """Create or activate the next stage"""
        existing = self.repository.get_by_case_and_stage(case_id, data.next_stage)

        if existing:
            # Activate existing stage
            update_data = {"status": StageStatus.IN_PROGRESS}
            if data.scheduled_date:
                update_data["scheduled_date"] = data.scheduled_date
            if data.notes:
                update_data["notes"] = data.notes
            return self.repository.update(existing.id, **update_data)
        else:
            # Create new stage
            return self.repository.create(
                case_id=case_id,
                stage=data.next_stage,
                status=StageStatus.IN_PROGRESS if start_in_progress else StageStatus.PENDING,
                scheduled_date=data.scheduled_date,
                notes=data.notes,
                created_by=user_id
            )

    def skip_stage(
        self,
        stage_id: str,
        reason: Optional[str] = None
    ) -> ProcedureStageRecord:
        """Skip a stage (mark as skipped)"""
        record = self.repository.get_by_id(stage_id)
        if not record:
            raise ValueError("Stage not found")

        if record.status == StageStatus.COMPLETED:
            raise ValueError("Cannot skip a completed stage")

        update_data = {
            "status": StageStatus.SKIPPED,
        }
        if reason:
            update_data["notes"] = f"[건너뜀] {reason}"

        return self.repository.update(stage_id, **update_data)

    def initialize_case_timeline(
        self,
        case_id: str,
        user_id: Optional[str] = None,
        start_filed: bool = True
    ) -> List[ProcedureStageRecord]:
        """Initialize timeline with all stages for a new case"""
        existing = self.repository.get_all_by_case(case_id)
        if existing:
            return existing  # Already initialized

        stages = self.repository.initialize_stages_for_case(case_id, user_id)

        # Optionally start FILED stage as in_progress
        if start_filed and stages:
            filed_stage = next(
                (s for s in stages if s.stage == ProcedureStageType.FILED), None
            )
            if filed_stage:
                self.repository.update(filed_stage.id, status=StageStatus.IN_PROGRESS)

        return self.repository.get_all_by_case(case_id)

    def get_upcoming_deadlines(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> UpcomingDeadlinesResponse:
        """Get upcoming procedure deadlines"""
        stages = self.repository.get_upcoming_deadlines(user_id, days_ahead)

        deadlines = []
        now = datetime.now(timezone.utc)

        for stage in stages:
            # Get case info
            case = self.db.query(Case).filter(Case.id == stage.case_id).first()
            if not case:
                continue

            days_until = (stage.scheduled_date - now).days

            deadlines.append(UpcomingDeadline(
                case_id=stage.case_id,
                case_title=case.title,
                stage=stage.stage,
                stage_label=STAGE_LABELS.get(stage.stage, str(stage.stage)),
                scheduled_date=stage.scheduled_date,
                days_until=days_until,
                court_reference=stage.court_reference
            ))

        return UpcomingDeadlinesResponse(
            deadlines=deadlines,
            total_count=len(deadlines)
        )

    def get_valid_next_stages(
        self,
        case_id: str
    ) -> List[Tuple[ProcedureStageType, str]]:
        """Get valid next stages from current position"""
        current = self.repository.get_current_stage(case_id)
        if not current:
            # Check for last completed
            all_stages = self.repository.get_all_by_case(case_id)
            completed = [s for s in all_stages if s.status == StageStatus.COMPLETED]
            if completed:
                current = completed[-1]
            else:
                # No stages, first must be FILED
                return [(ProcedureStageType.FILED, STAGE_LABELS[ProcedureStageType.FILED])]

        valid = VALID_TRANSITIONS.get(current.stage, [])
        return [(s, STAGE_LABELS.get(s, str(s))) for s in valid]

    def delete_stage(self, stage_id: str) -> bool:
        """Delete a procedure stage"""
        return self.repository.delete(stage_id)
