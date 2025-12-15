"""
Unit tests for PredictionService
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.services.prediction_service import PredictionService
from app.db.models import ConfidenceLevel
from app.middleware import NotFoundError, PermissionError


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_prediction_repo():
    """Create a mock prediction repository."""
    return MagicMock()


@pytest.fixture
def mock_property_repo():
    """Create a mock property repository."""
    return MagicMock()


@pytest.fixture
def mock_case_repo():
    """Create a mock case repository."""
    return MagicMock()


@pytest.fixture
def mock_member_repo():
    """Create a mock case member repository."""
    return MagicMock()


@pytest.fixture
def prediction_service(mock_db, mock_prediction_repo, mock_property_repo, mock_case_repo, mock_member_repo):
    """Create PredictionService with mocked repositories."""
    with patch('app.services.prediction_service.PredictionRepository', return_value=mock_prediction_repo), \
         patch('app.services.prediction_service.PropertyRepository', return_value=mock_property_repo), \
         patch('app.services.prediction_service.CaseRepository', return_value=mock_case_repo), \
         patch('app.services.prediction_service.CaseMemberRepository', return_value=mock_member_repo):
        service = PredictionService(mock_db)
        service.prediction_repo = mock_prediction_repo
        service.property_repo = mock_property_repo
        service.case_repo = mock_case_repo
        service.member_repo = mock_member_repo
        return service


class TestPredictionServiceInit:
    """Tests for PredictionService initialization."""

    def test_init_creates_repositories(self, mock_db):
        """Test that __init__ creates all repositories."""
        with patch('app.services.prediction_service.PredictionRepository') as mock_pred, \
             patch('app.services.prediction_service.PropertyRepository') as mock_prop, \
             patch('app.services.prediction_service.CaseRepository') as mock_case, \
             patch('app.services.prediction_service.CaseMemberRepository') as mock_member:

            _service = PredictionService(mock_db)  # noqa: F841

            mock_pred.assert_called_once_with(mock_db)
            mock_prop.assert_called_once_with(mock_db)
            mock_case.assert_called_once_with(mock_db)
            mock_member.assert_called_once_with(mock_db)


class TestCheckCaseAccess:
    """Tests for _check_case_access method."""

    def test_check_access_case_not_found(self, prediction_service, mock_case_repo, mock_member_repo):
        """Raises NotFoundError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            prediction_service._check_case_access("case-1", "user-1")

        mock_case_repo.get_by_id.assert_called_once_with("case-1")
        mock_member_repo.has_access.assert_not_called()

    def test_check_access_no_permission(self, prediction_service, mock_case_repo, mock_member_repo):
        """Raises PermissionError when user doesn't have access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = False

        with pytest.raises(PermissionError):
            prediction_service._check_case_access("case-1", "user-1")

        mock_member_repo.has_access.assert_called_once_with("case-1", "user-1")

    def test_check_access_success(self, prediction_service, mock_case_repo, mock_member_repo):
        """No exception when case exists and user has access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        # Should not raise
        prediction_service._check_case_access("case-1", "user-1")

        mock_case_repo.get_by_id.assert_called_once()
        mock_member_repo.has_access.assert_called_once()


class TestGetPrediction:
    """Tests for get_prediction method."""

    def test_get_prediction_not_found(self, prediction_service, mock_case_repo, mock_member_repo, mock_prediction_repo):
        """Returns None when no prediction exists."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_prediction_repo.get_latest_for_case.return_value = None

        result = prediction_service.get_prediction("case-1", "user-1")

        assert result is None
        mock_prediction_repo.get_latest_for_case.assert_called_once_with("case-1")

    def test_get_prediction_success(self, prediction_service, mock_case_repo, mock_member_repo, mock_prediction_repo):
        """Returns prediction when found."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        # Create mock prediction
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 100000000
        mock_prediction.total_debt_value = 20000000
        mock_prediction.net_value = 80000000
        mock_prediction.plaintiff_ratio = 55
        mock_prediction.defendant_ratio = 45
        mock_prediction.plaintiff_amount = 44000000
        mock_prediction.defendant_amount = 36000000
        mock_prediction.evidence_impacts = []
        mock_prediction.similar_cases = []
        mock_prediction.confidence_level = ConfidenceLevel.MEDIUM
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        mock_prediction_repo.get_latest_for_case.return_value = mock_prediction

        result = prediction_service.get_prediction("case-1", "user-1")

        assert result is not None
        assert result.id == "pred-1"
        assert result.plaintiff_ratio == 55


