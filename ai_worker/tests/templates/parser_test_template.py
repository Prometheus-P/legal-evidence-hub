"""
Parser Test Template
=====================

Template for testing file parsers in the AI Worker.
Copy and customize for your specific parser implementation.

QA Framework v4.0 - AI Worker Parser Testing

Parser Contract:
- Must inherit from BaseParser
- Must implement parse(file_path: str) -> List[ParsedMessage]
- Must handle file cleanup in /tmp (Lambda environment)

Usage:
    1. Copy to tests/src/test_your_parser.py
    2. Replace YourParser with your actual parser class
    3. Add parser-specific test cases
"""

import pytest
from typing import List
import tempfile
import os

# Uncomment and adjust imports for your parser:
# from src.parsers.your_parser import YourParser
# from src.parsers.base import BaseParser, ParsedMessage


# ============================================================================
# TDD STATUS TRACKING
# ============================================================================
# | Test Name                              | Status | Date       | Notes     |
# |----------------------------------------|--------|------------|-----------|
# | test_inherits_from_base_parser         | GREEN  | 2024-12-01 | Contract  |
# | test_parse_returns_list_of_messages    | GREEN  | 2024-12-01 | Contract  |
# | test_parse_extracts_content            | GREEN  | 2024-12-01 | Core      |
# | test_handles_empty_file                | GREEN  | 2024-12-01 | Edge      |
# | test_handles_encoding_issues           | RED    | -          | Pending   |
# ============================================================================


# ============================================================================
# Mock Parser for Template (replace with your actual parser)
# ============================================================================

class ParsedMessage:
    """Mock ParsedMessage for template."""
    def __init__(self, content: str, sender: str = "", timestamp: str = "", metadata: dict = None):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp
        self.metadata = metadata or {}


class BaseParser:
    """Mock BaseParser for template."""
    def parse(self, file_path: str) -> List[ParsedMessage]:
        raise NotImplementedError


class MockParser(BaseParser):
    """Sample parser for template testing."""

    def parse(self, file_path: str) -> List[ParsedMessage]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return []

        return [ParsedMessage(content=content, sender="unknown", timestamp="")]


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def parser():
    """
    Create parser instance.

    Replace MockParser with your actual parser class.
    """
    return MockParser()


@pytest.fixture
def sample_file():
    """
    Create a temporary sample file for testing.

    Yields:
        str: Path to temporary file
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Sample content for testing\nLine 2\nLine 3")
        f.flush()
        yield f.name

    # Cleanup
    if os.path.exists(f.name):
        os.remove(f.name)


@pytest.fixture
def empty_file():
    """Create an empty temporary file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        yield f.name

    if os.path.exists(f.name):
        os.remove(f.name)


