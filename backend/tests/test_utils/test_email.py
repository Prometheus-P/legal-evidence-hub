"""Tests for SES email utility."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from botocore.exceptions import ClientError

from app.core.config import settings
from app.utils import email as email_utils


def _patch_ses_client(monkeypatch, client):
    """Patch boto3 client factory used inside EmailService."""
    monkeypatch.setattr(
        email_utils,
        "boto3",
        SimpleNamespace(client=lambda *_, **__: client),
    )


def test_send_password_reset_email_success(monkeypatch):
    """Password reset helper should invoke SES with rendered template."""
    mock_client = MagicMock()
    mock_client.send_email.return_value = {"MessageId": "123"}
    _patch_ses_client(monkeypatch, mock_client)
    monkeypatch.setattr(settings, "SES_SENDER_EMAIL", "noreply@leh.test")
    monkeypatch.setattr(settings, "FRONTEND_URL", "https://leh.test")

    service = email_utils.EmailService()
    result = service.send_password_reset_email(
        to_email="user@example.com",
        reset_token="token-abc",
    )

    assert result is True
    mock_client.send_email.assert_called_once()
    payload = mock_client.send_email.call_args.kwargs
    assert payload["Source"] == "noreply@leh.test"
    assert "token-abc" in payload["Message"]["Body"]["Html"]["Data"]
    assert "token-abc" in payload["Message"]["Body"]["Text"]["Data"]


def test_send_email_returns_false_when_sender_missing(monkeypatch):
    """If SES sender is not configured the helper should short-circuit."""
    mock_client = MagicMock()
    _patch_ses_client(monkeypatch, mock_client)
    monkeypatch.setattr(settings, "SES_SENDER_EMAIL", "")
    service = email_utils.EmailService()

    assert service._send_email("to@test.com", "Subj", "<p>Body</p>", "Body") is False
    mock_client.send_email.assert_not_called()


def test_send_email_handles_client_error(monkeypatch):
    """ClientError should be caught and False returned."""
    error = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "denied"}},
        operation_name="SendEmail",
    )
    mock_client = MagicMock()
    mock_client.send_email.side_effect = error
    _patch_ses_client(monkeypatch, mock_client)
    monkeypatch.setattr(settings, "SES_SENDER_EMAIL", "noreply@leh.test")

    service = email_utils.EmailService()
    success = service._send_email("to@test.com", "Subj", "<p>Body</p>", "Body")

    assert success is False
    mock_client.send_email.assert_called_once()


def test_send_email_handles_unexpected_exception(monkeypatch):
    """Unexpected exceptions should also be handled gracefully."""
    mock_client = MagicMock()
    mock_client.send_email.side_effect = RuntimeError("boom")
    _patch_ses_client(monkeypatch, mock_client)
    monkeypatch.setattr(settings, "SES_SENDER_EMAIL", "noreply@leh.test")

    service = email_utils.EmailService()
    success = service._send_email("to@test.com", "Subj", "<p>Body</p>", "Body")

    assert success is False
