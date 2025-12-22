"""
Unit tests for Speaker Mapping validation in EvidenceService
015-evidence-speaker-mapping: T007
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.evidence_service import EvidenceService
from app.db.schemas import SpeakerMappingItem, SpeakerMappingUpdateRequest
from app.middleware import ValidationError


class TestSpeakerMappingValidation:
    """Unit tests for _validate_speaker_mapping method"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return MagicMock()

    @pytest.fixture
    def mock_party(self):
        """Create mock party object"""
        party = MagicMock()
        party.id = "party_001"
        party.case_id = "case_123"
        party.name = "김동우"
        return party

    @pytest.fixture
    def service_with_mocks(self, mock_db, mock_party):
        """Create EvidenceService with mocked repositories"""
        with patch.object(EvidenceService, '__init__', lambda self, db: None):
            service = EvidenceService.__new__(EvidenceService)
            service.db = mock_db
            service.case_repo = MagicMock()
            service.member_repo = MagicMock()
            service.user_repo = MagicMock()
            service.party_repo = MagicMock()
            service.party_repo.get_by_id.return_value = mock_party
            return service

    def test_validate_empty_mapping(self, service_with_mocks):
        """Empty mapping should not raise any error (it will be cleared)"""
        # Empty dict validation is handled before _validate_speaker_mapping is called
        # So this test confirms the method can handle minimal valid input
        speaker_mapping = {
            "나": SpeakerMappingItem(party_id="party_001", party_name="김동우")
        }
        # Should not raise
        service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

    def test_validate_max_speakers_exceeded(self, service_with_mocks):
        """Should raise ValidationError when more than 10 speakers"""
        # Create 11 speakers
        speaker_mapping = {
            f"화자{i}": SpeakerMappingItem(
                party_id=f"party_{i:03d}", party_name=f"인물{i}"
            )
            for i in range(11)
        }

        with pytest.raises(ValidationError) as exc_info:
            service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

        assert "10명" in str(exc_info.value)

    def test_validate_speaker_label_too_long(self, service_with_mocks):
        """Should raise ValidationError when speaker label exceeds 50 characters"""
        long_label = "가" * 51  # 51 characters
        speaker_mapping = {
            long_label: SpeakerMappingItem(party_id="party_001", party_name="김동우")
        }

        with pytest.raises(ValidationError) as exc_info:
            service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

        assert "50자" in str(exc_info.value)

    def test_validate_party_not_found(self, service_with_mocks):
        """Should raise ValidationError when party_id doesn't exist"""
        service_with_mocks.party_repo.get_by_id.return_value = None

        speaker_mapping = {
            "나": SpeakerMappingItem(party_id="nonexistent_party", party_name="김동우")
        }

        with pytest.raises(ValidationError) as exc_info:
            service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

        assert "찾을 수 없습니다" in str(exc_info.value)

    def test_validate_party_wrong_case(self, service_with_mocks, mock_party):
        """Should raise ValidationError when party belongs to different case"""
        # Party belongs to different case
        mock_party.case_id = "different_case_456"

        speaker_mapping = {
            "나": SpeakerMappingItem(party_id="party_001", party_name="김동우")
        }

        with pytest.raises(ValidationError) as exc_info:
            service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

        assert "이 사건에 속하지 않습니다" in str(exc_info.value)

    def test_validate_multiple_speakers_same_party(
        self, service_with_mocks, mock_party
    ):
        """Multiple speakers can map to the same party"""
        # Same party can be referenced by multiple speaker labels
        speaker_mapping = {
            "나": SpeakerMappingItem(party_id="party_001", party_name="김동우"),
            "본인": SpeakerMappingItem(party_id="party_001", party_name="김동우"),
        }

        # Should not raise - same party_id is allowed
        service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

    def test_validate_exactly_10_speakers(self, service_with_mocks, mock_party):
        """Should accept exactly 10 speakers (max limit)"""
        speaker_mapping = {
            f"화자{i}": SpeakerMappingItem(party_id="party_001", party_name="김동우")
            for i in range(10)
        }

        # Should not raise - exactly at limit
        service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")

    def test_validate_exactly_50_char_label(self, service_with_mocks, mock_party):
        """Should accept exactly 50 character speaker label (max limit)"""
        label_50_chars = "가" * 50
        speaker_mapping = {
            label_50_chars: SpeakerMappingItem(
                party_id="party_001", party_name="김동우"
            )
        }

        # Should not raise - exactly at limit
        service_with_mocks._validate_speaker_mapping(speaker_mapping, "case_123")


