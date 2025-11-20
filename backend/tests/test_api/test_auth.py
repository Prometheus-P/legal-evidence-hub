"""
Test suite for Authentication API endpoints

Tests for:
- POST /auth/login - JWT issuance with expiration time
- Invalid credentials handling (401)
- JWT validation and user context
"""

import pytest
from datetime import datetime, timezone
from fastapi import status


class TestAuthLogin:
    """
    Test suite for POST /auth/login endpoint
    """

    def test_should_issue_jwt_on_successful_login(self, client, test_user):
        """
        Given: Valid email and password
        When: POST /auth/login is called
        Then:
            - Returns 200 status code
            - Response contains access_token
            - Response contains token_type "bearer"
            - Response contains expires_in (integer seconds)
            - Response contains user info (id, name, role)
        """
        # Given: Valid credentials for the test_user
        login_payload = {
            "email": test_user.email,
            "password": "correct_password123"
        }

        # When: POST /auth/login
        response = client.post("/auth/login", json=login_payload)

        # Then: Success response with JWT
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data

        # Validate token_type
        assert data["token_type"] == "bearer"

        # Validate expires_in is an integer (seconds)
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

        # Validate user info
        user = data["user"]
        assert "id" in user
        assert "name" in user
        assert "role" in user
        assert user["email"] == test_user.email

    def test_should_return_401_for_invalid_email(self, client, test_user):
        """
        Given: Invalid email (user does not exist)
        When: POST /auth/login is called
        Then:
            - Returns 401 Unauthorized
            - Response contains error message
            - Error message is intentionally generic (security best practice)
        """
        # Given: Invalid email
        login_payload = {
            "email": "nonexistent@example.com",
            "password": "any_password"
        }

        # When: POST /auth/login
        response = client.post("/auth/login", json=login_payload)

        # Then: 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "AUTHENTICATION_FAILED"
        # Generic message to prevent user enumeration
        assert "이메일 또는 비밀번호" in data["error"]["message"]

    def test_should_return_401_for_invalid_password(self, client, test_user):
        """
        Given: Valid email but incorrect password
        When: POST /auth/login is called
        Then:
            - Returns 401 Unauthorized
            - Response contains error message
            - Error message is intentionally generic (security best practice)
        """
        # Given: Valid email but wrong password
        login_payload = {
            "email": test_user.email,
            "password": "wrong_password"
        }

        # When: POST /auth/login
        response = client.post("/auth/login", json=login_payload)

        # Then: 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "AUTHENTICATION_FAILED"
        # Generic message to prevent user enumeration
        assert "이메일 또는 비밀번호" in data["error"]["message"]
