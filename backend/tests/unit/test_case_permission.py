"""
Unit tests for Case Permission Middleware

Tests the CasePermissionChecker class and dependency factories
for case-level access control.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.middleware.case_permission import (
    CasePermissionChecker,
    require_case_access,
    require_case_write_access,
    require_case_owner,
    require_case_access_or_admin,
    require_case_write_or_admin,
    require_case_owner_or_admin
)
from app.middleware import PermissionError
from app.db.models import CaseMemberRole, UserRole


class TestCasePermissionChecker:
    """Unit tests for CasePermissionChecker class"""

    def test_check_read_access_returns_true_for_member(self):
        """Returns True when user is a case member"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.has_access.return_value = True
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_read_access("case_123", "user_456")

            assert result is True
            mock_repo.has_access.assert_called_once_with("case_123", "user_456")

    def test_check_read_access_returns_false_for_non_member(self):
        """Returns False when user is not a case member"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.has_access.return_value = False
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_read_access("case_123", "user_456")

            assert result is False

    def test_check_write_access_returns_true_for_owner(self):
        """Returns True when user is case owner"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.has_write_access.return_value = True
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_write_access("case_123", "user_456")

            assert result is True
            mock_repo.has_write_access.assert_called_once_with("case_123", "user_456")

    def test_check_write_access_returns_false_for_viewer(self):
        """Returns False when user is only a viewer"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.has_write_access.return_value = False
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_write_access("case_123", "user_456")

            assert result is False

    def test_check_owner_access_returns_true_for_owner(self):
        """Returns True when user is case owner"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.is_owner.return_value = True
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_owner_access("case_123", "user_456")

            assert result is True
            mock_repo.is_owner.assert_called_once_with("case_123", "user_456")

    def test_check_owner_access_returns_false_for_member(self):
        """Returns False when user is member but not owner"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.is_owner.return_value = False
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.check_owner_access("case_123", "user_456")

            assert result is False

    def test_get_member_role_returns_role(self):
        """Returns member role when user is a member"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_member.role = CaseMemberRole.MEMBER

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_member.return_value = mock_member
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.get_member_role("case_123", "user_456")

            assert result == CaseMemberRole.MEMBER

    def test_get_member_role_returns_none_for_non_member(self):
        """Returns None when user is not a member"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CaseMemberRepository') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_member.return_value = None
            mock_repo_class.return_value = mock_repo

            checker = CasePermissionChecker(mock_db)
            result = checker.get_member_role("case_123", "user_456")

            assert result is None


class TestRequireCaseAccess:
    """Unit tests for require_case_access dependency"""

    def test_returns_user_id_when_has_access(self):
        """Returns user_id when user has read access"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_read_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_access("case_123", mock_db, "user_456")

            assert result == "user_456"
            mock_checker.check_read_access.assert_called_once_with("case_123", "user_456")

    def test_raises_permission_error_when_no_access(self):
        """Raises PermissionError when user has no access"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_read_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError) as exc_info:
                require_case_access("case_123", mock_db, "user_456")

            assert "접근 권한이 없습니다" in str(exc_info.value)


class TestRequireCaseWriteAccess:
    """Unit tests for require_case_write_access dependency"""

    def test_returns_user_id_when_has_write_access(self):
        """Returns user_id when user has write access"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_write_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_write_access("case_123", mock_db, "user_456")

            assert result == "user_456"

    def test_raises_permission_error_for_viewer(self):
        """Raises PermissionError when user is viewer"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_write_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError) as exc_info:
                require_case_write_access("case_123", mock_db, "user_456")

            assert "수정할 권한이 없습니다" in str(exc_info.value)


class TestRequireCaseOwner:
    """Unit tests for require_case_owner dependency"""

    def test_returns_user_id_when_is_owner(self):
        """Returns user_id when user is owner"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_owner_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_owner("case_123", mock_db, "user_456")

            assert result == "user_456"

    def test_raises_permission_error_when_not_owner(self):
        """Raises PermissionError when user is not owner"""
        mock_db = MagicMock()

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_owner_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError) as exc_info:
                require_case_owner("case_123", mock_db, "user_456")

            assert "소유자만" in str(exc_info.value)


class TestRequireCaseAccessOrAdmin:
    """Unit tests for require_case_access_or_admin dependency"""

    def test_allows_admin_without_membership(self):
        """Admin users can access any case"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "admin_123"
        mock_user.role = UserRole.ADMIN

        result = require_case_access_or_admin("case_123", mock_db, mock_user)

        assert result == "admin_123"

    def test_allows_member_non_admin(self):
        """Non-admin members can access their cases"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_read_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_access_or_admin("case_123", mock_db, mock_user)

            assert result == "user_456"

    def test_denies_non_member_non_admin(self):
        """Non-admin non-members are denied access"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_read_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError):
                require_case_access_or_admin("case_123", mock_db, mock_user)


class TestRequireCaseWriteOrAdmin:
    """Unit tests for require_case_write_or_admin dependency"""

    def test_allows_admin_without_membership(self):
        """Admin users can modify any case"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "admin_123"
        mock_user.role = UserRole.ADMIN

        result = require_case_write_or_admin("case_123", mock_db, mock_user)

        assert result == "admin_123"

    def test_allows_member_with_write_access(self):
        """Members with write access can modify cases"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_write_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_write_or_admin("case_123", mock_db, mock_user)

            assert result == "user_456"

    def test_denies_viewer_non_admin(self):
        """Viewers without admin role are denied write access"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_write_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError):
                require_case_write_or_admin("case_123", mock_db, mock_user)


class TestRequireCaseOwnerOrAdmin:
    """Unit tests for require_case_owner_or_admin dependency"""

    def test_allows_admin_without_ownership(self):
        """Admin users can perform owner actions on any case"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "admin_123"
        mock_user.role = UserRole.ADMIN

        result = require_case_owner_or_admin("case_123", mock_db, mock_user)

        assert result == "admin_123"

    def test_allows_owner_non_admin(self):
        """Case owners can perform owner actions"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_owner_access.return_value = True
            mock_checker_class.return_value = mock_checker

            result = require_case_owner_or_admin("case_123", mock_db, mock_user)

            assert result == "user_456"

    def test_denies_member_non_owner_non_admin(self):
        """Members who are not owners or admins are denied"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user_456"
        mock_user.role = UserRole.LAWYER

        with patch('app.middleware.case_permission.CasePermissionChecker') as mock_checker_class:
            mock_checker = MagicMock()
            mock_checker.check_owner_access.return_value = False
            mock_checker_class.return_value = mock_checker

            with pytest.raises(PermissionError) as exc_info:
                require_case_owner_or_admin("case_123", mock_db, mock_user)

            assert "소유자 또는 관리자" in str(exc_info.value)
