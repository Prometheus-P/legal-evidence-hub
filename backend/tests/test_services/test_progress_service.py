"""Tests for ProgressService aggregation logic."""

from pathlib import Path
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import List, Optional
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import (
    Base,
    Case,
    CaseMember,
    CaseMemberRole,
    CaseStatus,
    Evidence,
    User,
    UserStatus,
    UserRole,
)
from app.schemas.progress import (
    EvidenceCounts,
    FeedbackChecklistItem,
    ProgressFilter,
)
from app.services.progress_service import CaseAssignment, ChecklistProvider, ProgressService


def _dummy_case(case_id: str, status: CaseStatus = CaseStatus.IN_PROGRESS) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=case_id,
        title=f"Case {case_id}",
        status=status,
        client_name="홍길동",
        updated_at=now,
        created_at=now - timedelta(days=3),
    )


def _dummy_user(user_id: str, name: str = "Paralegal Kim") -> SimpleNamespace:
    return SimpleNamespace(id=user_id, name=name, email=f"{user_id}@leh.test")


@pytest.fixture()
def checklist_provider():
    class StubProvider:
        def get_items(self, case_id: str) -> List[FeedbackChecklistItem]:
            return [
                FeedbackChecklistItem(
                    item_id="fbk-1",
                    title="판례 DB 연동",
                    status="pending",
                    description="Ensure 판례 DB is linked",
                ),
                FeedbackChecklistItem(
                    item_id="fbk-2",
                    title="AI 역할 강화",
                    status="pending",
                    description="Double-check AI summaries",
                ),
            ]

    return StubProvider()


@pytest.fixture()
def evidence_fetcher():
    def _fetch(case_id: str):
        if case_id == "case_ready":
            return [
                {"status": "completed", "updated_at": "2024-12-01T10:00:00+00:00"},
                {"status": "completed", "updated_at": "2024-12-01T11:00:00+00:00"},
            ]
        if case_id == "case_blocked":
            return [
                {"status": "failed", "error_message": "ocr timeout"},
                {"status": "processing"},
            ]
        return []

    return _fetch


@pytest.fixture()
def case_loader():
    def _load(user_id: str, filters: Optional[ProgressFilter] = None):
        return [
            CaseAssignment(
                case=_dummy_case("case_ready", CaseStatus.OPEN),
                assignee=_dummy_user("staff_1"),
            ),
            CaseAssignment(
                case=_dummy_case("case_blocked", CaseStatus.IN_PROGRESS),
                assignee=_dummy_user("staff_2"),
            ),
        ]

    return _load


@pytest.fixture()
def checklist_repository():
    class StubRepository:
        def __init__(self):
            self.calls = []

        def get_status_map(self, case_id: str):
            if case_id == "case_ready":
                return {
                    "fbk-1": SimpleNamespace(
                        status="done",
                        updated_at=datetime(2024, 12, 1, 9, 0, tzinfo=timezone.utc),
                        notes="판례 확인",
                    )
                }
            return {}

        def set_status(self, *, case_id: str, item_id: str, status: str, updated_by: Optional[str] = None, notes: Optional[str] = None):
            self.calls.append((case_id, item_id, status, updated_by, notes))
            return SimpleNamespace(
                case_id=case_id,
                item_id=item_id,
                status=status,
                notes=notes,
                updated_by=updated_by,
                updated_at=datetime(2024, 12, 2, 9, 0, tzinfo=timezone.utc),
            )

    return StubRepository()


@pytest.fixture()
def service(checklist_provider, checklist_repository, evidence_fetcher, case_loader):
    session = MagicMock()
    return ProgressService(
        session=session,
        evidence_fetcher=evidence_fetcher,
        checklist_provider=checklist_provider,
        checklist_repository=checklist_repository,
        case_loader=case_loader,
    )


def test_list_progress_returns_case_summaries(service):
    progress = service.list_progress(user_id="staff_1")

    assert len(progress) == 2
    ready_case = next(item for item in progress if item.case_id == "case_ready")
    assert ready_case.assignee.name == "Paralegal Kim"
    assert ready_case.evidence_counts == EvidenceCounts(completed=2, failed=0, processing=0, pending=0, uploaded=0)
    assert ready_case.ai_status == "ready"
    assert ready_case.outstanding_feedback_count == 1  # one pending item


