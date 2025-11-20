"""
CaseMember Repository - Data access layer for CaseMember model
Handles case membership and permissions
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.db.models import CaseMember


class CaseMemberRepository:
    """
    Repository for CaseMember database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def add_member(self, case_id: str, user_id: str, role: str = "owner") -> CaseMember:
        """
        Add a member to a case

        Args:
            case_id: Case ID
            user_id: User ID
            role: Member role (owner, member, viewer)

        Returns:
            Created CaseMember instance
        """
        member = CaseMember(
            case_id=case_id,
            user_id=user_id,
            role=role
        )

        self.session.add(member)
        self.session.flush()

        return member

    def get_member(self, case_id: str, user_id: str) -> Optional[CaseMember]:
        """
        Get a specific case member

        Args:
            case_id: Case ID
            user_id: User ID

        Returns:
            CaseMember instance if found, None otherwise
        """
        return (
            self.session.query(CaseMember)
            .filter(CaseMember.case_id == case_id)
            .filter(CaseMember.user_id == user_id)
            .first()
        )

    def has_access(self, case_id: str, user_id: str) -> bool:
        """
        Check if user has access to a case

        Args:
            case_id: Case ID
            user_id: User ID

        Returns:
            True if user has access, False otherwise
        """
        return self.get_member(case_id, user_id) is not None

    def remove_member(self, case_id: str, user_id: str) -> bool:
        """
        Remove a member from a case

        Args:
            case_id: Case ID
            user_id: User ID

        Returns:
            True if removed, False if not found
        """
        member = self.get_member(case_id, user_id)
        if not member:
            return False

        self.session.delete(member)
        self.session.flush()
        return True
