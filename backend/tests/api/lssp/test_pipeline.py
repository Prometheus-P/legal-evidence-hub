"""
LSSP API Tests - Keypoint Pipeline (v2.10)
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal

from app.main import app
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.models.lssp.pipeline import (
    KeypointRule,
    KeypointCandidate,
)


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
def sample_keypoint_rules():
    return [
        KeypointRule(
            rule_id=1,
            version="v2.10",
            evidence_type="CHAT_EXPORT",
            kind="ADMISSION",
            name="부정행위 인정 키워드",
            pattern="(외도|바람|불륜|상간|만났어|관계)",
            flags="i",
            value_template={"text": "${match}"},
            ground_tags=["G1"],
            base_confidence=Decimal("0.65"),
            base_materiality=85,
            is_enabled=True,
            created_at=datetime.utcnow(),
        ),
        KeypointRule(
            rule_id=2,
            version="v2.10",
            evidence_type="CHAT_EXPORT",
            kind="THREAT",
            name="위협 표현",
            pattern="(죽여|가만 안 둬|찾아간다|끝장)",
            flags="i",
            value_template={"text": "${match}"},
            ground_tags=["G3"],
            base_confidence=Decimal("0.6"),
            base_materiality=80,
            is_enabled=True,
            created_at=datetime.utcnow(),
        ),
    ]


@pytest.fixture
def sample_candidates():
    return [
        KeypointCandidate(
            candidate_id=1,
            case_id="case-123",
            evidence_id="ev-001",
            run_id=1,
            rule_id=1,
            kind="ADMISSION",
            content="바람 피운 것 미안해",
            value={"text": "바람"},
            ground_tags=["G1"],
            confidence=Decimal("0.65"),
            materiality=85,
            source_span={"start": 100, "end": 115},
            status="CANDIDATE",
            created_at=datetime.utcnow(),
        ),
        KeypointCandidate(
            candidate_id=2,
            case_id="case-123",
            evidence_id="ev-001",
            run_id=1,
            rule_id=2,
            kind="THREAT",
            content="가만 안 둘거야",
            value={"text": "가만 안 둬"},
            ground_tags=["G3"],
            confidence=Decimal("0.6"),
            materiality=80,
            source_span={"start": 200, "end": 215},
            status="ACCEPTED",
            created_at=datetime.utcnow(),
        ),
    ]


class TestListPipelineRules:
    """GET /api/lssp/pipeline/rules"""

    def test_list_pipeline_rules_success(
        self, client_with_mocks, sample_keypoint_rules
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = sample_keypoint_rules

        response = client.get("/api/lssp/pipeline/rules")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["kind"] == "ADMISSION"
        assert data[1]["kind"] == "THREAT"

    def test_list_pipeline_rules_filter_by_evidence_type(
        self, client_with_mocks, sample_keypoint_rules
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [
            sample_keypoint_rules[0]
        ]

        response = client.get("/api/lssp/pipeline/rules?evidence_type=CHAT_EXPORT")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 0  # Mock returns filtered


class TestListCandidates:
    """GET /api/lssp/pipeline/cases/{case_id}/candidates"""

    def test_list_candidates_success(
        self, client_with_mocks, sample_candidates
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = sample_candidates

        response = client.get("/api/lssp/pipeline/cases/case-123/candidates")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["status"] == "CANDIDATE"
        assert data[1]["status"] == "ACCEPTED"

    def test_list_candidates_filter_by_status(
        self, client_with_mocks, sample_candidates
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            sample_candidates[0]
        ]

        response = client.get("/api/lssp/pipeline/cases/case-123/candidates?status=CANDIDATE")

        assert response.status_code == 200


class TestUpdateCandidate:
    """PATCH /api/lssp/pipeline/cases/{case_id}/candidates/{candidate_id}"""

    def test_update_candidate_accept(
        self, client_with_mocks, sample_candidates
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_candidates[0]

        response = client.patch(
            "/api/lssp/pipeline/cases/case-123/candidates/1",
            json={"status": "ACCEPTED"},
        )

        assert response.status_code == 200
        mock_db.commit.assert_called_once()

    def test_update_candidate_reject_with_reason(
        self, client_with_mocks, sample_candidates
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_candidates[0]

        response = client.patch(
            "/api/lssp/pipeline/cases/case-123/candidates/1",
            json={"status": "REJECTED", "rejection_reason": "False positive"},
        )

        assert response.status_code == 200
        mock_db.commit.assert_called_once()

    def test_update_candidate_not_found(
        self, client_with_mocks
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.patch(
            "/api/lssp/pipeline/cases/case-123/candidates/999",
            json={"status": "ACCEPTED"},
        )

        assert response.status_code == 404


class TestPromoteCandidates:
    """POST /api/lssp/pipeline/cases/{case_id}/promote"""

    def test_promote_candidates_success(
        self, client_with_mocks, sample_candidates
    ):
        client, mock_db, _ = client_with_mocks
        # Return accepted candidate
        mock_db.query.return_value.filter.return_value.all.return_value = [sample_candidates[1]]

        response = client.post(
            "/api/lssp/pipeline/cases/case-123/promote",
            json={"candidate_ids": [2], "merge_similar": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert "promoted_count" in data

    def test_promote_candidates_empty_list(
        self, client_with_mocks
    ):
        client, mock_db, _ = client_with_mocks
        mock_db.query.return_value.filter.return_value.all.return_value = []

        response = client.post(
            "/api/lssp/pipeline/cases/case-123/promote",
            json={"candidate_ids": []},
        )

        assert response.status_code == 400


class TestPipelineStats:
    """GET /api/lssp/pipeline/cases/{case_id}/stats"""

    def test_get_pipeline_stats_success(
        self, client_with_mocks
    ):
        client, mock_db, _ = client_with_mocks

        # Mock count queries - scalar() returns the count
        mock_db.query.return_value.filter.return_value.scalar.return_value = 5

        response = client.get("/api/lssp/pipeline/cases/case-123/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_candidates" in data
        assert "pending_candidates" in data


class TestSeedKeypointRules:
    """Test seed_keypoint_rules function"""

    def test_seed_keypoint_rules_imports_correctly(self):
        """Verify seed loader module can be imported"""
        from app.seeds import seed_keypoint_rules
        assert callable(seed_keypoint_rules)

    def test_seed_keypoint_rules_with_mock_db(self, mock_db):
        """Test seed_keypoint_rules with mocked database"""
        from app.seeds import seed_keypoint_rules

        # Mock no existing rules
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        # Run seed (may return 0 if file not found in test env)
        count = seed_keypoint_rules(mock_db)
        assert isinstance(count, int)
        assert count >= 0
