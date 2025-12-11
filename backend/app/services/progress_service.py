"""Service that aggregates paralegal progress signals."""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from app.db.models import Case, CaseMember, CaseStatus, Evidence, User, UserRole
from app.repositories.case_checklist_repository import CaseChecklistRepository
from app.schemas.progress import (
    AssigneeInfo,
    CaseProgressSummary,
    EvidenceCounts,
    FeedbackChecklistItem,
    ProgressFilter,
)
from app.utils.dynamo import get_evidence_by_case


logger = logging.getLogger(__name__)

CONTRACT_PATH = Path(__file__).resolve().parents[3] / "specs" / "004-paralegal-progress" / "contracts" / "checklist.json"

DEFAULT_FEEDBACK_ITEMS = [
    ("fbk-1", "판례 DB 연동", "판례 DB 문서 연결 상태 점검"),
    ("fbk-2", "AI 역할 강화", "AI 요약·라벨링 품질 체크"),
    ("fbk-3", "증거 정합성 검토", "증거 ID와 업로드 기록 매칭"),
    ("fbk-4", "의뢰인 피드백 반영", "클라이언트 수정 요청 확인"),
]


class ChecklistProvider:
    """Loads checklist templates from the spec contract."""

    def __init__(self, *, contract_path: Optional[Path] = None) -> None:
        self.contract_path = Path(contract_path) if contract_path else CONTRACT_PATH
        self.templates = self._load_contract()

    def _load_contract(self) -> List[dict]:
        try:
            with self.contract_path.open("r", encoding="utf-8") as file:
                records = json.load(file)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("Falling back to default checklist items: %s", exc)
            return [
                {"item_id": item_id, "title": title, "description": desc, "owner": None}
                for item_id, title, desc in DEFAULT_FEEDBACK_ITEMS
            ]

        templates: List[dict] = []
        for record in records:
            templates.append(
                {
                    "item_id": record["id"],
                    "title": record["title"],
                    "description": record.get("description"),
                    "owner": record.get("owner"),
                }
            )
        return templates or [
            {"item_id": item_id, "title": title, "description": desc, "owner": None}
            for item_id, title, desc in DEFAULT_FEEDBACK_ITEMS
        ]

    def get_items(self, case_id: str) -> List[FeedbackChecklistItem]:  # noqa: ARG002
        return [
            FeedbackChecklistItem(
                item_id=item["item_id"],
                title=item["title"],
                description=item.get("description"),
                owner=item.get("owner"),
            )
            for item in self.templates
        ]


@dataclass
class CaseAssignment:
    """Represents a case paired with the paralegal assignee."""

    case: Case
    assignee: User


