"""Unit tests for S3 utility helpers."""

from app.utils import s3


def test_generate_presigned_upload_url_uses_mock_client(mock_aws_services):
    """Presigned upload URLs should be generated through boto3 with provided params."""
    mock_client = mock_aws_services["s3"]
    mock_client.reset_mock()
    mock_client.generate_presigned_url.return_value = "https://example.com/upload"

    result = s3.generate_presigned_upload_url(
        bucket="test-bucket",
        key="cases/case_1/raw/file.pdf",
        content_type="application/pdf",
        expires_in=180,
    )

    assert result == {
        "upload_url": "https://example.com/upload",
        "fields": {},
    }
    mock_client.generate_presigned_url.assert_called_once()
    args, kwargs = mock_client.generate_presigned_url.call_args
    assert args[0] == "put_object"
    assert kwargs["Params"]["Bucket"] == "test-bucket"
    assert kwargs["Params"]["Key"] == "cases/case_1/raw/file.pdf"
    assert kwargs["Params"]["ContentType"] == "application/pdf"
    assert kwargs["ExpiresIn"] == 180


def test_generate_presigned_upload_url_caps_expiration(mock_aws_services):
    """Expiration should be capped at 300 seconds per security policy."""
    mock_client = mock_aws_services["s3"]
    mock_client.reset_mock()

    s3.generate_presigned_upload_url(
        bucket="test-bucket",
        key="cases/case_1/raw/file.pdf",
        content_type="application/pdf",
        expires_in=999,
    )

    _, kwargs = mock_client.generate_presigned_url.call_args
    assert kwargs["ExpiresIn"] == 300


def test_generate_presigned_download_url_enforces_expiration(mock_aws_services):
    """Download URLs should also enforce the max expiration window."""
    mock_client = mock_aws_services["s3"]
    mock_client.reset_mock()
    mock_client.generate_presigned_url.return_value = "https://example.com/download"

    url = s3.generate_presigned_download_url(
        bucket="test-bucket",
        key="cases/case_1/raw/file.pdf",
        expires_in=600,
    )

    assert url == "https://example.com/download"
    _, kwargs = mock_client.generate_presigned_url.call_args
    assert kwargs["ExpiresIn"] == 300