def test_list_progress_flags_blocked_cases(service):
    progress = service.list_progress(user_id="staff_1", filters=ProgressFilter(blocked_only=True))

    assert len(progress) == 1
    blocked = progress[0]
    assert blocked.case_id == "case_blocked"
    assert blocked.is_blocked is True
    assert blocked.blocked_reason == "evidence_failed"
    assert blocked.evidence_counts.failed == 1


def test_list_progress_empty_when_no_cases(service):
    service.case_loader = lambda user_id, filters=None: []

    assert service.list_progress(user_id="staff_1") == []


def test_checklist_provider_loads_contract_file():
    contract_path = (
        Path(__file__).resolve().parents[3] / "specs" / "004-paralegal-progress" / "contracts" / "checklist.json"
    )
    provider = ChecklistProvider(contract_path=contract_path)

    items = provider.get_items("case_x")

    assert len(items) == 16
    assert items[0].item_id == "fbk-1"
    assert items[-1].title == "데모 리포트 스냅샷"


def test_progress_service_merges_persisted_checklist_statuses(checklist_repository, checklist_provider, evidence_fetcher, case_loader):
    session = MagicMock()
    service = ProgressService(
        session=session,
        evidence_fetcher=evidence_fetcher,
        checklist_provider=checklist_provider,
        checklist_repository=checklist_repository,
        case_loader=case_loader,
    )

    ready_case = next(item for item in service.list_progress(user_id="staff_1") if item.case_id == "case_ready")

    statuses = {item.item_id: item.status for item in ready_case.feedback_items}
    assert statuses["fbk-1"] == "done"
    assert statuses["fbk-2"] == "pending"


def test_update_checklist_item_uses_repository(checklist_repository, checklist_provider):
    session = MagicMock()
    service = ProgressService(
        session=session,
        checklist_provider=checklist_provider,
        checklist_repository=checklist_repository,
    )

    updated = service.update_checklist_item(
        case_id="case_ready",
        item_id="fbk-1",
        status="done",
        updated_by="staff_1",
        notes="완료",
    )

    assert checklist_repository.calls[-1] == ("case_ready", "fbk-1", "done", "staff_1", "완료")
    assert updated.status == "done"
    assert updated.notes == "완료"


def test_progress_service_reads_evidence_from_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    now = datetime.now(timezone.utc)
    staff = User(
        id="staff_db",
        email="staff@example.com",
        hashed_password="test",
        name="Staff DB",
        role=UserRole.STAFF,
        status=UserStatus.ACTIVE,
    )
    lawyer = User(
        id="lawyer_db",
        email="lawyer@example.com",
        hashed_password="test",
        name="Lawyer DB",
        role=UserRole.LAWYER,
        status=UserStatus.ACTIVE,
    )
    case = Case(
        id="case_db",
        title="실데이터 케이스",
        client_name="홍길동",
        status=CaseStatus.OPEN,
        created_by=lawyer.id,
    )
    membership = CaseMember(case_id=case.id, user_id=staff.id, role=CaseMemberRole.MEMBER)
    evidence_rows = [
        Evidence(
            id="ev1",
            case_id=case.id,
            file_name="doc1.pdf",
            s3_key="s3://bucket/doc1.pdf",
            status="completed",
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=5),
        ),
        Evidence(
            id="ev2",
            case_id=case.id,
            file_name="doc2.pdf",
            s3_key="s3://bucket/doc2.pdf",
            status="processing",
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=3),
        ),
        Evidence(
            id="ev3",
            case_id=case.id,
            file_name="doc3.pdf",
            s3_key="s3://bucket/doc3.pdf",
            status="failed",
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=1),
        ),
    ]
    session.add_all([staff, lawyer, case, membership, *evidence_rows])
    session.commit()

    class StubProvider:
        def get_items(self, case_id: str) -> List[FeedbackChecklistItem]:
            return [
                FeedbackChecklistItem(item_id="fbk-1", title="판례 DB 연동", status="pending"),
            ]

    class StubChecklistRepo:
        def get_status_map(self, case_id: str):
            return {}

    service = ProgressService(
        session=session,
        checklist_provider=StubProvider(),
        checklist_repository=StubChecklistRepo(),
    )

    progress = service.list_progress(user_id=staff.id)

    assert len(progress) == 1
    summary = progress[0]
    assert summary.case_id == case.id
    assert summary.evidence_counts.completed == 1
    assert summary.evidence_counts.processing == 1
    assert summary.evidence_counts.failed == 1
    assert summary.ai_status == "failed"

    session.close()
    Base.metadata.drop_all(bind=engine)
