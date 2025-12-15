"""
Unit tests for verify_internal_api_key dependency

Tests the security logic for internal API key verification via API endpoints.
"""

import pytest
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
        # Create a mock endpoint that uses verify_internal_api_key
        # We test via the existing jobs callback endpoint if it exists
        # For now, test the logic directly

        from fastapi import HTTPException
        from app.core.config import settings

        # Save original values
        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            # Simulate production without key
            settings.APP_ENV = "production"
            settings.INTERNAL_API_KEY = ""

            # Import and call the function directly
            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(HTTPException) as exc_info:
                verify_internal_api_key(x_internal_api_key="some-key")

            assert exc_info.value.status_code == 500
            assert "must be configured" in exc_info.value.detail
        finally:
            # Restore original values
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_prod_env_without_key_raises_500(self, client):
        """In 'prod' environment, missing INTERNAL_API_KEY raises 500."""
        from fastapi import HTTPException
        from app.core.config import settings

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "prod"
            settings.INTERNAL_API_KEY = None

            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(HTTPException) as exc_info:
                verify_internal_api_key(x_internal_api_key="some-key")

            assert exc_info.value.status_code == 500
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_development_without_key_allows_all(self, client):
        """In development, empty INTERNAL_API_KEY allows all traffic."""
        from app.core.config import settings

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "development"
            settings.INTERNAL_API_KEY = ""

            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key=None)
            assert result is True
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_test_env_without_key_allows_all(self, client):
        """In test environment, empty INTERNAL_API_KEY allows all traffic."""
        from app.core.config import settings

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "test"
            settings.INTERNAL_API_KEY = None

            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key=None)
            assert result is True
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_valid_api_key_returns_true(self, client):
        """Valid API key returns True."""
        from app.core.config import settings

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "development"
            settings.INTERNAL_API_KEY = "secret-api-key-12345"

            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key="secret-api-key-12345")
            assert result is True
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_missing_api_key_header_raises_error(self, client):
        """Missing API key header raises AuthenticationError when key is configured."""
        from app.core.config import settings
        from app.middleware import AuthenticationError

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "development"
            settings.INTERNAL_API_KEY = "secret-api-key-12345"

            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError) as exc_info:
                verify_internal_api_key(x_internal_api_key=None)

            assert "required" in str(exc_info.value)
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_invalid_api_key_raises_error(self, client):
        """Invalid API key raises AuthenticationError."""
        from app.core.config import settings
        from app.middleware import AuthenticationError

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "development"
            settings.INTERNAL_API_KEY = "correct-key"

            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError) as exc_info:
                verify_internal_api_key(x_internal_api_key="wrong-key")

            assert "Invalid" in str(exc_info.value)
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_production_with_valid_key_works(self, client):
        """In production with valid key, verification passes."""
        from app.core.config import settings

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "production"
            settings.INTERNAL_API_KEY = "prod-secret-key"

            from app.core.dependencies import verify_internal_api_key

            result = verify_internal_api_key(x_internal_api_key="prod-secret-key")
            assert result is True
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key

    def test_production_with_invalid_key_raises_error(self, client):
        """In production with invalid key, raises AuthenticationError."""
        from app.core.config import settings
        from app.middleware import AuthenticationError

        orig_env = settings.APP_ENV
        orig_key = settings.INTERNAL_API_KEY

        try:
            settings.APP_ENV = "production"
            settings.INTERNAL_API_KEY = "prod-secret-key"

            from app.core.dependencies import verify_internal_api_key

            with pytest.raises(AuthenticationError):
                verify_internal_api_key(x_internal_api_key="wrong-key")
        finally:
            settings.APP_ENV = orig_env
            settings.INTERNAL_API_KEY = orig_key
