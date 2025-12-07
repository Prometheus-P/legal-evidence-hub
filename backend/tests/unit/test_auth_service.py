"""
Unit tests for Auth Service
TDD - Improving test coverage for auth_service.py
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.auth_service import AuthService
from app.db.models import UserRole
from app.middleware.error_handler import AuthenticationError, ConflictError, ValidationError


class TestAuthenticateUser:
    """Unit tests for authenticate_user method"""

    def test_authenticate_user_not_found(self):
        """Returns None when user not found"""
        mock_db = MagicMock()

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()

            service.user_repo.get_by_email.return_value = None

            result = service.authenticate_user("unknown@test.com", "password")

            assert result is None

    @patch('app.services.auth_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify):
        """Returns None when password is wrong"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.hashed_password = "hashed"
        mock_verify.return_value = False

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()

            service.user_repo.get_by_email.return_value = mock_user

            result = service.authenticate_user("user@test.com", "wrong")

            assert result is None


class TestLogin:
    """Unit tests for login method"""

    def test_login_authentication_failed(self):
        """Raises AuthenticationError when authentication fails"""
        mock_db = MagicMock()

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()

            # Mock authenticate_user to return None
            service.authenticate_user = MagicMock(return_value=None)

            with pytest.raises(AuthenticationError, match="이메일 또는 비밀번호"):
                service.login("user@test.com", "wrong")


class TestSignup:
    """Unit tests for signup method"""

    def test_signup_terms_not_accepted(self):
        """Raises ValidationError when terms not accepted"""
        mock_db = MagicMock()

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()
            service.SELF_SIGNUP_ROLES = {UserRole.LAWYER, UserRole.CLIENT, UserRole.DETECTIVE}

            with pytest.raises(ValidationError, match="이용약관 동의"):
                service.signup(
                    email="user@test.com",
                    password="password",
                    name="Test",
                    accept_terms=False
                )

    def test_signup_invalid_role(self):
        """Raises ValidationError when role not allowed for self-signup"""
        mock_db = MagicMock()

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()
            service.SELF_SIGNUP_ROLES = {UserRole.LAWYER, UserRole.CLIENT, UserRole.DETECTIVE}

            with pytest.raises(ValidationError, match="자가 등록"):
                service.signup(
                    email="user@test.com",
                    password="password",
                    name="Test",
                    accept_terms=True,
                    role=UserRole.ADMIN
                )

    def test_signup_duplicate_email(self):
        """Raises ConflictError when email already exists"""
        mock_db = MagicMock()

        with patch.object(AuthService, '__init__', lambda x, y: None):
            service = AuthService(mock_db)
            service.session = mock_db
            service.user_repo = MagicMock()
            service.SELF_SIGNUP_ROLES = {UserRole.LAWYER, UserRole.CLIENT, UserRole.DETECTIVE}

            service.user_repo.exists.return_value = True

            with pytest.raises(ConflictError, match="이미 등록된 이메일"):
                service.signup(
                    email="existing@test.com",
                    password="password",
                    name="Test",
                    accept_terms=True
                )
