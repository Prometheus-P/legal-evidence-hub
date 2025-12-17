"""
Unit tests for verify_internal_api_key dependency

Tests the security logic for internal API key verification via API endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient


class TestVerifyInternalApiKeyIntegration:
    """Integration tests for verify_internal_api_key via API."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        return TestClient(app)

    def test_production_without_key_raises_500(self, client):
        """In production, missing INTERNAL_API_KEY raises 500 on callback endpoints."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "production"
        mock_settings.INTERNAL_API_KEY = ""

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(HTTPException) as exc_info:
                verify_internal_api_key(x_internal_api_key="some-key")

            assert exc_info.value.status_code == 500
            assert "must be configured" in exc_info.value.detail

    def test_prod_env_without_key_raises_500(self, client):
        """In 'prod' environment, missing INTERNAL_API_KEY raises 500."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "prod"
        mock_settings.INTERNAL_API_KEY = None

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(HTTPException) as exc_info:
                verify_internal_api_key(x_internal_api_key="some-key")

            assert exc_info.value.status_code == 500

    def test_development_without_key_allows_all(self, client):
        """In development, empty INTERNAL_API_KEY allows all traffic."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "development"
        mock_settings.INTERNAL_API_KEY = ""

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key=None)
            assert result is True

    def test_test_env_without_key_allows_all(self, client):
        """In test environment, empty INTERNAL_API_KEY allows all traffic."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "test"
        mock_settings.INTERNAL_API_KEY = None

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key=None)
            assert result is True

    def test_valid_api_key_returns_true(self, client):
        """Valid API key returns True."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "development"
        mock_settings.INTERNAL_API_KEY = "secret-api-key-12345"

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key="secret-api-key-12345")
            assert result is True

    def test_missing_api_key_header_raises_error(self, client):
        """Missing API key header raises AuthenticationError when key is configured."""
        from app.middleware import AuthenticationError

        mock_settings = MagicMock()
        mock_settings.APP_ENV = "development"
        mock_settings.INTERNAL_API_KEY = "secret-api-key-12345"

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError) as exc_info:
                verify_internal_api_key(x_internal_api_key=None)

            assert "required" in str(exc_info.value)

    def test_invalid_api_key_raises_error(self, client):
        """Invalid API key raises AuthenticationError."""
        from app.middleware import AuthenticationError

        mock_settings = MagicMock()
        mock_settings.APP_ENV = "development"
        mock_settings.INTERNAL_API_KEY = "correct-key"

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError) as exc_info:
                verify_internal_api_key(x_internal_api_key="wrong-key")

            assert "Invalid" in str(exc_info.value)

    def test_production_with_valid_key_works(self, client):
        """In production with valid key, verification passes."""
        mock_settings = MagicMock()
        mock_settings.APP_ENV = "production"
        mock_settings.INTERNAL_API_KEY = "prod-secret-key"

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key="prod-secret-key")
            assert result is True

    def test_production_with_invalid_key_raises_error(self, client):
        """In production with invalid key, raises AuthenticationError."""
        from app.middleware import AuthenticationError

        mock_settings = MagicMock()
        mock_settings.APP_ENV = "production"
        mock_settings.INTERNAL_API_KEY = "prod-secret-key"

        with patch("app.core.dependencies.settings", mock_settings):
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError):
                verify_internal_api_key(x_internal_api_key="wrong-key")