@pytest.fixture
def unicode_file():
    """Create a file with unicode content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("한글 테스트 🎉\nEmoji: 🚀\n日本語: こんにちは")
        f.flush()
        yield f.name

    if os.path.exists(f.name):
        os.remove(f.name)


# ============================================================================
# Contract Tests (Required for all parsers)
# ============================================================================

class TestParserContract:
    """
    Tests that verify the parser adheres to the BaseParser contract.

    These tests are REQUIRED for all parser implementations.
    """

    @pytest.mark.unit
    @pytest.mark.parser
    def test_inherits_from_base_parser(self, parser):
        """
        Given: A parser instance
        When: Checking inheritance
        Then: Parser should inherit from BaseParser
        """
        assert isinstance(parser, BaseParser), (
            f"{type(parser).__name__} must inherit from BaseParser"
        )

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_method_exists(self, parser):
        """
        Given: A parser instance
        When: Checking for parse method
        Then: parse method should exist and be callable
        """
        assert hasattr(parser, 'parse'), "Parser must have 'parse' method"
        assert callable(parser.parse), "'parse' must be callable"

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_returns_list(self, parser, sample_file):
        """
        Given: A valid file
        When: parse() is called
        Then: Should return a list
        """
        result = parser.parse(sample_file)
        assert isinstance(result, list), "parse() must return a list"

    @pytest.mark.unit
    @pytest.mark.parser
    def test_parse_returns_parsed_messages(self, parser, sample_file):
        """
        Given: A valid file with content
        When: parse() is called
        Then: Should return list of ParsedMessage objects
        """
        result = parser.parse(sample_file)

        if len(result) > 0:
            message = result[0]
            assert hasattr(message, 'content'), "Message must have 'content'"
            assert hasattr(message, 'sender'), "Message must have 'sender'"
            assert hasattr(message, 'timestamp'), "Message must have 'timestamp'"


# ============================================================================
# Content Extraction Tests
# ============================================================================

class TestContentExtraction:
    """
    Tests for content extraction from files.

    Customize these tests based on your parser's specific behavior.
    """

    @pytest.mark.unit
    @pytest.mark.parser
    def test_extracts_content_from_file(self, parser, sample_file):
        """
        Given: A file with text content
        When: parse() is called
        Then: Content should be extracted
        """
        result = parser.parse(sample_file)

        assert len(result) > 0, "Should extract at least one message"
        assert result[0].content, "Message content should not be empty"

    @pytest.mark.unit
    @pytest.mark.parser
    def test_handles_unicode_content(self, parser, unicode_file):
        """
        Given: A file with unicode content
        When: parse() is called
        Then: Unicode should be preserved
        """
        result = parser.parse(unicode_file)

        assert len(result) > 0
        content = result[0].content
        assert "한글" in content, "Korean characters should be preserved"
        assert "🎉" in content or "🚀" in content, "Emojis should be preserved"


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """
    Tests for edge cases and error handling.
    """

    @pytest.mark.unit
    @pytest.mark.parser
    def test_handles_empty_file(self, parser, empty_file):
        """
        Given: An empty file
        When: parse() is called
        Then: Should return empty list (no crash)
        """
        result = parser.parse(empty_file)

        assert isinstance(result, list)
        assert len(result) == 0, "Empty file should return empty list"

    @pytest.mark.unit
    @pytest.mark.parser
    def test_raises_on_nonexistent_file(self, parser):
        """
        Given: A path to non-existent file
        When: parse() is called
        Then: Should raise FileNotFoundError
        """
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.txt")

    @pytest.mark.unit
    @pytest.mark.parser
    def test_handles_large_file(self, parser):
        """
        Given: A large file (simulating real-world data)
        When: parse() is called
        Then: Should handle without memory issues
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write 1MB of content
            for _ in range(10000):
                f.write("A" * 100 + "\n")
            f.flush()
            file_path = f.name

        try:
            result = parser.parse(file_path)
            assert isinstance(result, list)
        finally:
            os.remove(file_path)


# ============================================================================
# Parser-Specific Tests (Customize these)
# ============================================================================

class TestParserSpecificBehavior:
    """
    Parser-specific tests.

    Customize these based on your parser's unique features.
    Examples:
    - Text parser: KakaoTalk format detection
    - Image parser: OCR text extraction
    - Audio parser: Whisper transcription
    - PDF parser: Text extraction vs OCR fallback
    """

    @pytest.mark.unit
    @pytest.mark.parser
    @pytest.mark.skip(reason="Template - implement for your parser")
    def test_parser_specific_feature(self, parser):
        """
        Given: Specific input format
        When: parse() is called
        Then: Parser-specific behavior occurs
        """
        pass

    @pytest.mark.unit
    @pytest.mark.parser
    @pytest.mark.skip(reason="Template - implement for your parser")
    def test_extracts_metadata(self, parser):
        """
        Given: File with extractable metadata
        When: parse() is called
        Then: Metadata is populated in ParsedMessage
        """
        pass


# ============================================================================
# Integration Tests (with external services)
# ============================================================================

class TestParserIntegration:
    """
    Integration tests that may require external services.

    These tests are typically skipped in CI unless explicitly enabled.
    """

    @pytest.mark.integration
    @pytest.mark.parser
    @pytest.mark.skip(reason="Requires external service - run locally")
    def test_integration_with_openai(self):
        """
        Given: Real file and OpenAI connection
        When: parse() is called
        Then: AI-enhanced parsing works correctly
        """
        pass