class ProgressService:
    """Aggregates case metrics for the paralegal dashboard."""

    def __init__(
        self,
        session: Session,
        *,
        checklist_provider: Optional[ChecklistProvider] = None,
        checklist_repository: Optional[CaseChecklistRepository] = None,
        evidence_fetcher: Optional[Callable[[str], List[dict]]] = None,
        case_loader: Optional[Callable[[str, Optional[ProgressFilter]], List[CaseAssignment]]] = None,
    ):
        self.session = session
        self.checklist_provider = checklist_provider or ChecklistProvider()
        self.checklist_repository = checklist_repository or CaseChecklistRepository(session)
        self.evidence_fetcher = evidence_fetcher
        self.case_loader = case_loader or self._load_assignments

    def list_progress(self, user_id: str, filters: Optional[ProgressFilter] = None) -> List[CaseProgressSummary]:
        """Return summarized progress for cases assigned to the given user."""
        filters = filters or ProgressFilter()
        assignments = self.case_loader(user_id, filters)
        summaries: List[CaseProgressSummary] = []

        for assignment in assignments:
            evidence = self._get_evidence_records(assignment.case.id)
            checklist = self._hydrate_checklist(assignment.case.id)
            summary = self._build_summary(assignment, evidence, checklist)

            if filters.blocked_only and not summary.is_blocked:
                continue

            summaries.append(summary)

        return summaries

    def update_checklist_item(
        self,
        *,
        case_id: str,
        item_id: str,
        status: str,
        updated_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> FeedbackChecklistItem:
        allowed_statuses = {"pending", "done"}
        normalized_status = status.lower()
        if normalized_status not in allowed_statuses:
            raise ValueError("Invalid checklist status")

        templates = {item.item_id: item for item in self.checklist_provider.get_items(case_id)}
        template = templates.get(item_id)
        if template is None:
            raise ValueError("Checklist item not found")

        record = self.checklist_repository.set_status(
            case_id=case_id,
            item_id=item_id,
            status=normalized_status,
            updated_by=updated_by,
            notes=notes,
        )

        return template.model_copy(
            update={
                "status": record.status,
                "notes": record.notes,
                "updated_by": record.updated_by,
                "updated_at": record.updated_at,
            }
        )

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _build_summary(
        self,
        assignment: CaseAssignment,
        evidence: List[dict],
        checklist: List[FeedbackChecklistItem],
    ) -> CaseProgressSummary:
        case = assignment.case
        assignee = assignment.assignee

        counts = self._count_evidence(evidence)
        ai_status, ai_updated = self._derive_ai_status(evidence, counts)
        outstanding = sum(1 for item in checklist if item.status.lower() != "done")
        blocked_reason = self._determine_blocked_reason(counts, outstanding)

        return CaseProgressSummary(
            case_id=case.id,
            title=case.title,
            client_name=getattr(case, "client_name", None),
            status=case.status if isinstance(case.status, CaseStatus) else CaseStatus(case.status),
            assignee=AssigneeInfo(id=assignee.id, name=getattr(assignee, "name", ""), email=getattr(assignee, "email", None)),
            updated_at=case.updated_at or case.created_at,
            evidence_counts=counts,
            ai_status=ai_status,
            ai_last_updated=ai_updated,
            outstanding_feedback_count=outstanding,
            feedback_items=checklist,
            is_blocked=blocked_reason is not None,
            blocked_reason=blocked_reason,
        )

    def _hydrate_checklist(self, case_id: str) -> List[FeedbackChecklistItem]:
        base_items = self.checklist_provider.get_items(case_id)
        if not base_items:
            return []
        status_map = self.checklist_repository.get_status_map(case_id)
        if not status_map:
            return base_items

        merged: List[FeedbackChecklistItem] = []
        for item in base_items:
            record = status_map.get(item.item_id)
            if not record:
                merged.append(item)
                continue
            merged.append(
                item.model_copy(
                    update={
                        "status": record.status,
                        "notes": getattr(record, "notes", None),
                        "updated_by": getattr(record, "updated_by", None),
                        "updated_at": record.updated_at,
                    }
                )
            )
        return merged

    def _get_evidence_records(self, case_id: str) -> List[dict]:
        if self.evidence_fetcher is not None:
            return self.evidence_fetcher(case_id) or []

        records = self._fetch_evidence_from_db(case_id)
        if records:
            return records

        try:  # pragma: no cover - exercised in integration environments
            return get_evidence_by_case(case_id)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to fetch Dynamo evidence for %s: %s", case_id, exc)
            return []

    def _fetch_evidence_from_db(self, case_id: str) -> List[dict]:
        rows = (
            self.session.query(Evidence)
            .filter(Evidence.case_id == case_id)
            .all()
        )
        evidence: List[dict] = []
        for row in rows:
            evidence.append(
                {
                    "status": row.status,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
            )
        return evidence

    def _count_evidence(self, evidence: List[dict]) -> EvidenceCounts:
        counter = Counter()
        for item in evidence:
            status = (item.get("status") or "").lower()
            if status in {"pending", "uploaded", "processing", "completed", "failed"}:
                counter[status] += 1
        return EvidenceCounts(
            pending=counter["pending"],
            uploaded=counter["uploaded"],
            processing=counter["processing"],
            completed=counter["completed"],
            failed=counter["failed"],
        )

    def _derive_ai_status(self, evidence: List[dict], counts: EvidenceCounts) -> tuple[str, Optional[datetime]]:
        if counts.failed:
            status = "failed"
        elif counts.processing:
            status = "processing"
        elif counts.completed:
            status = "ready"
        elif counts.uploaded:
            status = "uploaded"
        else:
            status = "pending"

        timestamps = []
        for item in evidence:
            ts = item.get("updated_at") or item.get("created_at")
            if isinstance(ts, datetime):
                timestamps.append(ts)
            elif isinstance(ts, str):
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except ValueError:
                    continue

        last_updated = max(timestamps) if timestamps else None
        return status, last_updated

    def _determine_blocked_reason(self, counts: EvidenceCounts, outstanding_feedback: int) -> Optional[str]:
        if counts.failed:
            return "evidence_failed"
        if outstanding_feedback > 0 and counts.completed == 0:
            return "feedback_pending"
        if counts.processing > 0 and counts.completed == 0:
            return "ai_processing"
        return None

    def _load_assignments(self, user_id: str, filters: Optional[ProgressFilter] = None) -> List[CaseAssignment]:
        """Default loader hitting the SQL database."""
        filters = filters or ProgressFilter()
        query = (
            self.session.query(Case, User, CaseMember)
            .join(CaseMember, Case.id == CaseMember.case_id)
            .join(User, CaseMember.user_id == User.id)
            .filter(User.role == UserRole.STAFF)
        )

        if filters.assignee_id:
            query = query.filter(CaseMember.user_id == filters.assignee_id)
        else:
            query = query.filter(CaseMember.user_id == user_id)

        rows = query.all()
        assignments = [CaseAssignment(case=row[0], assignee=row[1]) for row in rows]
        return assignments
