"""
Unit Tests for S3 Utilities
009-mvp-gap-closure - Issue #270

Tests for app/utils/s3.py
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.utils.s3 import (
    generate_presigned_upload_url,
    generate_presigned_download_url,
    upload_export_file,
    generate_export_download_url,
    delete_export_file,
    EXPORTS_BUCKET,
    EXPORTS_PREFIX
)


class TestGeneratePresignedUploadUrl:
    """Tests for generate_presigned_upload_url function"""

    @patch('app.utils.s3.boto3.client')
    def test_generates_presigned_url_successfully(self, mock_boto_client):
        """Test successful presigned PUT URL generation"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/test-bucket/test-key?signed=true"

        result = generate_presigned_upload_url(
            bucket="test-bucket",
            key="test-key",
            content_type="application/pdf"
        )

        assert "upload_url" in result
        assert "https://s3.amazonaws.com" in result["upload_url"]
        assert result["fields"] == {}
        mock_s3.generate_presigned_url.assert_called_once()

    @patch('app.utils.s3.boto3.client')
    def test_enforces_max_expiration_300_seconds(self, mock_boto_client):
        """Test that expiration is capped at 300 seconds"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://signed-url"

        generate_presigned_upload_url(
            bucket="test-bucket",
            key="test-key",
            content_type="application/pdf",
            expires_in=1000  # More than 300
        )

        # Verify expires_in was capped to 300
        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 300

    @patch('app.utils.s3.boto3.client')
    def test_uses_provided_expiration_within_limit(self, mock_boto_client):
        """Test that expiration is used when within limit"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://signed-url"

        generate_presigned_upload_url(
            bucket="test-bucket",
            key="test-key",
            content_type="image/jpeg",
            expires_in=180
        )

        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 180

    @patch('app.utils.s3.boto3.client')
    def test_raises_exception_on_error(self, mock_boto_client):
        """Test that exceptions are propagated"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.side_effect = Exception("S3 error")

        with pytest.raises(Exception) as exc_info:
            generate_presigned_upload_url(
                bucket="test-bucket",
                key="test-key",
                content_type="application/pdf"
            )
        assert "S3 error" in str(exc_info.value)


class TestGeneratePresignedDownloadUrl:
    """Tests for generate_presigned_download_url function"""

    @patch('app.utils.s3.boto3.client')
    def test_generates_presigned_url_successfully(self, mock_boto_client):
        """Test successful presigned GET URL generation"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://s3.amazonaws.com/test-bucket/test-key?signed=true"

        result = generate_presigned_download_url(
            bucket="test-bucket",
            key="test-key"
        )

        assert "https://s3.amazonaws.com" in result
        mock_s3.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'test-bucket', 'Key': 'test-key'},
            ExpiresIn=300
        )

    @patch('app.utils.s3.boto3.client')
    def test_enforces_max_expiration_300_seconds(self, mock_boto_client):
        """Test that expiration is capped at 300 seconds"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://signed-url"

        generate_presigned_download_url(
            bucket="test-bucket",
            key="test-key",
            expires_in=500
        )

        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 300

    @patch('app.utils.s3.boto3.client')
    def test_raises_exception_on_error(self, mock_boto_client):
        """Test that exceptions are propagated"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.side_effect = Exception("S3 download error")

        with pytest.raises(Exception) as exc_info:
            generate_presigned_download_url(
                bucket="test-bucket",
                key="test-key"
            )
        assert "S3 download error" in str(exc_info.value)


