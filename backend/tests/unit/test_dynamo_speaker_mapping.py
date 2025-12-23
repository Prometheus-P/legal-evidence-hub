"""
Unit tests for DynamoDB speaker mapping functions
015-evidence-speaker-mapping: T008
"""

import pytest
from unittest.mock import MagicMock, patch

from app.utils.dynamo import (
    update_evidence_speaker_mapping,
    get_evidence_speaker_mapping,
    _serialize_value,
)


class TestUpdateEvidenceSpeakerMapping:
    """Unit tests for update_evidence_speaker_mapping function"""

    @pytest.fixture
    def mock_dynamodb_client(self):
        """Create mock DynamoDB client"""
        client = MagicMock()
        client.update_item.return_value = {}
        return client

    @patch('app.utils.dynamo._get_dynamodb_client')
    def test_set_speaker_mapping(self, mock_get_client, mock_dynamodb_client):
        """Successfully set speaker mapping"""
        mock_get_client.return_value = mock_dynamodb_client

        speaker_mapping = {
            "나": {"party_id": "party_001", "party_name": "김동우"},
            "상대방": {"party_id": "party_002", "party_name": "김도연"},
        }

        result = update_evidence_speaker_mapping(
            evidence_id="evt_123",
            speaker_mapping=speaker_mapping,
            updated_by="user_001"
        )

        assert result is True
        mock_dynamodb_client.update_item.assert_called_once()

        # Verify the update expression includes SET operations
        call_args = mock_dynamodb_client.update_item.call_args
        assert "SET speaker_mapping" in call_args.kwargs["UpdateExpression"]
        assert "speaker_mapping_updated_at" in call_args.kwargs["UpdateExpression"]
        assert "speaker_mapping_updated_by" in call_args.kwargs["UpdateExpression"]

    @patch('app.utils.dynamo._get_dynamodb_client')
    def test_clear_speaker_mapping_with_none(
        self, mock_get_client, mock_dynamodb_client
    ):
        """Clear speaker mapping when None is passed"""
        mock_get_client.return_value = mock_dynamodb_client

        result = update_evidence_speaker_mapping(
            evidence_id="evt_123",
            speaker_mapping=None,
            updated_by="user_001"
        )

        assert result is True
        mock_dynamodb_client.update_item.assert_called_once()

        # Verify REMOVE is used for clearing
        call_args = mock_dynamodb_client.update_item.call_args
        assert "REMOVE speaker_mapping" in call_args.kwargs["UpdateExpression"]

    @patch('app.utils.dynamo._get_dynamodb_client')
    def test_clear_speaker_mapping_with_empty_dict(
        self, mock_get_client, mock_dynamodb_client
    ):
        """Clear speaker mapping when empty dict is passed"""
        mock_get_client.return_value = mock_dynamodb_client

        # Empty dict should be treated as falsy
        result = update_evidence_speaker_mapping(
            evidence_id="evt_123",
            speaker_mapping={},
            updated_by="user_001"
        )

        assert result is True
        # Empty dict is falsy, so REMOVE should be used
        call_args = mock_dynamodb_client.update_item.call_args
        assert "REMOVE speaker_mapping" in call_args.kwargs["UpdateExpression"]

    @patch('app.utils.dynamo._get_dynamodb_client')
    def test_update_speaker_mapping_error(self, mock_get_client, mock_dynamodb_client):
        """Return False when DynamoDB update fails"""
        from botocore.exceptions import ClientError

        mock_get_client.return_value = mock_dynamodb_client
        mock_dynamodb_client.update_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationException", "Message": "Test error"}},
            "UpdateItem"
        )

        speaker_mapping = {
            "나": {"party_id": "party_001", "party_name": "김동우"}
        }

        result = update_evidence_speaker_mapping(
            evidence_id="evt_123",
            speaker_mapping=speaker_mapping,
            updated_by="user_001"
        )

        assert result is False


class TestGetEvidenceSpeakerMapping:
    """Unit tests for get_evidence_speaker_mapping function"""

    @patch('app.utils.dynamo.get_evidence_by_id')
    def test_get_speaker_mapping_exists(self, mock_get_evidence):
        """Return speaker mapping when it exists"""
        mock_get_evidence.return_value = {
            "evidence_id": "evt_123",
            "case_id": "case_123",
            "speaker_mapping": {
                "나": {"party_id": "party_001", "party_name": "김동우"},
                "상대방": {"party_id": "party_002", "party_name": "김도연"},
            }
        }

        result = get_evidence_speaker_mapping("evt_123")

        assert result is not None
        assert "나" in result
        assert result["나"]["party_name"] == "김동우"

    @patch('app.utils.dynamo.get_evidence_by_id')
    def test_get_speaker_mapping_not_set(self, mock_get_evidence):
        """Return None when speaker mapping is not set"""
        mock_get_evidence.return_value = {
            "evidence_id": "evt_123",
            "case_id": "case_123",
            # No speaker_mapping field
        }

        result = get_evidence_speaker_mapping("evt_123")

        assert result is None

    @patch('app.utils.dynamo.get_evidence_by_id')
    def test_get_speaker_mapping_evidence_not_found(self, mock_get_evidence):
        """Return None when evidence doesn't exist"""
        mock_get_evidence.return_value = None

        result = get_evidence_speaker_mapping("evt_nonexistent")

        assert result is None


class TestSerializeValue:
    """Unit tests for _serialize_value helper function"""

    def test_serialize_dict(self):
        """Serialize nested dict correctly"""
        speaker_mapping = {
            "나": {"party_id": "party_001", "party_name": "김동우"}
        }

        result = _serialize_value(speaker_mapping)

        assert "M" in result
        assert "나" in result["M"]
        assert result["M"]["나"]["M"]["party_id"]["S"] == "party_001"
        assert result["M"]["나"]["M"]["party_name"]["S"] == "김동우"

    def test_serialize_string(self):
        """Serialize string correctly"""
        result = _serialize_value("test_string")
        assert result == {"S": "test_string"}

    def test_serialize_none(self):
        """Serialize None correctly"""
        result = _serialize_value(None)
        assert result == {"NULL": True}

    def test_serialize_bool(self):
        """Serialize boolean correctly"""
        assert _serialize_value(True) == {"BOOL": True}
        assert _serialize_value(False) == {"BOOL": False}

    def test_serialize_number(self):
        """Serialize numbers correctly"""
        assert _serialize_value(42) == {"N": "42"}
        assert _serialize_value(3.14) == {"N": "3.14"}

    def test_serialize_list(self):
        """Serialize list correctly"""
        result = _serialize_value(["a", "b", "c"])
        assert "L" in result
        assert len(result["L"]) == 3
        assert result["L"][0] == {"S": "a"}
