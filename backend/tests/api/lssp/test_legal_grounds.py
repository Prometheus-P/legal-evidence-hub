"""
LSSP API Tests - Legal Grounds (v2.01)
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.models.lssp import LegalGround


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "user-123"
    user.role = "lawyer"
    return user


@pytest.fixture
def client_with_mocks(mock_db, mock_user):
    """TestClient with dependency overrides for auth and DB"""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    with TestClient(app) as client:
        yield client, mock_db, mock_user

    app.dependency_overrides.clear()


@pytest.fixture
def sample_legal_grounds():
    return [
        LegalGround(
            code="G1",
            name_ko="배우자의 부정행위",
            elements=["불륜 행위", "성적 관계", "혼인 파탄 원인"],
            limitation={"type": "discovery", "known_within_months": 6, "occurred_within_years": 2},
            notes="최근 2년 내 행위, 사실 인지 후 6개월 내 청구 필요",
            version="2.01",
            created_at=datetime.utcnow(),
        ),
        LegalGround(
            code="G2",
            name_ko="악의의 유기",
            elements=["정당한 이유 없는 동거 거부", "악의성"],
            limitation={"needs_legal_review": True},
            notes="상대방이 정당한 이유 없이 부부 동거를 거부",
            version="2.01",
            created_at=datetime.utcnow(),
        ),
    ]


class TestListLegalGrounds:
    """GET /api/lssp/legal-grounds"""

    def test_list_legal_grounds_success(
        self, client_with_mocks, sample_legal_grounds
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.order_by.return_value.all.return_value = sample_legal_grounds

        response = client.get("/api/lssp/legal-grounds")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["code"] == "G1"
        assert data[1]["code"] == "G2"


class TestGetLegalGround:
    """GET /api/lssp/legal-grounds/{code}"""

    def test_get_legal_ground_success(
        self, client_with_mocks, sample_legal_grounds
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_legal_grounds[0]

        response = client.get("/api/lssp/legal-grounds/G1")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "G1"
        assert data["name_ko"] == "배우자의 부정행위"
        assert "불륜 행위" in data["elements"]

    def test_get_legal_ground_not_found(
        self, client_with_mocks
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.get("/api/lssp/legal-grounds/G99")

        assert response.status_code == 404


class TestCaseLegalGroundLinks:
    """POST/GET/DELETE /api/lssp/legal-grounds/cases/{case_id}/grounds"""

    def test_add_case_legal_ground(
        self, client_with_mocks, sample_legal_grounds
    ):
        client, mock_db, _ = client_with_mocks
        # Ground exists
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_legal_grounds[0],  # Ground lookup
            None,  # Not already linked
        ]

        # Mock refresh to set assessed_at (normally set by DB default)
        def mock_refresh(obj):
            obj.assessed_at = datetime.utcnow()
        mock_db.refresh.side_effect = mock_refresh

        response = client.post(
            "/api/lssp/legal-grounds/cases/case-123/grounds",
            json={
                "ground_code": "G1",
                "is_primary": True,
                "strength_score": "STRONG",
                "notes": "Clear evidence of infidelity",
            },
        )

        assert response.status_code == 201
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_add_case_legal_ground_invalid_code(
        self, client_with_mocks
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(
            "/api/lssp/legal-grounds/cases/case-123/grounds",
            json={"ground_code": "INVALID"},
        )

        assert response.status_code == 400
        # Custom error handler uses {"error": {"message": ...}} format
        resp_json = response.json()
        error_msg = resp_json.get("error", {}).get("message", resp_json.get("detail", ""))
        assert "Invalid ground code" in error_msg

    def test_get_case_legal_grounds(
        self, client_with_mocks, sample_legal_grounds
    ):
        client, mock_db, _ = client_with_mocks

        link = MagicMock()
        link.case_id = "case-123"
        link.ground_code = "G1"
        link.is_primary = True
        link.strength_score = "STRONG"
        link.notes = "Test note"
        link.assessed_by = "user-123"
        link.assessed_at = datetime.utcnow()

        mock_db.query.return_value.filter.return_value.all.return_value = [link]
        mock_db.query.return_value.filter.return_value.first.return_value = sample_legal_grounds[0]

        response = client.get("/api/lssp/legal-grounds/cases/case-123/grounds")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ground_code"] == "G1"
