"""
Test suite for Authentication API endpoints

Tests for:
- POST /auth/login - JWT issuance with expiration time
- POST /auth/signup - User registration with JWT issuance
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


class TestAuthSignup:
    """
    Test suite for POST /auth/signup endpoint
    """

    def test_should_create_user_and_issue_jwt_on_successful_signup(self, client):
        """
        Given: Valid signup data with accept_terms=true
        When: POST /auth/signup is called
        Then:
            - Returns 201 status code
            - Response contains access_token
            - Response contains token_type "bearer"
            - Response contains expires_in (integer seconds)
            - Response contains user info with LAWYER role
            - User is created in database
        """
        # Given: Valid signup data
        signup_payload = {
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User",
            "accept_terms": True
        }

        # When: POST /auth/signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: Success response with JWT
        assert response.status_code == status.HTTP_201_CREATED

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
        assert "status" in user
        assert "created_at" in user
        assert user["email"] == "newuser@example.com"
        assert user["name"] == "New User"
        assert user["role"] == "lawyer"  # Default role for signup
        assert user["status"] == "active"

    def test_should_return_409_when_email_already_exists(self, client, test_user):
        """
        Given: Email that already exists in database
        When: POST /auth/signup is called
        Then:
            - Returns 409 Conflict
            - Response contains error message about duplicate email
        """
        # Given: Signup with existing email
        signup_payload = {
            "email": test_user.email,  # This email already exists
            "password": "password123",
            "name": "Another User",
            "accept_terms": True
        }

        # When: POST /auth/signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT

        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "CONFLICT"
        assert "이미 등록된 이메일" in data["error"]["message"]

    def test_should_return_400_when_accept_terms_is_false(self, client):
        """
        Given: Valid signup data but accept_terms=false
        When: POST /auth/signup is called
        Then:
            - Returns 400 Bad Request
            - Response contains error message about terms acceptance
        """
        # Given: accept_terms is false
        signup_payload = {
            "email": "user@example.com",
            "password": "password123",
            "name": "User",
            "accept_terms": False
        }

        # When: POST /auth/signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: 400 Bad Request
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "이용약관 동의" in data["error"]["message"]

    def test_should_hash_password_with_bcrypt(self, client):
        """
        Given: Valid signup data
        When: POST /auth/signup is called
        Then:
            - Password is hashed with bcrypt (not stored in plain text)
            - Can login with the same password
        """
        # Given: Valid signup data
        signup_payload = {
            "email": "secure@example.com",
            "password": "securepass123",
            "name": "Secure User",
            "accept_terms": True
        }

        # When: POST /auth/signup
        signup_response = client.post("/auth/signup", json=signup_payload)
        assert signup_response.status_code == status.HTTP_201_CREATED

        # Then: Verify password is hashed by attempting login
        login_payload = {
            "email": "secure@example.com",
            "password": "securepass123"
        }
        login_response = client.post("/auth/login", json=login_payload)
        assert login_response.status_code == status.HTTP_200_OK

        # Verify stored password is not plain text
        from app.db.session import get_db
        from app.db.models import User

        db = next(get_db())
        user = db.query(User).filter(User.email == "secure@example.com").first()
        assert user.hashed_password != "securepass123"
        assert user.hashed_password.startswith("$2b$")  # Bcrypt hash prefix

    def test_should_reject_short_password(self, client):
        """
        Given: Password with less than 8 characters
        When: POST /auth/signup is called
        Then:
            - Returns 422 Unprocessable Entity (Pydantic validation error)
        """
        # Given: Short password (7 characters)
        signup_payload = {
            "email": "user@example.com",
            "password": "short12",  # Only 7 characters
            "name": "User",
            "accept_terms": True
        }

        # When: POST /auth/signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: 422 Validation Error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_should_reject_invalid_email(self, client):
        """
        Given: Invalid email format
        When: POST /auth/signup is called
        Then:
            - Returns 422 Unprocessable Entity (Pydantic validation error)
        """
        # Given: Invalid email format
        signup_payload = {
            "email": "not-an-email",
            "password": "password123",
            "name": "User",
            "accept_terms": True
        }

        # When: POST /auth/signup
        response = client.post("/auth/signup", json=signup_payload)

        # Then: 422 Validation Error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
