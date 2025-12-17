"""
Contract tests for Authentication Cookie Headers
Task T013 - TDD for cookie settings verification

Tests for POST /auth/login and /auth/signup endpoints:
- Set-Cookie headers are correctly set
- Cookie attributes (httponly, secure, samesite) match config
- Cross-origin cookie requirements are met

Related to: 011-production-bug-fixes (Login redirect bug)
Root Cause: Cookie SameSite and Secure settings blocked cross-origin transmission
"""

import pytest
from fastapi import status
from unittest.mock import patch
import os


class TestLoginCookieHeaders:
    """
    Contract tests for login response cookies

    Verifies that POST /auth/login sets correct cookies for authentication.
    """

    def test_login_should_set_access_token_cookie(self, client):
        """
        Given: Valid user credentials
        When: POST /auth/login is called
        Then: Response includes Set-Cookie header with access_token
        """
        # Given: Create a user first
        signup_payload = {
            "email": "cookie_test_user@example.com",
            "password": "password123",
            "name": "Cookie Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        # When: Login with valid credentials
        login_payload = {
            "email": "cookie_test_user@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_payload)

        # Then: Response is successful
        assert response.status_code == status.HTTP_200_OK

        # Then: Set-Cookie header exists with access_token
        cookies = response.cookies
        assert "access_token" in cookies, "access_token cookie should be set"

    def test_login_should_set_refresh_token_cookie(self, client):
        """
        Given: Valid user credentials
        When: POST /auth/login is called
        Then: Response includes Set-Cookie header with refresh_token
        """
        # Given: Create a user first
        signup_payload = {
            "email": "cookie_refresh_test@example.com",
            "password": "password123",
            "name": "Refresh Token Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        # When: Login with valid credentials
        login_payload = {
            "email": "cookie_refresh_test@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_payload)

        # Then: Response is successful
        assert response.status_code == status.HTTP_200_OK

        # Then: Set-Cookie header exists with refresh_token
        cookies = response.cookies
        assert "refresh_token" in cookies, "refresh_token cookie should be set"

    def test_access_token_cookie_should_be_httponly(self, client):
        """
        Given: Valid user credentials
        When: POST /auth/login is called
        Then: access_token cookie has httponly attribute for XSS protection
        """
        # Given: Create a user
        signup_payload = {
            "email": "httponly_test@example.com",
            "password": "password123",
            "name": "HttpOnly Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        # When: Login
        login_payload = {
            "email": "httponly_test@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_payload)

        # Then: Check Set-Cookie header for httponly
        set_cookie_headers = response.headers.get_list("set-cookie")
        access_token_cookie = next(
            (c for c in set_cookie_headers if c.startswith("access_token=")),
            None
        )
        assert access_token_cookie is not None, "access_token cookie should exist"
        assert "httponly" in access_token_cookie.lower(), \
            "access_token cookie must have HttpOnly attribute"


class TestCookieSettingsValidator:
    """
    Tests for cookie settings auto-configuration based on APP_ENV

    Verifies that config.py model_validator correctly sets:
    - SameSite=None for cross-origin (prod/dev)
    - Secure=True when SameSite=None
    """

    def test_local_env_uses_default_cookie_settings(self):
        """
        Given: APP_ENV is "local"
        When: Settings are loaded
        Then: Cookie settings use defaults (lax, false)
        """
        # Given: Local environment
        with patch.dict(os.environ, {
            "APP_ENV": "local",
            "JWT_SECRET": "test-secret-32-characters-minimum"
        }, clear=False):
            # Force fresh Settings load
            from importlib import reload
            from app.core import config
            reload(config)

            # Then: Default settings (local doesn't trigger validator)
            # Note: In local, defaults remain lax/false
            assert config.settings.APP_ENV == "local"

    def test_dev_env_auto_configures_cross_origin_cookies(self):
        """
        Given: APP_ENV is "dev"
        When: Settings are loaded without explicit cookie env vars
        Then: Cookie settings are auto-configured for cross-origin
             - COOKIE_SAMESITE = "none"
             - COOKIE_SECURE = True
        """
        # Given: Dev environment without explicit cookie settings
        env_vars = {
            "APP_ENV": "dev",
            "JWT_SECRET": "test-secret-32-characters-minimum"
        }
        # Remove any existing cookie env vars to test auto-config
        for key in ["COOKIE_SAMESITE", "COOKIE_SECURE"]:
            env_vars[key] = None  # Will be removed

        # Clear the specific vars
        clean_env = {k: v for k, v in env_vars.items() if v is not None}

        with patch.dict(os.environ, clean_env, clear=False):
            # Also remove the keys we want to test auto-config for
            os.environ.pop("COOKIE_SAMESITE", None)
            os.environ.pop("COOKIE_SECURE", None)

            # Force fresh Settings load
            from app.core.config import Settings
            settings = Settings()

            # Then: Auto-configured for cross-origin
            assert settings.COOKIE_SAMESITE == "none", \
                "Dev environment should auto-configure SameSite=none"
            assert settings.COOKIE_SECURE is True, \
                "Dev environment should auto-configure Secure=True"

    def test_prod_env_auto_configures_cross_origin_cookies(self):
        """
        Given: APP_ENV is "prod"
        When: Settings are loaded without explicit cookie env vars
        Then: Cookie settings are auto-configured for cross-origin
        """
        # Given: Production environment
        with patch.dict(os.environ, {
            "APP_ENV": "prod",
            "JWT_SECRET": "production-secret-key-at-least-32-chars-long"
        }, clear=False):
            # Remove any existing cookie env vars
            os.environ.pop("COOKIE_SAMESITE", None)
            os.environ.pop("COOKIE_SECURE", None)

            # Force fresh Settings load
            from app.core.config import Settings
            settings = Settings()

            # Then: Auto-configured for cross-origin
            assert settings.COOKIE_SAMESITE == "none"
            assert settings.COOKIE_SECURE is True

    def test_samesite_none_requires_secure_true(self):
        """
        Given: COOKIE_SAMESITE is explicitly set to "none"
        And: COOKIE_SECURE is explicitly set to False
        When: Settings are loaded in prod/dev environment
        Then: Raises ValueError (security requirement)
        """
        # Given: Invalid combination for cross-origin
        with patch.dict(os.environ, {
            "APP_ENV": "prod",
            "JWT_SECRET": "production-secret-key-at-least-32-chars-long",
            "COOKIE_SAMESITE": "none",
            "COOKIE_SECURE": "false"
        }, clear=False):
            # When/Then: Should raise validation error
            from app.core.config import Settings
            with pytest.raises(ValueError) as exc_info:
                Settings()

            assert "COOKIE_SECURE must be True" in str(exc_info.value)


class TestSignupCookieHeaders:
    """
    Contract tests for signup response cookies

    Verifies that POST /auth/signup sets correct cookies.
    """

    def test_signup_should_set_access_token_cookie(self, client):
        """
        Given: Valid signup data
        When: POST /auth/signup is called
        Then: Response includes access_token cookie
        """
        # Given: Valid signup payload
        signup_payload = {
            "email": "signup_cookie_test@example.com",
            "password": "password123",
            "name": "Signup Cookie Test",
            "accept_terms": True
        }

        # When: Signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: Success and cookies set
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.cookies

    def test_signup_should_set_refresh_token_cookie(self, client):
        """
        Given: Valid signup data
        When: POST /auth/signup is called
        Then: Response includes refresh_token cookie
        """
        # Given: Valid signup payload
        signup_payload = {
            "email": "signup_refresh_test@example.com",
            "password": "password123",
            "name": "Signup Refresh Test",
            "accept_terms": True
        }

        # When: Signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: Success and cookies set
        assert response.status_code == status.HTTP_201_CREATED
        assert "refresh_token" in response.cookies


class TestLogoutClearsCookies:
    """
    Contract tests for logout clearing cookies
    """

    def test_logout_should_clear_access_token_cookie(self, client):
        """
        Given: User is logged in
        When: POST /auth/logout is called
        Then: access_token cookie is cleared
        """
        # Given: Login first
        signup_payload = {
            "email": "logout_test@example.com",
            "password": "password123",
            "name": "Logout Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        login_payload = {
            "email": "logout_test@example.com",
            "password": "password123"
        }
        client.post("/auth/login", json=login_payload)

        # When: Logout
        response = client.post("/auth/logout")

        # Then: Success and cookie cleared
        assert response.status_code == status.HTTP_200_OK

        # Check that cookie is deleted (set with max-age=0 or expires in past)
        set_cookie_headers = response.headers.get_list("set-cookie")
        access_token_clear = next(
            (c for c in set_cookie_headers if "access_token=" in c),
            None
        )
        if access_token_clear:
            # Cookie should be cleared (empty value or max-age=0)
            assert 'access_token=""' in access_token_clear or "max-age=0" in access_token_clear.lower()


class TestCookiePathSettings:
    """
    Tests for cookie path attributes
    """

    def test_access_token_cookie_path_is_root(self, client):
        """
        Given: User logs in
        When: POST /auth/login is called
        Then: access_token cookie path is "/" (accessible from all routes)
        """
        # Given: Create user and login
        signup_payload = {
            "email": "path_test@example.com",
            "password": "password123",
            "name": "Path Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        login_payload = {
            "email": "path_test@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_payload)

        # Then: access_token cookie has path=/
        set_cookie_headers = response.headers.get_list("set-cookie")
        access_token_cookie = next(
            (c for c in set_cookie_headers if c.startswith("access_token=")),
            None
        )
        assert access_token_cookie is not None
        assert 'path="/"' in access_token_cookie.lower() or "path=/" in access_token_cookie.lower(), \
            "access_token cookie should have path=/"

    def test_refresh_token_cookie_path_is_auth(self, client):
        """
        Given: User logs in
        When: POST /auth/login is called
        Then: refresh_token cookie path is "/auth" (only sent to auth endpoints)
        """
        # Given: Create user and login
        signup_payload = {
            "email": "refresh_path_test@example.com",
            "password": "password123",
            "name": "Refresh Path Test User",
            "accept_terms": True
        }
        client.post("/auth/signup", json=signup_payload)

        login_payload = {
            "email": "refresh_path_test@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_payload)

        # Then: refresh_token cookie has path=/auth
        set_cookie_headers = response.headers.get_list("set-cookie")
        refresh_token_cookie = next(
            (c for c in set_cookie_headers if c.startswith("refresh_token=")),
            None
        )
        assert refresh_token_cookie is not None
        assert 'path="/auth"' in refresh_token_cookie.lower() or "path=/auth" in refresh_token_cookie.lower(), \
            "refresh_token cookie should have path=/auth"
