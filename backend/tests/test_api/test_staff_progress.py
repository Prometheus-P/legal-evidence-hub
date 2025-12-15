"""API tests for staff progress endpoint."""

from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from datetime import datetime, timezone

from app.api.staff_progress import router
from app.core.dependencies import get_current_user
from app.db.models import CaseStatus, UserRole
from app.db.session import get_db
from app.schemas.progress import (
    AssigneeInfo,
    CaseProgressSummary,
    EvidenceCounts,
    FeedbackChecklistItem,
)


@pytest.fixture()
def api_client():
    app = FastAPI()
    app.include_router(router)

    user = SimpleNamespace(id="staff_1", role=UserRole.STAFF, name="Paralegal Kim", email="staff@example.com")

    def override_user():
        return user

    def override_db():
        yield MagicMock()

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as client:
        yield client, user


def _sample_summary() -> CaseProgressSummary:
    timestamp = datetime(2024, 12, 1, 10, 0, tzinfo=timezone.utc)
    return CaseProgressSummary(
        case_id="case_123",
        title="Test Case",
        client_name="홍길동",
        status=CaseStatus.IN_PROGRESS,
        assignee=AssigneeInfo(id="staff_1", name="Paralegal Kim"),
        updated_at=timestamp,
        evidence_counts=EvidenceCounts(completed=1, processing=1, failed=0, pending=0, uploaded=0),
        ai_status="processing",
        ai_last_updated=timestamp,
        outstanding_feedback_count=1,
        feedback_items=[
            FeedbackChecklistItem(item_id="fbk-1", title="판례 DB 연동", status="pending"),
        ],
        is_blocked=True,
        blocked_reason="feedback_pending",
    )


def test_staff_progress_returns_payload(api_client):
    client, user = api_client
    with patch("app.api.staff_progress.ProgressService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.list_progress.return_value = [_sample_summary()]
        mock_service_cls.return_value = mock_service

        response = client.get("/staff/progress")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["case_id"] == "case_123"
        mock_service.list_progress.assert_called_once_with(user.id, filters=ANY)


def test_staff_progress_filters_blocked(api_client):
    client, user = api_client
    with patch("app.api.staff_progress.ProgressService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.list_progress.return_value = []
        mock_service_cls.return_value = mock_service

        response = client.get("/staff/progress?blocked_only=true")
        assert response.status_code == 200
        mock_service.list_progress.assert_called_once()
        called_filters = mock_service.list_progress.call_args.kwargs["filters"]
        assert called_filters.blocked_only is True


def test_staff_progress_rejects_external_user():
    """Test that external users (CLIENT role) are rejected with 403."""
    from fastapi.responses import JSONResponse
    from app.middleware.error_handler import PermissionError as LEHPermissionError

    # Create a fresh app with CLIENT user to avoid fixture caching issues
    app = FastAPI()
    app.include_router(router)

    # Add exception handler for PermissionError (needed since we're using a fresh app)
    @app.exception_handler(LEHPermissionError)
    async def permission_error_handler(request, exc):
        return JSONResponse(
            status_code=403,
            content={"detail": exc.message}
        )

    # Create user with CLIENT role
    client_user = SimpleNamespace(
        id="client_1",
        role=UserRole.CLIENT,
        name="Client User",
        email="client@example.com"
    )

    def override_client_user():
        return client_user

    def override_db():
        yield MagicMock()

    app.dependency_overrides[get_current_user] = override_client_user
    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as test_client:
        response = test_client.get("/staff/progress")
        assert response.status_code == 403


def test_staff_progress_updates_checklist_item(api_client):
    client, user = api_client
    with patch("app.api.staff_progress.ProgressService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.update_checklist_item.return_value = FeedbackChecklistItem(
            item_id="fbk-1",
            title="판례 DB 연동",
            status="done",
            owner="Ops",
            notes="완료",
        )
        mock_service_cls.return_value = mock_service

        response = client.patch("/staff/progress/case_123/checklist/fbk-1", json={"status": "done", "notes": "완료"})

        assert response.status_code == 200
        mock_service.update_checklist_item.assert_called_once_with(
            case_id="case_123",
            item_id="fbk-1",
            status="done",
            updated_by=user.id,
            notes="완료",
        )
