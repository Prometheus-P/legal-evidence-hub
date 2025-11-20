"""
Case Service - Business logic for case management
Implements Service pattern per BACKEND_SERVICE_REPOSITORY_GUIDE.md
"""

from sqlalchemy.orm import Session
from typing import List
from app.db.models import Case
from app.db.schemas import CaseCreate, CaseOut
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.middleware import NotFoundError, PermissionError


class CaseService:
    """
    Service for case management business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)

    def create_case(self, case_data: CaseCreate, user_id: str) -> CaseOut:
        """
        Create a new case and add creator as owner

        Args:
            case_data: Case creation data
            user_id: ID of user creating the case

        Returns:
            Created case data
        """
        # Create case in database
        case = self.case_repo.create(
            title=case_data.title,
            description=case_data.description,
            created_by=user_id
        )

        # Add creator as owner in case_members
        self.member_repo.add_member(
            case_id=case.id,
            user_id=user_id,
            role="owner"
        )

        # Commit transaction
        self.db.commit()
        self.db.refresh(case)

        return CaseOut.model_validate(case)

    def get_cases_for_user(self, user_id: str) -> List[CaseOut]:
        """
        Get all cases accessible by user

        Args:
            user_id: User ID

        Returns:
            List of cases user has access to
        """
        cases = self.case_repo.get_all_for_user(user_id)
        return [CaseOut.model_validate(case) for case in cases]

    def get_case_by_id(self, case_id: str, user_id: str) -> CaseOut:
        """
        Get case by ID with permission check

        Args:
            case_id: Case ID
            user_id: User ID requesting access

        Returns:
            Case data

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have access
        """
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if user has access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        return CaseOut.model_validate(case)

    def delete_case(self, case_id: str, user_id: str):
        """
        Soft delete a case (set status to closed)

        Args:
            case_id: Case ID
            user_id: User ID requesting deletion

        Raises:
            NotFoundError: Case not found
            PermissionError: User does not have owner access
        """
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if user is owner
        member = self.member_repo.get_member(case_id, user_id)
        if not member or member.role != "owner":
            raise PermissionError("Only case owner can delete the case")

        # Soft delete
        self.case_repo.soft_delete(case_id)

        # TODO: Trigger OpenSearch index deletion
        # This will be implemented when OpenSearch integration is added

        self.db.commit()
