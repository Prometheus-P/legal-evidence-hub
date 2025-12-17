"""
Case Permission Middleware - Reusable case-level access control

Provides dependency injection factories for case permission checks.
Integrates with existing JWT authentication via dependencies.py.

Usage:
    from app.middleware.case_permission import (
        require_case_access,
        require_case_write_access,
        require_case_owner
    )

    @router.get("/cases/{case_id}")
    async def get_case(
        case_id: str,
        user_id: str = Depends(require_case_access(case_id))
    ):
        ...
"""

from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_id, get_db, get_current_user
from app.repositories.case_member_repository import CaseMemberRepository
from app.middleware import PermissionError
from app.db.models import User, UserRole, CaseMemberRole
import logging

logger = logging.getLogger(__name__)


class CasePermissionChecker:
    """
    Reusable case permission checker class.

    Provides methods to check case access at different permission levels:
    - read: Any case member (OWNER, MEMBER, VIEWER)
    - write: OWNER or MEMBER only
    - owner: OWNER only

    Attributes:
        db: Database session
        member_repo: CaseMemberRepository instance
    """

    def __init__(self, db: Session):
        self.db = db
        self.member_repo = CaseMemberRepository(db)

    def check_read_access(self, case_id: str, user_id: str) -> bool:
        """
        Check if user has read access to a case.

        Args:
            case_id: Case ID to check
            user_id: User ID to verify

        Returns:
            True if user has read access
        """
        return self.member_repo.has_access(case_id, user_id)

    def check_write_access(self, case_id: str, user_id: str) -> bool:
        """
        Check if user has write access to a case.

        Args:
            case_id: Case ID to check
            user_id: User ID to verify

        Returns:
            True if user has write access (OWNER or MEMBER)
        """
        return self.member_repo.has_write_access(case_id, user_id)

    def check_owner_access(self, case_id: str, user_id: str) -> bool:
        """
        Check if user is the owner of a case.

        Args:
            case_id: Case ID to check
            user_id: User ID to verify

        Returns:
            True if user is case owner
        """
        return self.member_repo.is_owner(case_id, user_id)

    def get_member_role(self, case_id: str, user_id: str) -> Optional[CaseMemberRole]:
        """
        Get user's role in a case.

        Args:
            case_id: Case ID to check
            user_id: User ID to verify

        Returns:
            CaseMemberRole if user is a member, None otherwise
        """
        member = self.member_repo.get_member(case_id, user_id)
        return member.role if member else None


def get_permission_checker(
    db: Session = Depends(get_db)
) -> CasePermissionChecker:
    """
    Dependency to get CasePermissionChecker instance.

    Args:
        db: Database session (injected)

    Returns:
        CasePermissionChecker instance
    """
    return CasePermissionChecker(db)


def require_case_access(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> str:
    """
    Verify user has read access to a case (any member role).

    This is a FastAPI dependency that can be used in route handlers
    to ensure the current user has access to view the case.

    Args:
        case_id: Case ID to check access for
        db: Database session (injected via Depends)
        user_id: User ID to check (injected via Depends)

    Returns:
        user_id if access granted

    Raises:
        PermissionError: User is not a member of this case
    """
    checker = CasePermissionChecker(db)

    if not checker.check_read_access(case_id, user_id):
        logger.warning(f"Access denied: user={user_id} attempted to access case={case_id}")
        raise PermissionError("이 케이스에 대한 접근 권한이 없습니다.")

    return user_id


def require_case_write_access(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> str:
    """
    Verify user has write access to a case (OWNER or MEMBER role).

    VIEWER role does NOT have write access.

    Args:
        case_id: Case ID to check access for
        db: Database session (injected via Depends)
        user_id: User ID to check (injected via Depends)

    Returns:
        user_id if access granted

    Raises:
        PermissionError: User is VIEWER or not a member
    """
    checker = CasePermissionChecker(db)

    if not checker.check_write_access(case_id, user_id):
        logger.warning(f"Write access denied: user={user_id} attempted to modify case={case_id}")
        raise PermissionError("이 케이스를 수정할 권한이 없습니다.")

    return user_id


def require_case_owner(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> str:
    """
    Verify user is the owner of a case.

    Only the case OWNER can perform certain actions (e.g., delete case,
    manage members).

    Args:
        case_id: Case ID to check ownership for
        db: Database session (injected via Depends)
        user_id: User ID to check (injected via Depends)

    Returns:
        user_id if user is owner

    Raises:
        PermissionError: User is not the case owner
    """
    checker = CasePermissionChecker(db)

    if not checker.check_owner_access(case_id, user_id):
        logger.warning(f"Owner access denied: user={user_id} is not owner of case={case_id}")
        raise PermissionError("케이스 소유자만 이 작업을 수행할 수 있습니다.")

    return user_id


def require_case_access_or_admin(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Verify user has read access OR is an admin.

    Admins can access any case without being a member.

    Args:
        case_id: Case ID to check access for
        db: Database session (injected via Depends)
        current_user: Current authenticated user (injected via Depends)

    Returns:
        user_id if access granted

    Raises:
        PermissionError: User is not a member and not admin
    """
    # Admins can access any case
    if current_user.role == UserRole.ADMIN:
        return current_user.id

    checker = CasePermissionChecker(db)

    if not checker.check_read_access(case_id, current_user.id):
        logger.warning(
            f"Access denied: user={current_user.id} attempted to access case={case_id}"
        )
        raise PermissionError("이 케이스에 대한 접근 권한이 없습니다.")

    return current_user.id


def require_case_write_or_admin(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Verify user has write access OR is an admin.

    Admins can modify any case without being a member.

    Args:
        case_id: Case ID to check access for
        db: Database session (injected via Depends)
        current_user: Current authenticated user (injected via Depends)

    Returns:
        user_id if access granted

    Raises:
        PermissionError: User is VIEWER or not a member, and not admin
    """
    # Admins can modify any case
    if current_user.role == UserRole.ADMIN:
        return current_user.id

    checker = CasePermissionChecker(db)

    if not checker.check_write_access(case_id, current_user.id):
        logger.warning(
            f"Write access denied: user={current_user.id} attempted to modify case={case_id}"
        )
        raise PermissionError("이 케이스를 수정할 권한이 없습니다.")

    return current_user.id


def require_case_owner_or_admin(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Verify user is case owner OR is an admin.

    Admins can perform owner-level actions on any case.

    Args:
        case_id: Case ID to check ownership for
        db: Database session (injected via Depends)
        current_user: Current authenticated user (injected via Depends)

    Returns:
        user_id if user is owner or admin

    Raises:
        PermissionError: User is not the case owner and not admin
    """
    # Admins can perform owner actions on any case
    if current_user.role == UserRole.ADMIN:
        return current_user.id

    checker = CasePermissionChecker(db)

    if not checker.check_owner_access(case_id, current_user.id):
        logger.warning(
            f"Owner access denied: user={current_user.id} is not owner of case={case_id}"
        )
        raise PermissionError("케이스 소유자 또는 관리자만 이 작업을 수행할 수 있습니다.")

    return current_user.id
