"""
Client Contact Service
Issue #297 - FR-009~010, FR-015

Business logic for client contact management.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import User, UserRole
from app.repositories.client_contact_repository import ClientContactRepository
from app.db.schemas import (
    ClientContactCreate,
    ClientContactUpdate,
    ClientContactResponse,
    ClientContactListResponse,
)


class ClientContactService:
    """Service for client contact business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ClientContactRepository(db)

    def _check_lawyer_role(self, user_id: str) -> None:
        """Verify user is a lawyer"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.role != UserRole.LAWYER:
            raise PermissionError("Only lawyers can access client contacts")

    def _validate_contact_info(self, phone: Optional[str], email: Optional[str]) -> None:
        """Validate that at least phone or email is provided"""
        if not phone and not email:
            raise ValueError("Either phone or email must be provided")

    def create_client(
        self,
        lawyer_id: str,
        data: ClientContactCreate,
    ) -> ClientContactResponse:
        """Create a new client contact"""
        self._check_lawyer_role(lawyer_id)
        self._validate_contact_info(data.phone, str(data.email) if data.email else None)

        client = self.repository.create(
            lawyer_id=lawyer_id,
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            memo=data.memo,
        )
        return ClientContactResponse.model_validate(client)

    def get_clients(
        self,
        lawyer_id: str,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> ClientContactListResponse:
        """Get client contacts for a lawyer"""
        self._check_lawyer_role(lawyer_id)

        clients, total = self.repository.get_by_lawyer(
            lawyer_id=lawyer_id,
            search=search,
            page=page,
            limit=limit,
        )

        return ClientContactListResponse(
            items=[ClientContactResponse.model_validate(c) for c in clients],
            total=total,
            page=page,
            limit=limit,
        )

    def get_client(self, client_id: str, lawyer_id: str) -> ClientContactResponse:
        """Get a specific client contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(client_id, lawyer_id):
            raise PermissionError("Client not found or not authorized")

        client = self.repository.get_by_id(client_id)
        if not client:
            raise KeyError("Client not found")

        return ClientContactResponse.model_validate(client)

    def update_client(
        self,
        client_id: str,
        lawyer_id: str,
        data: ClientContactUpdate,
    ) -> ClientContactResponse:
        """Update a client contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(client_id, lawyer_id):
            raise PermissionError("Client not found or not authorized")

        # Validate contact info if both are being cleared
        current = self.repository.get_by_id(client_id)
        new_phone = data.phone if data.phone is not None else current.phone
        new_email = str(data.email) if data.email is not None else current.email
        self._validate_contact_info(new_phone, new_email)

        client = self.repository.update(
            client_id=client_id,
            name=data.name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            memo=data.memo,
        )

        if not client:
            raise KeyError("Client not found")

        return ClientContactResponse.model_validate(client)

    def delete_client(self, client_id: str, lawyer_id: str) -> bool:
        """Delete a client contact"""
        self._check_lawyer_role(lawyer_id)

        if not self.repository.belongs_to_lawyer(client_id, lawyer_id):
            raise PermissionError("Client not found or not authorized")

        return self.repository.delete(client_id)
