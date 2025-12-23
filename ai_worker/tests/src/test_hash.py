"""
Unit tests for Hash Utilities

Tests SHA-256 hashing for idempotency and duplicate prevention.
"""

import pytest
import hashlib
import tempfile
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

from src.utils.hash import (
    calculate_file_hash,
    calculate_s3_object_hash,
    calculate_content_hash,
    get_s3_etag,
    is_duplicate_by_hash,
    HASH_BUFFER_SIZE,
)


class TestCalculateFileHash:
    """Test local file hashing"""

    def test_calculate_file_hash_small_file(self):
        """Given: Small text file
        When: Calculating hash
        Then: Returns correct SHA-256 hash"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            temp_path = f.name
        
        try:
            result = calculate_file_hash(temp_path)
            # SHA-256 of "Hello, World!"
            expected = hashlib.sha256(b"Hello, World!").hexdigest()
            assert result == expected
            assert len(result) == 64  # SHA-256 hex is 64 chars
        finally:
            os.unlink(temp_path)

    def test_calculate_file_hash_large_file(self):
        """Given: Large file (>8KB)
        When: Calculating hash
        Then: Correctly handles chunked reading"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Create 100KB file
            data = b"A" * 102400
            f.write(data)
            temp_path = f.name
        
        try:
            result = calculate_file_hash(temp_path)
            expected = hashlib.sha256(data).hexdigest()
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_calculate_file_hash_empty_file(self):
        """Given: Empty file
        When: Calculating hash
        Then: Returns hash of empty content"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            result = calculate_file_hash(temp_path)
            expected = hashlib.sha256(b"").hexdigest()
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_calculate_file_hash_binary_file(self):
        """Given: Binary file
        When: Calculating hash
        Then: Returns correct hash"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            binary_data = bytes([0, 1, 2, 3, 255, 254, 253])
            f.write(binary_data)
            temp_path = f.name
        
        try:
            result = calculate_file_hash(temp_path)
            expected = hashlib.sha256(binary_data).hexdigest()
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_calculate_file_hash_nonexistent_file(self):
        """Given: Nonexistent file path
        When: Calculating hash
        Then: Raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            calculate_file_hash("/nonexistent/path/to/file.txt")

    def test_calculate_file_hash_deterministic(self):
        """Given: Same file content
        When: Calculating hash multiple times
        Then: Returns same hash"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Deterministic test")
            temp_path = f.name
        
        try:
            hash1 = calculate_file_hash(temp_path)
            hash2 = calculate_file_hash(temp_path)
            hash3 = calculate_file_hash(temp_path)
            assert hash1 == hash2 == hash3
        finally:
            os.unlink(temp_path)

    def test_calculate_file_hash_different_content(self):
        """Given: Two files with different content
        When: Calculating hashes
        Then: Returns different hashes"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("Content A")
            path1 = f1.name
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("Content B")
            path2 = f2.name
        
        try:
            hash1 = calculate_file_hash(path1)
            hash2 = calculate_file_hash(path2)
            assert hash1 != hash2
        finally:
            os.unlink(path1)
            os.unlink(path2)


class TestCalculateS3ObjectHash:
    """Test S3 object hashing"""

    def test_calculate_s3_object_hash_success(self):
        """Given: Valid S3 object
        When: Calculating hash
        Then: Returns correct SHA-256 hash"""
        mock_s3 = MagicMock()
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = [b"Hello", b", ", b"World!"]
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        result = calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
        expected = hashlib.sha256(b"Hello, World!").hexdigest()
        assert result == expected

    def test_calculate_s3_object_hash_large_object(self):
        """Given: Large S3 object
        When: Calculating hash
        Then: Handles streaming correctly"""
        mock_s3 = MagicMock()
        mock_body = MagicMock()
        # Simulate large object with multiple chunks
        chunks = [b"A" * 8192 for _ in range(100)]
        mock_body.iter_chunks.return_value = chunks
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        result = calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
        expected = hashlib.sha256(b"A" * 8192 * 100).hexdigest()
        assert result == expected

    def test_calculate_s3_object_hash_empty_object(self):
        """Given: Empty S3 object
        When: Calculating hash
        Then: Returns hash of empty content"""
        mock_s3 = MagicMock()
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = []
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        result = calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_calculate_s3_object_hash_client_error(self, caplog):
        """Given: S3 client error
        When: Calculating hash
        Then: Returns None and logs error"""
        mock_s3 = MagicMock()
        error = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'GetObject'
        )
        mock_s3.get_object.side_effect = error
        
        result = calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
        assert result is None
        assert "Failed to hash S3 object" in caplog.text

    def test_calculate_s3_object_hash_unexpected_error(self, caplog):
        """Given: Unexpected error
        When: Calculating hash
        Then: Returns None and logs error"""
        mock_s3 = MagicMock()
        mock_s3.get_object.side_effect = RuntimeError("Unexpected error")
        
        result = calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
        assert result is None
        assert "Unexpected error" in caplog.text

    def test_calculate_s3_object_hash_creates_client_if_none(self):
        """Given: No S3 client provided
        When: Calculating hash
        Then: Creates new client"""
        with patch('src.utils.hash.boto3.client') as mock_boto:
            mock_s3 = MagicMock()
            mock_body = MagicMock()
            mock_body.iter_chunks.return_value = [b"test"]
            mock_s3.get_object.return_value = {'Body': mock_body}
            mock_boto.return_value = mock_s3
            
            result = calculate_s3_object_hash("test-bucket", "test-key")
            mock_boto.assert_called_once_with('s3')
            assert result is not None

    def test_calculate_s3_object_hash_uses_provided_client(self):
        """Given: S3 client provided
        When: Calculating hash
        Then: Uses provided client"""
        mock_s3 = MagicMock()
        mock_body = MagicMock()
        mock_body.iter_chunks.return_value = [b"test"]
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        with patch('src.utils.hash.boto3.client') as mock_boto:
            calculate_s3_object_hash("test-bucket", "test-key", mock_s3)
            mock_boto.assert_not_called()
            mock_s3.get_object.assert_called_once()


class TestCalculateContentHash:
    """Test string content hashing"""

    def test_calculate_content_hash_simple_string(self):
        """Given: Simple string
        When: Calculating hash
        Then: Returns correct SHA-256 hash"""
        content = "Hello, World!"
        result = calculate_content_hash(content)
        expected = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert result == expected
        assert len(result) == 64

    def test_calculate_content_hash_empty_string(self):
        """Given: Empty string
        When: Calculating hash
        Then: Returns hash of empty content"""
        result = calculate_content_hash("")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_calculate_content_hash_unicode(self):
        """Given: Unicode string
        When: Calculating hash
        Then: Returns correct hash"""
        content = "안녕하세요 世界 🌍"
        result = calculate_content_hash(content)
        expected = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert result == expected

    def test_calculate_content_hash_multiline(self):
        """Given: Multiline string
        When: Calculating hash
        Then: Returns correct hash"""
        content = "Line 1\nLine 2\nLine 3"
        result = calculate_content_hash(content)
        expected = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert result == expected

    def test_calculate_content_hash_large_content(self):
        """Given: Large string (>1MB)
        When: Calculating hash
        Then: Returns correct hash"""
        content = "A" * (1024 * 1024)  # 1MB
        result = calculate_content_hash(content)
        expected = hashlib.sha256(content.encode('utf-8')).hexdigest()
        assert result == expected

    def test_calculate_content_hash_custom_encoding(self):
        """Given: Custom encoding
        When: Calculating hash
        Then: Uses specified encoding"""
        content = "Test content"
        result_utf8 = calculate_content_hash(content, encoding='utf-8')
        result_ascii = calculate_content_hash(content, encoding='ascii')
        # For ASCII-compatible content, results should be same
        assert result_utf8 == result_ascii

    def test_calculate_content_hash_deterministic(self):
        """Given: Same content
        When: Calculating hash multiple times
        Then: Returns same hash"""
        content = "Deterministic test"
        hash1 = calculate_content_hash(content)
        hash2 = calculate_content_hash(content)
        hash3 = calculate_content_hash(content)
        assert hash1 == hash2 == hash3

    def test_calculate_content_hash_different_content(self):
        """Given: Different content
        When: Calculating hashes
        Then: Returns different hashes"""
        hash1 = calculate_content_hash("Content A")
        hash2 = calculate_content_hash("Content B")
        assert hash1 != hash2

    def test_calculate_content_hash_sensitive_to_whitespace(self):
        """Given: Content differing only in whitespace
        When: Calculating hashes
        Then: Returns different hashes"""
        hash1 = calculate_content_hash("Hello World")
        hash2 = calculate_content_hash("Hello  World")  # Double space
        assert hash1 != hash2


class TestGetS3Etag:
    """Test S3 ETag retrieval"""

    def test_get_s3_etag_success(self):
        """Given: Valid S3 object
        When: Getting ETag
        Then: Returns ETag and content length"""
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            'ETag': '"abc123def456"',
            'ContentLength': 1024
        }
        
        etag, size = get_s3_etag("test-bucket", "test-key", mock_s3)
        assert etag == "abc123def456"  # Quotes stripped
        assert size == 1024

    def test_get_s3_etag_no_quotes(self):
        """Given: ETag without quotes
        When: Getting ETag
        Then: Returns ETag as-is"""
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {
            'ETag': 'abc123',
            'ContentLength': 512
        }
        
        etag, size = get_s3_etag("test-bucket", "test-key", mock_s3)
        assert etag == "abc123"
        assert size == 512

    def test_get_s3_etag_client_error(self, caplog):
        """Given: S3 client error
        When: Getting ETag
        Then: Returns None, None and logs error"""
        mock_s3 = MagicMock()
        error = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'HeadObject'
        )
        mock_s3.head_object.side_effect = error
        
        etag, size = get_s3_etag("test-bucket", "test-key", mock_s3)
        assert etag is None
        assert size is None
        assert "Failed to get S3 object metadata" in caplog.text

    def test_get_s3_etag_creates_client_if_none(self):
        """Given: No S3 client provided
        When: Getting ETag
        Then: Creates new client"""
        with patch('src.utils.hash.boto3.client') as mock_boto:
            mock_s3 = MagicMock()
            mock_s3.head_object.return_value = {
                'ETag': '"test"',
                'ContentLength': 100
            }
            mock_boto.return_value = mock_s3
            
            etag, size = get_s3_etag("test-bucket", "test-key")
            mock_boto.assert_called_once_with('s3')
            assert etag == "test"
            assert size == 100

    def test_get_s3_etag_missing_fields(self):
        """Given: Response missing ETag or ContentLength
        When: Getting ETag
        Then: Returns empty string and 0"""
        mock_s3 = MagicMock()
        mock_s3.head_object.return_value = {}
        
        etag, size = get_s3_etag("test-bucket", "test-key", mock_s3)
        assert etag == ""
        assert size == 0


class TestIsDuplicateByHash:
    """Test duplicate detection"""

    def test_is_duplicate_hash_exists(self):
        """Given: Hash in existing set
        When: Checking for duplicate
        Then: Returns True"""
        existing = {"hash1", "hash2", "hash3"}
        assert is_duplicate_by_hash("hash2", existing) is True

    def test_is_duplicate_hash_not_exists(self):
        """Given: Hash not in existing set
        When: Checking for duplicate
        Then: Returns False"""
        existing = {"hash1", "hash2", "hash3"}
        assert is_duplicate_by_hash("hash4", existing) is False

    def test_is_duplicate_empty_set(self):
        """Given: Empty set
        When: Checking for duplicate
        Then: Returns False"""
        existing = set()
        assert is_duplicate_by_hash("hash1", existing) is False

    def test_is_duplicate_case_sensitive(self):
        """Given: Hash with different case
        When: Checking for duplicate
        Then: Case matters"""
        existing = {"HASH1", "HASH2"}
        assert is_duplicate_by_hash("hash1", existing) is False
        assert is_duplicate_by_hash("HASH1", existing) is True


class TestHashBufferSize:
    """Test hash buffer size constant"""

    def test_buffer_size_constant(self):
        """Given: HASH_BUFFER_SIZE constant
        When: Checking value
        Then: Is 8KB (8192 bytes)"""
        assert HASH_BUFFER_SIZE == 8192


class TestEdgeCases:
    """Test edge cases and integration scenarios"""

    def test_file_and_content_hash_consistency(self):
        """Given: Same content in file and string
        When: Hashing both
        Then: Returns same hash"""
        content = "Consistency test content"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            file_hash = calculate_file_hash(temp_path)
            content_hash = calculate_content_hash(content)
            assert file_hash == content_hash
        finally:
            os.unlink(temp_path)

    def test_hash_unicode_file_content(self):
        """Given: File with Unicode content
        When: Hashing file
        Then: Returns correct hash"""
        content = "한글 테스트 🎉"
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            file_hash = calculate_file_hash(temp_path)
            content_hash = calculate_content_hash(content)
            assert file_hash == content_hash
        finally:
            os.unlink(temp_path)

    def test_duplicate_detection_workflow(self):
        """Given: Multiple files with some duplicates
        When: Hashing and checking duplicates
        Then: Correctly identifies duplicates"""
        # Create files
        files = []
        for i, content in enumerate(["A", "B", "A", "C", "B"]):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(content)
                files.append(f.name)
        
        try:
            # Hash all files
            hashes = [calculate_file_hash(f) for f in files]
            
            # Detect duplicates
            seen = set()
            duplicates = []
            for i, h in enumerate(hashes):
                if is_duplicate_by_hash(h, seen):
                    duplicates.append(i)
                else:
                    seen.add(h)
            
            # Indices 2 and 4 should be duplicates (content "A" and "B")
            assert 2 in duplicates  # "A" duplicate
            assert 4 in duplicates  # "B" duplicate
            assert len(duplicates) == 2
        finally:
            for f in files:
                os.unlink(f)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])