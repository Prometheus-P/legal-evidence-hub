"""
Summary Card Service - Business logic for case summary generation
US8 - 진행 상태 요약 카드 (Progress Summary Cards)

Generates shareable case summary for client communication
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from app.db.models import (
    Case, User, ProcedureStageRecord,
    ProcedureStageType, StageStatus
)
from app.schemas.summary import (
    CaseSummaryResponse,
    CompletedStageInfo,
    NextSchedule,
    EvidenceStat,
    LawyerInfo,
)
from app.schemas.procedure import STAGE_LABELS, STATUS_LABELS


class SummaryCardService:
    """Service for generating case summary cards"""

    def __init__(self, db: Session):
        self.db = db

    def generate_summary(self, case_id: str) -> CaseSummaryResponse:
        """
        Generate a complete summary card for a case

        Args:
            case_id: The case ID to generate summary for

        Returns:
            CaseSummaryResponse with all summary data

        Raises:
            ValueError: If case not found
        """
        # Get case
        case = self.db.query(Case).filter(
            Case.id == case_id,
            Case.deleted_at.is_(None)
        ).first()

        if not case:
            raise ValueError("사건을 찾을 수 없습니다.")

        # Get procedure stages
        stages = self._get_procedure_stages(case_id)
        current_stage = self._get_current_stage(stages)
        completed_stages = self._get_completed_stages(stages)
        next_schedules = self._get_next_schedules(stages)
        progress_percent = self._calculate_progress(stages)

        # Get court reference from stages
        court_reference = self._get_court_reference(stages)

        # Get lawyer info
        lawyer_info = self._get_lawyer_info(case_id)

        # Get evidence stats (placeholder - integrate with evidence service when available)
        evidence_total, evidence_stats = self._get_evidence_stats(case_id)

        return CaseSummaryResponse(
            case_id=case_id,
            case_title=case.title,
            court_reference=court_reference,
            client_name=case.client_name,
            current_stage=current_stage.get("label") if current_stage else None,
            current_stage_status=current_stage.get("status") if current_stage else None,
            progress_percent=progress_percent,
            completed_stages=completed_stages,
            next_schedules=next_schedules,
            evidence_total=evidence_total,
            evidence_stats=evidence_stats,
            lawyer=lawyer_info,
            generated_at=datetime.now(timezone.utc)
        )

    def _get_procedure_stages(self, case_id: str) -> List[ProcedureStageRecord]:
        """Get all procedure stages for a case"""
        return self.db.query(ProcedureStageRecord).filter(
            ProcedureStageRecord.case_id == case_id
        ).order_by(ProcedureStageRecord.created_at.asc()).all()

    def _get_current_stage(
        self,
        stages: List[ProcedureStageRecord]
    ) -> Optional[dict]:
        """Get the current stage info"""
        # Find in_progress stage first
        in_progress = next(
            (s for s in stages if s.status == StageStatus.IN_PROGRESS),
            None
        )

        if in_progress:
            return {
                "label": STAGE_LABELS.get(in_progress.stage, str(in_progress.stage)),
                "status": STATUS_LABELS.get(in_progress.status, str(in_progress.status))
            }

        # If no in_progress, find the last completed
        completed = [s for s in stages if s.status == StageStatus.COMPLETED]
        if completed:
            last_completed = completed[-1]
            return {
                "label": f"{STAGE_LABELS.get(last_completed.stage, str(last_completed.stage))} 완료",
                "status": "완료"
            }

        # If no stages yet
        if stages:
            first_pending = next(
                (s for s in stages if s.status == StageStatus.PENDING),
                None
            )
            if first_pending:
                return {
                    "label": f"{STAGE_LABELS.get(first_pending.stage, str(first_pending.stage))} 대기중",
                    "status": "대기"
                }

        return None

    def _get_completed_stages(
        self,
        stages: List[ProcedureStageRecord]
    ) -> List[CompletedStageInfo]:
        """Get list of completed stages"""
        completed = []
        for s in stages:
            if s.status == StageStatus.COMPLETED:
                completed.append(CompletedStageInfo(
                    stage_label=STAGE_LABELS.get(s.stage, str(s.stage)),
                    completed_date=s.completed_date
                ))
        return completed

    def _get_next_schedules(
        self,
        stages: List[ProcedureStageRecord]
    ) -> List[NextSchedule]:
        """Get upcoming scheduled events"""
        now = datetime.now(timezone.utc)
        schedules = []

        for s in stages:
            # Only include future scheduled dates for pending/in_progress stages
            if s.scheduled_date and s.scheduled_date > now:
                if s.status in [StageStatus.PENDING, StageStatus.IN_PROGRESS]:
                    location = None
                    if s.court_room:
                        # Combine judge name and court room for location
                        location_parts = []
                        if s.court_reference:
                            location_parts.append(s.court_reference.split('가')[0] if '가' in s.court_reference else "법원")
                        if s.court_room:
                            location_parts.append(s.court_room)
                        location = " ".join(location_parts) if location_parts else None

                    schedules.append(NextSchedule(
                        event_type=f"{STAGE_LABELS.get(s.stage, str(s.stage))} 기일",
                        scheduled_date=s.scheduled_date,
                        location=location,
                        notes=s.notes
                    ))

        # Sort by date
        schedules.sort(key=lambda x: x.scheduled_date)
        return schedules[:3]  # Return max 3 upcoming schedules

    def _calculate_progress(self, stages: List[ProcedureStageRecord]) -> int:
        """Calculate progress percentage"""
        if not stages:
            return 0

        total = len(ProcedureStageType)  # 9 total stages
        completed = sum(1 for s in stages if s.status == StageStatus.COMPLETED)
        skipped = sum(1 for s in stages if s.status == StageStatus.SKIPPED)

        # Skipped stages also count toward progress
        progress = completed + skipped
        return min(int((progress / total) * 100), 100)

    def _get_court_reference(
        self,
        stages: List[ProcedureStageRecord]
    ) -> Optional[str]:
        """Get court reference from stages"""
        for s in stages:
            if s.court_reference:
                return s.court_reference
        return None

    def _get_lawyer_info(self, case_id: str) -> Optional[LawyerInfo]:
        """Get assigned lawyer info for the case"""
        # Get case owner (creator is usually the lawyer)
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None

        lawyer = self.db.query(User).filter(User.id == case.created_by).first()
        if not lawyer:
            return None

        return LawyerInfo(
            name=lawyer.name or lawyer.email.split('@')[0],
            phone=None,  # User model may not have phone
            email=lawyer.email
        )

    def _get_evidence_stats(self, case_id: str) -> tuple[int, List[EvidenceStat]]:
        """
        Get evidence statistics for the case

        Note: This is a placeholder. In production, this would integrate
        with the evidence service to get real evidence counts and categories.
        """
        # TODO: Integrate with actual evidence service when available
        # For now, return empty stats
        return 0, []

    def get_case_for_pdf(self, case_id: str) -> dict:
        """
        Get case data formatted for PDF generation

        Returns a dict with all the data needed for PDF rendering
        """
        summary = self.generate_summary(case_id)

        # Format dates for display
        def format_date(dt: Optional[datetime]) -> str:
            if not dt:
                return "-"
            return dt.strftime("%Y.%m.%d")

        def format_datetime(dt: Optional[datetime]) -> str:
            if not dt:
                return "-"
            return dt.strftime("%Y.%m.%d %H:%M")

        return {
            "title": summary.case_title,
            "court_reference": summary.court_reference or "-",
            "client_name": summary.client_name or "-",
            "current_stage": summary.current_stage or "진행 전",
            "progress_percent": summary.progress_percent,
            "completed_stages": [
                {
                    "label": s.stage_label,
                    "date": format_date(s.completed_date)
                }
                for s in summary.completed_stages
            ],
            "next_schedules": [
                {
                    "event": s.event_type,
                    "datetime": format_datetime(s.scheduled_date),
                    "location": s.location or "-"
                }
                for s in summary.next_schedules
            ],
            "evidence_total": summary.evidence_total,
            "evidence_stats": [
                {"category": e.category, "count": e.count}
                for e in summary.evidence_stats
            ],
            "lawyer": {
                "name": summary.lawyer.name if summary.lawyer else "-",
                "phone": summary.lawyer.phone or "-" if summary.lawyer else "-",
                "email": summary.lawyer.email or "-" if summary.lawyer else "-"
            },
            "generated_at": format_datetime(summary.generated_at)
        }
