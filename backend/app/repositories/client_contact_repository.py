"""
Client Contact Repository
Issue #297 - FR-009~010, FR-015

Data access layer for client contact operations.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import ClientContact


class ClientContactRepository:
    """Repository for client contact CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        lawyer_id: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> ClientContact:
        """Create a new client contact"""
        client = ClientContact(
            lawyer_id=lawyer_id,
            name=name,
            phone=phone,
            email=email,
            memo=memo,
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_id(self, client_id: str) -> Optional[ClientContact]:
        """Get client contact by ID"""
        return self.db.query(ClientContact).filter(ClientContact.id == client_id).first()

    def get_by_lawyer(
        self,
        lawyer_id: str,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[ClientContact], int]:
        """Get client contacts for a lawyer with optional search"""
        query = self.db.query(ClientContact).filter(ClientContact.lawyer_id == lawyer_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    ClientContact.name.ilike(search_pattern),
                    ClientContact.phone.ilike(search_pattern),
                    ClientContact.email.ilike(search_pattern),
                )
            )

        total = query.count()
        clients = (
            query.order_by(ClientContact.name.asc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return clients, total

    def update(
        self,
        client_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> Optional[ClientContact]:
        """Update a client contact"""
        client = self.get_by_id(client_id)
        if not client:
            return None

        if name is not None:
            client.name = name
        if phone is not None:
            client.phone = phone
        if email is not None:
            client.email = email
        if memo is not None:
            client.memo = memo

        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client_id: str) -> bool:
        """Delete a client contact (hard delete)"""
        client = self.get_by_id(client_id)
        if client:
            self.db.delete(client)
            self.db.commit()
            return True
        return False

    def belongs_to_lawyer(self, client_id: str, lawyer_id: str) -> bool:
        """Check if client contact belongs to the lawyer"""
        client = self.get_by_id(client_id)
        return client is not None and client.lawyer_id == lawyer_id
