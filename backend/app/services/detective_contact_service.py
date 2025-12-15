"""
Detective Contact Service
Issue #298 - FR-011~012, FR-016

Business logic for detective contact management.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User, UserRole
from app.repositories.detective_contact_repository import DetectiveContactRepository
from app.db.schemas import (
    DetectiveContactCreate,
    DetectiveContactUpdate,
    DetectiveContactResponse,
    DetectiveContactListResponse,
)


class DetectiveContactService:
    """Service for detective contact business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DetectiveContactRepository(db)

    def _check_lawyer_role(self, user_id: str) -> None:
        """Verify user is a lawyer"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.role != UserRole.LAWYER:
            raise PermissionError("Only lawyers can access detective contacts")

    def _validate_contact_info(self, phone: Optional[str], email: Optional[str]) -> None:
        """Validate that at least phone or email is provided"""
        if not phone and not email:
            raise ValueError("Either phone or email must be provided")

    def create_detective(
        self,
        lawyer_id: str,
        data: DetectiveContactCreate,
    ) -> DetectiveContactResponse:
        """Create a new detective contact"""
        self._check_lawyer_role(lawyer_id)
        self._validate_contact_info(data.phone, str(data.email) if data.email else None)

        detective = self.repository.create(
            lawyer_id=lawyer_id,
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            specialty=data.specialty,
            memo=data.memo,
        )
        return DetectiveContactResponse.model_validate(detective)

    def get_detectives(
        self,
        lawyer_id: str,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> DetectiveContactListResponse:
        """Get detective contacts for a lawyer"""
        self._check_lawyer_role(lawyer_id)

        detectives, total = self.repository.get_by_lawyer(
            lawyer_id=lawyer_id,
            search=search,
            page=page,
            limit=limit,
        )

        return DetectiveContactListResponse(
            items=[DetectiveContactResponse.model_validate(d) for d in detectives],
            total=total,
            page=page,
            limit=limit,
        )

    def get_detective(self, detective_id: str, lawyer_id: str) -> DetectiveContactResponse:
        """Get a specific detective contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(detective_id, lawyer_id):
            raise PermissionError("Detective not found or not authorized")

        detective = self.repository.get_by_id(detective_id)
        if not detective:
            raise KeyError("Detective not found")

        return DetectiveContactResponse.model_validate(detective)

    def update_detective(
        self,
        detective_id: str,
        lawyer_id: str,
        data: DetectiveContactUpdate,
    ) -> DetectiveContactResponse:
        """Update a detective contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(detective_id, lawyer_id):
            raise PermissionError("Detective not found or not authorized")

        # Validate contact info if both are being cleared
        current = self.repository.get_by_id(detective_id)
        new_phone = data.phone if data.phone is not None else current.phone
        new_email = str(data.email) if data.email is not None else current.email
        self._validate_contact_info(new_phone, new_email)

        detective = self.repository.update(
            detective_id=detective_id,
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            specialty=data.specialty,
            memo=data.memo,
        )

        if not detective:
            raise KeyError("Detective not found")

        return DetectiveContactResponse.model_validate(detective)

    def delete_detective(self, detective_id: str, lawyer_id: str) -> bool:
        """Delete a detective contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(detective_id, lawyer_id):
            raise PermissionError("Detective not found or not authorized")

        return self.repository.delete(detective_id)
