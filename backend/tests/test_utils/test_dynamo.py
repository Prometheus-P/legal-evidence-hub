"""Unit tests for DynamoDB utility helpers."""

from datetime import datetime, timezone

import pytest
from botocore.exceptions import ClientError

from app.utils import dynamo


@pytest.fixture(autouse=True)
def reset_dynamo_client():
    """Ensure singleton client is reset between tests."""
    dynamo._dynamodb_client = None
    yield
    dynamo._dynamodb_client = None


def _mock_items():
    """Helper to build serialized DynamoDB records."""
    return [
        {
            "evidence_id": {"S": "ev_old"},
            "case_id": {"S": "case_1"},
            "created_at": {"S": "2024-01-01T00:00:00Z"},
            "score": {"N": "0.11"},
        },
        {
            "evidence_id": {"S": "ev_new"},
            "case_id": {"S": "case_1"},
            "created_at": {"S": "2024-03-01T00:00:00Z"},
            "score": {"N": "0.95"},
        },
    ]


def test_serialize_and_deserialize_round_trip():
    """Serializers should faithfully convert nested structures."""
    payload = {
        "none": None,
        "bool": True,
        "int": 2,
        "float": 2.5,
        "str": "hello",
        "list": [1, "two", {"nested": False}],
        "dict": {"a": 1, "b": ["x", "y"]},
    }

    serialized = dynamo._serialize_to_dynamodb(payload)
    round_trip = dynamo._deserialize_dynamodb_item(serialized)
    assert round_trip == {
        **payload,
        "float": 2.5,
    }


def test_get_evidence_by_case_returns_sorted_deserialized(mock_aws_services):
    """Query results should be deserialized and sorted by created_at desc."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()
    mock_dynamodb.query.return_value = {"Items": _mock_items()}

    results = dynamo.get_evidence_by_case("case_1")

    mock_dynamodb.query.assert_called_once()
    assert results[0]["evidence_id"] == "ev_new"
    assert results[1]["evidence_id"] == "ev_old"
    assert results[0]["score"] == 0.95


def test_get_evidence_by_id_returns_none_when_not_found(mock_aws_services):
    """Missing records should return None."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()
    mock_dynamodb.get_item.return_value = {}

    assert dynamo.get_evidence_by_id("ev_missing") is None


def test_put_evidence_metadata_normalizes_fields(monkeypatch, mock_aws_services):
    """put_evidence_metadata should upsert normalized payload."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()

    fixed_dt = datetime(2024, 4, 1, tzinfo=timezone.utc)

    class FakeDatetime:
        @classmethod
        def now(cls, tz=None):
            return fixed_dt

    monkeypatch.setattr(dynamo, "datetime", FakeDatetime)

    data = {"id": "ev_123", "case_id": "case_1", "content": "hello"}
    result = dynamo.put_evidence_metadata(data)

    assert result["evidence_id"] == "ev_123"
    assert result["created_at"] == fixed_dt.isoformat()
    mock_dynamodb.put_item.assert_called_once()
    item = mock_dynamodb.put_item.call_args.kwargs["Item"]
    assert item["evidence_id"]["S"] == "ev_123"
    assert item["created_at"]["S"] == fixed_dt.isoformat()


def test_put_evidence_metadata_requires_id():
    """Missing evidence id should raise ValueError."""
    with pytest.raises(ValueError):
        dynamo.put_evidence_metadata({"case_id": "case_1"})


def test_update_evidence_status_builds_expression(mock_aws_services):
    """Update helper should send expected expression values."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()

    result = dynamo.update_evidence_status(
        evidence_id="ev_123",
        status="processing",
        error_message="timeout",
        additional_fields={"attempt": 2, "labels": ["폭언"]},
    )

    assert result is True
    update_kwargs = mock_dynamodb.update_item.call_args.kwargs
    assert "#status" in update_kwargs["ExpressionAttributeNames"]
    assert update_kwargs["ExpressionAttributeValues"][":status"]["S"] == "processing"
    assert update_kwargs["ExpressionAttributeValues"][":error_message"]["S"] == "timeout"
    # Additional field should be serialized via helper
    assert update_kwargs["ExpressionAttributeValues"][":attempt"]["N"] == "2"
    labels = update_kwargs["ExpressionAttributeValues"][":labels"]["L"]
    assert labels[0]["S"] == "폭언"


def test_update_evidence_status_returns_false_on_client_error(monkeypatch, mock_aws_services):
    """Client errors should cause update helper to return False."""
    mock_dynamodb = mock_aws_services["dynamodb"]

    error = ClientError(
        {"Error": {"Code": "ConditionalCheckFailed", "Message": "oops"}},
        operation_name="UpdateItem",
    )
    mock_dynamodb.update_item.side_effect = error

    assert dynamo.update_evidence_status("ev_1", "failed") is False
    mock_dynamodb.update_item.side_effect = None  # cleanup


def test_delete_evidence_metadata_handles_client_error(mock_aws_services):
    """delete helper should return False when boto raises ClientError."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.delete_item.side_effect = ClientError(
        {"Error": {"Code": "Throttling", "Message": "slow"}},
        operation_name="DeleteItem",
    )

    assert dynamo.delete_evidence_metadata("ev_1") is False
    mock_dynamodb.delete_item.side_effect = None


def test_clear_case_evidence_deletes_each_item(monkeypatch, mock_aws_services):
    """clear_case_evidence should delete each queried evidence id."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()
    mock_dynamodb.query.return_value = {
        "Items": [
            {"evidence_id": {"S": "ev_a"}},
            {"evidence_id": {"S": "ev_b"}},
        ]
    }

    deleted = dynamo.clear_case_evidence("case_1")

    assert deleted == 2
    assert mock_dynamodb.delete_item.call_count == 2


def test_clear_case_evidence_raises_on_query_failure(mock_aws_services):
    """clear_case_evidence should bubble up query errors to the caller."""
    mock_dynamodb = mock_aws_services["dynamodb"]
    mock_dynamodb.reset_mock()
    mock_dynamodb.query.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}},
        operation_name="Query",
    )

    with pytest.raises(ClientError):
        dynamo.clear_case_evidence("case_1")

    mock_dynamodb.query.side_effect = None
