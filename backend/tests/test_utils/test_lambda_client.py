"""Tests for Lambda invocation utility."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from app.core.config import settings
from app.utils import lambda_client


def _patch_lambda_client(monkeypatch, response=None, side_effect=None):
    """Patch boto3 client to return a controllable Lambda mock."""
    mock_lambda = MagicMock()
    if side_effect is not None:
        mock_lambda.invoke.side_effect = side_effect
    elif response is not None:
        mock_lambda.invoke.return_value = response

    def _mock_boto3_client(service_name, **kwargs):
        assert service_name == "lambda"
        return mock_lambda

    monkeypatch.setattr(
        lambda_client,
        "boto3",
        SimpleNamespace(client=_mock_boto3_client),
    )
    return mock_lambda


def test_invoke_ai_worker_skips_when_disabled(monkeypatch):
    """Return skip result when Lambda invocation feature flag is off."""
    monkeypatch.setattr(settings, "LAMBDA_AI_WORKER_ENABLED", False)

    result = lambda_client.invoke_ai_worker(
        bucket="test-bucket",
        s3_key="cases/case_1/raw/file.pdf",
        evidence_id="ev_123",
        case_id="case_1",
    )

    assert result["status"] == "skipped"
    assert "reason" in result


def test_invoke_ai_worker_success(monkeypatch):
    """Successful invocation should return request metadata."""
    monkeypatch.setattr(settings, "LAMBDA_AI_WORKER_ENABLED", True)
    response = {
        "StatusCode": 202,
        "ResponseMetadata": {"RequestId": "req-123"},
    }
    mock_lambda = _patch_lambda_client(monkeypatch, response=response)

    result = lambda_client.invoke_ai_worker(
        bucket="test-bucket",
        s3_key="cases/case_1/raw/file.pdf",
        evidence_id="ev_123",
        case_id="case_1",
    )

    assert result == {
        "status": "invoked",
        "request_id": "req-123",
        "function_name": settings.LAMBDA_AI_WORKER_FUNCTION,
    }
    mock_lambda.invoke.assert_called_once()
    _args, kwargs = mock_lambda.invoke.call_args
    assert kwargs["InvocationType"] == "Event"
    payload = kwargs["Payload"]
    assert "Records" in payload


def test_invoke_ai_worker_handles_unexpected_status(monkeypatch):
    """Return unexpected status info when Lambda responds with non-202 code."""
    monkeypatch.setattr(settings, "LAMBDA_AI_WORKER_ENABLED", True)
    response = {"StatusCode": 500, "ResponseMetadata": {"RequestId": "bad"}}
    _patch_lambda_client(monkeypatch, response=response)

    result = lambda_client.invoke_ai_worker(
        bucket="test-bucket",
        s3_key="cases/case_1/raw/file.pdf",
        evidence_id="ev_123",
        case_id="case_1",
    )

    assert result["status"] == "unexpected"
    assert result["status_code"] == 500
    assert result["request_id"] == "bad"


def test_invoke_ai_worker_handles_client_error(monkeypatch):
    """Return error status when boto3 raises ClientError."""
    monkeypatch.setattr(settings, "LAMBDA_AI_WORKER_ENABLED", True)
    error = ClientError(
        error_response={
            "Error": {"Code": "AccessDenied", "Message": "denied"},
        },
        operation_name="Invoke",
    )
    _patch_lambda_client(monkeypatch, side_effect=error)

    result = lambda_client.invoke_ai_worker(
        bucket="test-bucket",
        s3_key="cases/case_1/raw/file.pdf",
        evidence_id="ev_123",
        case_id="case_1",
    )

    assert result["status"] == "error"
    assert result["error_code"] == "AccessDenied"
    assert "denied" in result["error_message"]


def test_invoke_ai_worker_handles_unexpected_exception(monkeypatch):
    """Return generic error when unexpected exception occurs."""
    monkeypatch.setattr(settings, "LAMBDA_AI_WORKER_ENABLED", True)
    _patch_lambda_client(monkeypatch, side_effect=RuntimeError("boom"))

    result = lambda_client.invoke_ai_worker(
        bucket="test-bucket",
        s3_key="cases/case_1/raw/file.pdf",
        evidence_id="ev_123",
        case_id="case_1",
    )

    assert result["status"] == "error"
    assert result["error_message"] == "boom"