class TestUpdateSpeakerMapping:
    """Unit tests for update_speaker_mapping method"""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def service_with_mocks(self, mock_db):
        """Create EvidenceService with mocked dependencies"""
        with patch.object(EvidenceService, '__init__', lambda self, db: None):
            service = EvidenceService.__new__(EvidenceService)
            service.db = mock_db
            service.case_repo = MagicMock()
            service.member_repo = MagicMock()
            service.member_repo.has_access.return_value = True
            service.user_repo = MagicMock()
            service.party_repo = MagicMock()

            # Mock party
            mock_party = MagicMock()
            mock_party.case_id = "case_123"
            service.party_repo.get_by_id.return_value = mock_party

            return service

    @patch('app.services.evidence_service.get_evidence_by_id')
    @patch('app.services.evidence_service.update_evidence_speaker_mapping')
    def test_update_speaker_mapping_success(
        self, mock_update_dynamo, mock_get_evidence, service_with_mocks
    ):
        """Successfully update speaker mapping"""
        mock_get_evidence.return_value = {
            "evidence_id": "evt_123",
            "case_id": "case_123",
            "type": "image",
            "filename": "test.jpg",
            "s3_key": "cases/case_123/raw/test.jpg",
            "created_at": "2024-01-01T00:00:00Z",
        }
        mock_update_dynamo.return_value = True

        request = SpeakerMappingUpdateRequest(
            speaker_mapping={
                "나": SpeakerMappingItem(party_id="party_001", party_name="김동우")
            }
        )

        result = service_with_mocks.update_speaker_mapping(
            "evt_123", "user_001", request
        )

        assert result.evidence_id == "evt_123"
        assert result.speaker_mapping is not None
        assert "나" in result.speaker_mapping
        assert result.updated_by == "user_001"

    @patch('app.services.evidence_service.get_evidence_by_id')
    @patch('app.services.evidence_service.update_evidence_speaker_mapping')
    def test_clear_speaker_mapping(
        self, mock_update_dynamo, mock_get_evidence, service_with_mocks
    ):
        """Clear speaker mapping with empty dict"""
        mock_get_evidence.return_value = {
            "evidence_id": "evt_123",
            "case_id": "case_123",
            "type": "image",
            "filename": "test.jpg",
            "s3_key": "cases/case_123/raw/test.jpg",
            "created_at": "2024-01-01T00:00:00Z",
        }
        mock_update_dynamo.return_value = True

        # Empty speaker_mapping to clear
        request = SpeakerMappingUpdateRequest(speaker_mapping={})

        result = service_with_mocks.update_speaker_mapping(
            "evt_123", "user_001", request
        )

        assert result.evidence_id == "evt_123"
        assert result.speaker_mapping is None  # Cleared
        mock_update_dynamo.assert_called_once_with("evt_123", None, "user_001")

    @patch('app.services.evidence_service.get_evidence_by_id')
    def test_update_speaker_mapping_evidence_not_found(
        self, mock_get_evidence, service_with_mocks
    ):
        """Should raise NotFoundError when evidence doesn't exist"""
        from app.middleware import NotFoundError

        mock_get_evidence.return_value = None

        request = SpeakerMappingUpdateRequest(
            speaker_mapping={
                "나": SpeakerMappingItem(party_id="party_001", party_name="김동우")
            }
        )

        with pytest.raises(NotFoundError):
            service_with_mocks.update_speaker_mapping(
                "evt_nonexistent", "user_001", request
            )

    @patch('app.services.evidence_service.get_evidence_by_id')
    def test_update_speaker_mapping_permission_denied(
        self, mock_get_evidence, service_with_mocks
    ):
        """Should raise PermissionError when user doesn't have access"""
        from app.middleware import PermissionError

        mock_get_evidence.return_value = {
            "evidence_id": "evt_123",
            "case_id": "case_123",
            "type": "image",
            "filename": "test.jpg",
            "s3_key": "cases/case_123/raw/test.jpg",
            "created_at": "2024-01-01T00:00:00Z",
        }
        service_with_mocks.member_repo.has_access.return_value = False

        request = SpeakerMappingUpdateRequest(
            speaker_mapping={
                "나": SpeakerMappingItem(party_id="party_001", party_name="김동우")
            }
        )

        with pytest.raises(PermissionError):
            service_with_mocks.update_speaker_mapping("evt_123", "user_001", request)
