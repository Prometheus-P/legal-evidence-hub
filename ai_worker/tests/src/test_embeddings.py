"""
Unit tests for Embedding Utilities

Tests OpenAI embedding generation with fallback mechanisms.
"""

import pytest
from unittest.mock import patch, MagicMock
from openai import OpenAI

from src.utils.embeddings import (
    _get_client,
    generate_fallback_embedding,
    get_embedding,
    get_embedding_with_fallback,
    get_embeddings_batch,
    get_embedding_dimension,
)


class TestGetClient:
    """Test OpenAI client singleton"""

    def test_get_client_with_api_key(self, monkeypatch):
        """Given: OPENAI_API_KEY set
        When: Getting client
        Then: Returns OpenAI client"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        # Reset singleton
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        client = _get_client()
        assert client is not None
        assert isinstance(client, OpenAI)

    def test_get_client_without_api_key(self, monkeypatch):
        """Given: No OPENAI_API_KEY
        When: Getting client
        Then: Raises ValueError"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        # Reset singleton
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            _get_client()

    def test_get_client_singleton_behavior(self, monkeypatch):
        """Given: Multiple calls to _get_client
        When: Getting client repeatedly
        Then: Returns same instance"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        client1 = _get_client()
        client2 = _get_client()
        assert client1 is client2


class TestGenerateFallbackEmbedding:
    """Test fallback embedding generation"""

    def test_fallback_empty_text(self):
        """Given: Empty text
        When: Generating fallback
        Then: Returns zero vector"""
        result = generate_fallback_embedding("", 1536)
        assert len(result) == 1536
        assert all(v == 0.0 for v in result)

    def test_fallback_whitespace_only(self):
        """Given: Whitespace-only text
        When: Generating fallback
        Then: Returns zero vector"""
        result = generate_fallback_embedding("   ", 1536)
        assert len(result) == 1536
        assert all(v == 0.0 for v in result)

    def test_fallback_deterministic(self):
        """Given: Same text twice
        When: Generating fallback
        Then: Returns identical embeddings"""
        text = "Test text for deterministic embedding"
        embedding1 = generate_fallback_embedding(text, 1536)
        embedding2 = generate_fallback_embedding(text, 1536)
        assert embedding1 == embedding2

    def test_fallback_different_texts_different_embeddings(self):
        """Given: Different texts
        When: Generating fallback
        Then: Returns different embeddings"""
        embedding1 = generate_fallback_embedding("Text A", 1536)
        embedding2 = generate_fallback_embedding("Text B", 1536)
        assert embedding1 != embedding2

    def test_fallback_correct_dimensions(self):
        """Given: Custom dimension size
        When: Generating fallback
        Then: Returns vector of correct size"""
        for dims in [128, 256, 512, 1536, 3072]:
            result = generate_fallback_embedding("test", dims)
            assert len(result) == dims

    def test_fallback_values_in_range(self):
        """Given: Any text
        When: Generating fallback
        Then: All values in [-1, 1]"""
        result = generate_fallback_embedding("Test text", 1536)
        assert all(-1.0 <= v <= 1.0 for v in result)

    def test_fallback_korean_text(self):
        """Given: Korean text
        When: Generating fallback
        Then: Returns valid embedding"""
        result = generate_fallback_embedding("한글 텍스트 테스트", 1536)
        assert len(result) == 1536
        assert all(-1.0 <= v <= 1.0 for v in result)

    def test_fallback_long_text(self):
        """Given: Very long text
        When: Generating fallback
        Then: Returns valid embedding"""
        long_text = "A" * 10000
        result = generate_fallback_embedding(long_text, 1536)
        assert len(result) == 1536


class TestGetEmbedding:
    """Test single text embedding generation"""

    def test_get_embedding_success(self, monkeypatch):
        """Given: Valid text and OpenAI API
        When: Getting embedding
        Then: Returns embedding vector"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            result = get_embedding("Test text")
            assert len(result) == 1536
            assert result[0] == 0.1

    def test_get_embedding_empty_text_raises(self):
        """Given: Empty text
        When: Getting embedding
        Then: Raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            get_embedding("")

    def test_get_embedding_whitespace_raises(self):
        """Given: Whitespace-only text
        When: Getting embedding
        Then: Raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            get_embedding("   ")

    def test_get_embedding_truncates_long_text(self, monkeypatch, caplog):
        """Given: Very long text (>30000 chars)
        When: Getting embedding
        Then: Truncates and logs warning"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        long_text = "A" * 40000
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            get_embedding(long_text)
            assert "truncated" in caplog.text.lower()

    def test_get_embedding_api_failure_raises(self, monkeypatch):
        """Given: OpenAI API failure
        When: Getting embedding
        Then: Raises exception"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            with pytest.raises(Exception, match="API Error"):
                get_embedding("Test text")

    def test_get_embedding_custom_model(self, monkeypatch):
        """Given: Custom embedding model
        When: Getting embedding
        Then: Uses specified model"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 3072)]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            get_embedding("Test", model="text-embedding-3-large")
            mock_client.embeddings.create.assert_called_once()
            call_kwargs = mock_client.embeddings.create.call_args[1]
            assert call_kwargs['model'] == "text-embedding-3-large"


class TestGetEmbeddingWithFallback:
    """Test embedding with automatic fallback"""

    def test_get_embedding_with_fallback_success(self, monkeypatch):
        """Given: Valid text and working API
        When: Getting embedding with fallback
        Then: Returns real embedding and True flag"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            embedding, is_real = get_embedding_with_fallback("Test text")
            assert len(embedding) == 1536
            assert is_real is True
            assert embedding[0] == 0.1

    def test_get_embedding_with_fallback_api_failure(self, monkeypatch, caplog):
        """Given: API failure
        When: Getting embedding with fallback
        Then: Returns fallback embedding and False flag"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            embedding, is_real = get_embedding_with_fallback("Test text")
            assert len(embedding) == 1536
            assert is_real is False
            assert "fallback" in caplog.text.lower()

    def test_get_embedding_with_fallback_empty_text(self, caplog):
        """Given: Empty text
        When: Getting embedding with fallback
        Then: Returns zero vector and False flag"""
        embedding, is_real = get_embedding_with_fallback("")
        assert len(embedding) == 1536
        assert is_real is False
        assert all(v == 0.0 for v in embedding)
        assert "empty" in caplog.text.lower()

    def test_get_embedding_with_fallback_truncates_long_text(self, monkeypatch, caplog):
        """Given: Very long text
        When: Getting embedding with fallback
        Then: Truncates text and logs warning"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        long_text = "A" * 40000
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            embedding, is_real = get_embedding_with_fallback(long_text)
            assert "truncated" in caplog.text.lower()

    def test_get_embedding_with_fallback_never_raises(self, monkeypatch):
        """Given: Any error condition
        When: Getting embedding with fallback
        Then: Never raises exception"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = RuntimeError("Critical failure")
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            # Should not raise
            embedding, is_real = get_embedding_with_fallback("Test")
            assert len(embedding) == 1536
            assert is_real is False


class TestGetEmbeddingsBatch:
    """Test batch embedding generation"""

    def test_get_embeddings_batch_success(self, monkeypatch):
        """Given: List of texts
        When: Getting batch embeddings
        Then: Returns list of embeddings"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.1] * 1536),
            MagicMock(index=1, embedding=[0.2] * 1536),
            MagicMock(index=2, embedding=[0.3] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        texts = ["Text 1", "Text 2", "Text 3"]
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            results = get_embeddings_batch(texts)
            assert len(results) == 3
            assert results[0][0] == 0.1
            assert results[1][0] == 0.2
            assert results[2][0] == 0.3

    def test_get_embeddings_batch_empty_list(self):
        """Given: Empty list
        When: Getting batch embeddings
        Then: Returns empty list"""
        result = get_embeddings_batch([])
        assert result == []

    def test_get_embeddings_batch_filters_empty_texts(self, monkeypatch):
        """Given: List with empty texts
        When: Getting batch embeddings
        Then: Filters out empty texts"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(index=0, embedding=[0.1] * 1536),
            MagicMock(index=1, embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        texts = ["Text 1", "", "Text 2", "   "]
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            results = get_embeddings_batch(texts)
            assert len(results) == 2

    def test_get_embeddings_batch_truncates_long_texts(self, monkeypatch):
        """Given: Texts longer than 30000 chars
        When: Getting batch embeddings
        Then: Truncates each text"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(index=0, embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        long_text = "A" * 40000
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            get_embeddings_batch([long_text])
            # Should call API with truncated text
            call_args = mock_client.embeddings.create.call_args
            assert len(call_args[1]['input'][0]) <= 30000

    def test_get_embeddings_batch_handles_large_batches(self, monkeypatch):
        """Given: More than 2048 texts
        When: Getting batch embeddings
        Then: Splits into multiple API calls"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        
        # First batch response
        mock_response1 = MagicMock()
        mock_response1.data = [MagicMock(index=i, embedding=[0.1] * 1536) for i in range(2048)]
        
        # Second batch response
        mock_response2 = MagicMock()
        mock_response2.data = [MagicMock(index=i, embedding=[0.2] * 1536) for i in range(100)]
        
        mock_client.embeddings.create.side_effect = [mock_response1, mock_response2]
        
        texts = [f"Text {i}" for i in range(2148)]  # 2048 + 100
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            results = get_embeddings_batch(texts)
            assert len(results) == 2148
            assert mock_client.embeddings.create.call_count == 2

    def test_get_embeddings_batch_preserves_order(self, monkeypatch):
        """Given: List of texts
        When: Getting batch embeddings
        Then: Returns embeddings in same order"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Return in scrambled order to test sorting
        mock_response.data = [
            MagicMock(index=2, embedding=[0.3] * 1536),
            MagicMock(index=0, embedding=[0.1] * 1536),
            MagicMock(index=1, embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        texts = ["Text 1", "Text 2", "Text 3"]
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            results = get_embeddings_batch(texts)
            # Should be sorted by index
            assert results[0][0] == 0.1
            assert results[1][0] == 0.2
            assert results[2][0] == 0.3

    def test_get_embeddings_batch_api_failure_raises(self, monkeypatch):
        """Given: API failure
        When: Getting batch embeddings
        Then: Raises exception"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            with pytest.raises(Exception, match="API Error"):
                get_embeddings_batch(["Text 1", "Text 2"])


class TestGetEmbeddingDimension:
    """Test embedding dimension lookup"""

    def test_dimension_ada_002(self):
        """Given: text-embedding-ada-002
        When: Getting dimension
        Then: Returns 1536"""
        assert get_embedding_dimension("text-embedding-ada-002") == 1536

    def test_dimension_3_small(self):
        """Given: text-embedding-3-small
        When: Getting dimension
        Then: Returns 1536"""
        assert get_embedding_dimension("text-embedding-3-small") == 1536

    def test_dimension_3_large(self):
        """Given: text-embedding-3-large
        When: Getting dimension
        Then: Returns 3072"""
        assert get_embedding_dimension("text-embedding-3-large") == 3072

    def test_dimension_unknown_model(self):
        """Given: Unknown model
        When: Getting dimension
        Then: Returns default 1536"""
        assert get_embedding_dimension("unknown-model") == 1536

    def test_dimension_default_model(self):
        """Given: No model specified
        When: Getting dimension
        Then: Returns 1536"""
        assert get_embedding_dimension() == 1536


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_unicode_text_embedding(self, monkeypatch):
        """Given: Text with various Unicode characters
        When: Getting embedding
        Then: Handles correctly"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        unicode_text = "Hello 世界 🌍 مرحبا"
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            result = get_embedding(unicode_text)
            assert len(result) == 1536

    def test_fallback_consistency_across_calls(self):
        """Given: Same text multiple times
        When: Generating fallback
        Then: Always returns identical embedding"""
        text = "Consistency test"
        embeddings = [generate_fallback_embedding(text, 1536) for _ in range(10)]
        # All should be identical
        for emb in embeddings[1:]:
            assert emb == embeddings[0]

    def test_single_character_text(self, monkeypatch):
        """Given: Single character text
        When: Getting embedding
        Then: Processes successfully"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        import src.utils.embeddings as emb_module
        emb_module._client = None
        
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('src.utils.embeddings._get_client', return_value=mock_client):
            result = get_embedding("A")
            assert len(result) == 1536


if __name__ == "__main__":
    pytest.main([__file__, "-v"])