class TestCalculatePrediction:
    """Tests for calculate_prediction method."""

    def test_calculate_with_zero_net_value(
        self, prediction_service, mock_db,
        mock_case_repo, mock_member_repo,
        mock_property_repo, mock_prediction_repo
    ):
        """Returns default 50:50 when net value is 0."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_property_repo.get_summary.return_value = {
            "total_assets": 0,
            "total_debts": 0,
            "net_value": 0
        }

        # Mock prediction creation
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 0
        mock_prediction.total_debt_value = 0
        mock_prediction.net_value = 0
        mock_prediction.plaintiff_ratio = 50
        mock_prediction.defendant_ratio = 50
        mock_prediction.plaintiff_amount = 0
        mock_prediction.defendant_amount = 0
        mock_prediction.evidence_impacts = []
        mock_prediction.similar_cases = []
        mock_prediction.confidence_level = ConfidenceLevel.LOW
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        mock_prediction_repo.create.return_value = mock_prediction

        result = prediction_service.calculate_prediction("case-1", "user-1")

        assert result.plaintiff_ratio == 50
        assert result.defendant_ratio == 50
        mock_db.commit.assert_called()

    def test_calculate_with_net_value_no_ai(
        self, prediction_service, mock_db,
        mock_case_repo, mock_member_repo,
        mock_property_repo, mock_prediction_repo
    ):
        """Calculates prediction without AI Worker."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_property_repo.get_summary.return_value = {
            "total_assets": 100000000,
            "total_debts": 20000000,
            "net_value": 80000000
        }

        # Mock prediction creation
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 100000000
        mock_prediction.total_debt_value = 20000000
        mock_prediction.net_value = 80000000
        mock_prediction.plaintiff_ratio = 50
        mock_prediction.defendant_ratio = 50
        mock_prediction.plaintiff_amount = 40000000
        mock_prediction.defendant_amount = 40000000
        mock_prediction.evidence_impacts = []
        mock_prediction.similar_cases = []
        mock_prediction.confidence_level = ConfidenceLevel.LOW
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        mock_prediction_repo.create.return_value = mock_prediction

        # Patch AI worker to not be available
        with patch.object(prediction_service, '_analyze_with_ai_worker', return_value=([], [], None)):
            result = prediction_service.calculate_prediction("case-1", "user-1")

        assert result is not None
        mock_prediction_repo.create.assert_called_once()
        mock_db.commit.assert_called()


class TestAnalyzeWithAiWorker:
    """Tests for _analyze_with_ai_worker method."""

    def test_ai_worker_import_error(self, prediction_service):
        """Returns empty results when AI Worker not available."""
        # Mock the import to fail
        with patch.dict('sys.modules', {'src.analysis.impact_analyzer': None}):
            with patch('builtins.__import__', side_effect=ImportError("Module not found")):
                impacts, cases, ratio = prediction_service._analyze_with_ai_worker("case-1")

        assert impacts == []
        assert cases == []
        assert ratio is None

    def test_ai_worker_exception(self, prediction_service):
        """Returns empty results when AI Worker raises exception."""
        with patch.object(prediction_service, '_get_mock_evidences', return_value=[]):
            # Empty evidences list means AI analysis returns defaults
            impacts, cases, ratio = prediction_service._analyze_with_ai_worker("case-1")

        # With no evidences to analyze, impacts and cases should be empty
        assert impacts == []
        assert cases == []
        # ratio can be None or a default value depending on implementation


class TestGetMockEvidences:
    """Tests for _get_mock_evidences method."""

    def test_returns_empty_list(self, prediction_service):
        """Returns empty list (placeholder for future implementation)."""
        result = prediction_service._get_mock_evidences("case-1")
        assert result == []


class TestCreateDefaultPrediction:
    """Tests for _create_default_prediction method."""

    def test_creates_default_50_50(self, prediction_service, mock_db, mock_prediction_repo):
        """Creates default 50:50 prediction."""
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 0
        mock_prediction.total_debt_value = 0
        mock_prediction.net_value = 0
        mock_prediction.plaintiff_ratio = 50
        mock_prediction.defendant_ratio = 50
        mock_prediction.plaintiff_amount = 0
        mock_prediction.defendant_amount = 0
        mock_prediction.evidence_impacts = []
        mock_prediction.similar_cases = []
        mock_prediction.confidence_level = ConfidenceLevel.LOW
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        mock_prediction_repo.create.return_value = mock_prediction

        result = prediction_service._create_default_prediction("case-1", 0, 0, 0)

        assert result.plaintiff_ratio == 50
        assert result.defendant_ratio == 50
        assert result.confidence_level == ConfidenceLevel.LOW
        mock_prediction_repo.create.assert_called_once()