class TestUploadExportFile:
    """Tests for upload_export_file function"""

    @patch('app.utils.s3.boto3.client')
    def test_uploads_file_successfully(self, mock_boto_client):
        """Test successful file upload"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        result = upload_export_file(
            file_bytes=b"test file content",
            case_id="case_123",
            export_job_id="job_456",
            file_format="pdf",
            content_type="application/pdf"
        )

        assert "s3_key" in result
        assert result["s3_key"] == f"{EXPORTS_PREFIX}/case_123/job_456.pdf"
        assert result["file_size"] == len(b"test file content")
        assert "expires_at" in result
        mock_s3.put_object.assert_called_once()

    @patch('app.utils.s3.boto3.client')
    def test_caps_expiration_to_24_hours(self, mock_boto_client):
        """Test that expiration is capped at 24 hours"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        result = upload_export_file(
            file_bytes=b"content",
            case_id="case_123",
            export_job_id="job_456",
            file_format="docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            expires_hours=48  # More than 24
        )

        # Check that expires_at is within 24 hours
        expires_at = datetime.fromisoformat(result["expires_at"])
        now = datetime.now(timezone.utc)
        diff = expires_at - now
        assert diff.total_seconds() <= 24 * 3600 + 60  # Allow 1 minute tolerance

    @patch('app.utils.s3.boto3.client')
    def test_uploads_with_correct_metadata(self, mock_boto_client):
        """Test that correct metadata is set"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        upload_export_file(
            file_bytes=b"content",
            case_id="case_abc",
            export_job_id="job_xyz",
            file_format="pdf",
            content_type="application/pdf"
        )

        call_args = mock_s3.put_object.call_args
        metadata = call_args[1]['Metadata']
        assert metadata['case_id'] == 'case_abc'
        assert metadata['export_job_id'] == 'job_xyz'
        assert 'expires_at' in metadata

    @patch('app.utils.s3.boto3.client')
    def test_raises_exception_on_error(self, mock_boto_client):
        """Test that exceptions are propagated"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.put_object.side_effect = Exception("Upload failed")

        with pytest.raises(Exception) as exc_info:
            upload_export_file(
                file_bytes=b"content",
                case_id="case_123",
                export_job_id="job_456",
                file_format="pdf",
                content_type="application/pdf"
            )
        assert "Upload failed" in str(exc_info.value)


class TestGenerateExportDownloadUrl:
    """Tests for generate_export_download_url function"""

    @patch('app.utils.s3.boto3.client')
    def test_generates_download_url_successfully(self, mock_boto_client):
        """Test successful download URL generation"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://download-url"

        result = generate_export_download_url(s3_key="exports/case_123/job_456.pdf")

        assert result == "https://download-url"
        mock_s3.generate_presigned_url.assert_called_once()

    @patch('app.utils.s3.boto3.client')
    def test_adds_content_disposition_with_filename(self, mock_boto_client):
        """Test that Content-Disposition is set when filename provided"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://download-url"

        generate_export_download_url(
            s3_key="exports/case_123/job_456.pdf",
            filename="이혼소장_2025.pdf"
        )

        call_args = mock_s3.generate_presigned_url.call_args
        params = call_args[1]['Params']
        assert 'ResponseContentDisposition' in params
        assert '이혼소장_2025.pdf' in params['ResponseContentDisposition']

    @patch('app.utils.s3.boto3.client')
    def test_no_content_disposition_without_filename(self, mock_boto_client):
        """Test that Content-Disposition is not set when filename not provided"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://download-url"

        generate_export_download_url(s3_key="exports/case_123/job_456.pdf")

        call_args = mock_s3.generate_presigned_url.call_args
        params = call_args[1]['Params']
        assert 'ResponseContentDisposition' not in params

    @patch('app.utils.s3.boto3.client')
    def test_caps_expiration_to_3600_seconds(self, mock_boto_client):
        """Test that expiration is capped at 3600 seconds"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://download-url"

        generate_export_download_url(
            s3_key="exports/case_123/job_456.pdf",
            expires_in=7200  # More than 3600
        )

        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[1]['ExpiresIn'] == 3600

    @patch('app.utils.s3.boto3.client')
    def test_raises_exception_on_error(self, mock_boto_client):
        """Test that exceptions are propagated"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.side_effect = Exception("Download URL error")

        with pytest.raises(Exception) as exc_info:
            generate_export_download_url(s3_key="exports/case_123/job_456.pdf")
        assert "Download URL error" in str(exc_info.value)


class TestDeleteExportFile:
    """Tests for delete_export_file function"""

    @patch('app.utils.s3.boto3.client')
    def test_deletes_file_successfully(self, mock_boto_client):
        """Test successful file deletion"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        result = delete_export_file(s3_key="exports/case_123/job_456.pdf")

        assert result is True
        mock_s3.delete_object.assert_called_once_with(
            Bucket=EXPORTS_BUCKET,
            Key="exports/case_123/job_456.pdf"
        )

    @patch('app.utils.s3.boto3.client')
    def test_raises_exception_on_error(self, mock_boto_client):
        """Test that exceptions are propagated"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.delete_object.side_effect = Exception("Delete failed")

        with pytest.raises(Exception) as exc_info:
            delete_export_file(s3_key="exports/case_123/job_456.pdf")
        assert "Delete failed" in str(exc_info.value)


class TestS3Constants:
    """Tests for S3 module constants"""

    def test_exports_prefix_value(self):
        """Test EXPORTS_PREFIX is correct"""
        assert EXPORTS_PREFIX == "exports"

    def test_exports_bucket_is_set(self):
        """Test EXPORTS_BUCKET is set"""
        assert EXPORTS_BUCKET is not None
        assert isinstance(EXPORTS_BUCKET, str)
