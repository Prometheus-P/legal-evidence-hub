"""Unit tests for OpenAI utility module without hitting the real API."""

import builtins
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.utils import openai_client


@pytest.fixture(autouse=True)
def reset_openai_singleton():
    """Ensure cached OpenAI client is reset for every test."""
    openai_client._openai_client = None
    yield
    openai_client._openai_client = None


def _mock_openai_client(monkeypatch):
    """Patch OpenAI constructor and return the mock instance."""
    mock_client = MagicMock()
    monkeypatch.setattr(openai_client, "OpenAI", MagicMock(return_value=mock_client))
    return mock_client


def test_generate_chat_completion_uses_mock_client(monkeypatch):
    """Chat completion should unwrap the first choice content."""
    mock_client = _mock_openai_client(monkeypatch)
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="hello"))],
        usage=SimpleNamespace(total_tokens=42),
    )

    response = openai_client.generate_chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        model="gpt-test",
        max_tokens=5,
    )

    assert response == "hello"
    mock_client.chat.completions.create.assert_called_once()


def test_generate_embedding_returns_vector(monkeypatch):
    """generate_embedding should unwrap embedding payload."""
    mock_client = _mock_openai_client(monkeypatch)
    mock_client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(embedding=[0.1, 0.2, 0.3])]
    )

    embedding = openai_client.generate_embedding("hello", model="text-embed-test")

    assert embedding == [0.1, 0.2, 0.3]
    mock_client.embeddings.create.assert_called_once()


def test_get_openai_client_requires_api_key(monkeypatch):
    """Missing API key should raise ValueError before instantiating client."""
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")

    with pytest.raises(ValueError):
        openai_client._get_openai_client()


def test_count_tokens_uses_tiktoken_when_available(monkeypatch):
    """count_tokens should rely on tiktoken encoding when module is present."""

    class DummyEncoding:
        def encode(self, text: str):
            return list(range(len(text)))

    class DummyTikToken:
        def encoding_for_model(self, _model):
            return DummyEncoding()

        def get_encoding(self, _name):
            return DummyEncoding()

    dummy_module = DummyTikToken()
    monkeypatch.setitem(sys.modules, "tiktoken", dummy_module)

    tokens = openai_client.count_tokens("hello", model="gpt-test")

    assert tokens == len("hello")


def test_count_tokens_falls_back_without_tiktoken(monkeypatch):
    """When tiktoken import fails, fallback estimator should be used."""
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "tiktoken":
            raise ImportError("forced")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    tokens = openai_client.count_tokens("가나다라마바사")

    # Fallback estimates half the length for Korean text
    assert tokens == len("가나다라마바사") // 2