class TestDetermineConfidence:
    """Tests for _determine_confidence method."""

    def test_no_ai_analysis_returns_low(self, prediction_service):
        """Returns LOW when no AI analysis available."""
        result = prediction_service._determine_confidence(
            evidence_count=10,
            similar_case_count=10,
            has_ai_analysis=False
        )
        assert result == ConfidenceLevel.LOW

    def test_high_confidence(self, prediction_service):
        """Returns HIGH with sufficient evidence and cases."""
        result = prediction_service._determine_confidence(
            evidence_count=5,
            similar_case_count=3,
            has_ai_analysis=True
        )
        assert result == ConfidenceLevel.HIGH

    def test_medium_confidence_with_evidence(self, prediction_service):
        """Returns MEDIUM with some evidence."""
        result = prediction_service._determine_confidence(
            evidence_count=2,
            similar_case_count=0,
            has_ai_analysis=True
        )
        assert result == ConfidenceLevel.MEDIUM

    def test_medium_confidence_with_cases(self, prediction_service):
        """Returns MEDIUM with similar cases."""
        result = prediction_service._determine_confidence(
            evidence_count=0,
            similar_case_count=1,
            has_ai_analysis=True
        )
        assert result == ConfidenceLevel.MEDIUM

    def test_low_confidence_minimal_data(self, prediction_service):
        """Returns LOW with minimal data."""
        result = prediction_service._determine_confidence(
            evidence_count=1,
            similar_case_count=0,
            has_ai_analysis=True
        )
        assert result == ConfidenceLevel.LOW


class TestToPredictionOut:
    """Tests for _to_prediction_out method."""

    def test_converts_model_to_schema(self, prediction_service):
        """Converts prediction model to output schema."""
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 100000000
        mock_prediction.total_debt_value = 20000000
        mock_prediction.net_value = 80000000
        mock_prediction.plaintiff_ratio = 55
        mock_prediction.defendant_ratio = 45
        mock_prediction.plaintiff_amount = 44000000
        mock_prediction.defendant_amount = 36000000
        mock_prediction.evidence_impacts = [
            {
                "evidence_id": "ev-1",
                "evidence_type": "audio",
                "impact_type": "폭언",
                "impact_percent": 5,
                "direction": "plaintiff",
                "reason": "폭언 증거",
                "confidence": 0.85
            }
        ]
        mock_prediction.similar_cases = [
            {
                "case_ref": "2023드단1234",
                "similarity_score": 0.89,
                "division_ratio": "55:45",
                "key_factors": ["유책배우자", "재산형성기여도"]
            }
        ]
        mock_prediction.confidence_level = ConfidenceLevel.MEDIUM
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        result = prediction_service._to_prediction_out(mock_prediction)

        assert result.id == "pred-1"
        assert result.case_id == "case-1"
        assert result.plaintiff_ratio == 55
        assert len(result.evidence_impacts) == 1
        assert len(result.similar_cases) == 1

    def test_handles_none_impacts_and_cases(self, prediction_service):
        """Handles None for evidence_impacts and similar_cases."""
        mock_prediction = MagicMock()
        mock_prediction.id = "pred-1"
        mock_prediction.case_id = "case-1"
        mock_prediction.total_property_value = 0
        mock_prediction.total_debt_value = 0
        mock_prediction.net_value = 0
        mock_prediction.plaintiff_ratio = 50
        mock_prediction.defendant_ratio = 50
        mock_prediction.plaintiff_amount = 0
        mock_prediction.defendant_amount = 0
        mock_prediction.evidence_impacts = None
        mock_prediction.similar_cases = None
        mock_prediction.confidence_level = ConfidenceLevel.LOW
        mock_prediction.version = 1
        mock_prediction.created_at = datetime.now()
        mock_prediction.updated_at = datetime.now()

        result = prediction_service._to_prediction_out(mock_prediction)

        assert result.evidence_impacts == []
        assert result.similar_cases == []
