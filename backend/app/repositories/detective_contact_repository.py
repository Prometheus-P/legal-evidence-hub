"""
Detective Contact Repository
Issue #298 - FR-011~012, FR-016

Data access layer for detective contact operations.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import DetectiveContact


class DetectiveContactRepository:
    """Repository for detective contact CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        lawyer_id: str,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        specialty: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> DetectiveContact:
        """Create a new detective contact"""
        detective = DetectiveContact(
            lawyer_id=lawyer_id,
            name=name,
            phone=phone,
            email=email,
            specialty=specialty,
            memo=memo,
        )
        self.db.add(detective)
        self.db.commit()
        self.db.refresh(detective)
        return detective

    def get_by_id(self, detective_id: str) -> Optional[DetectiveContact]:
        """Get detective contact by ID"""
        return self.db.query(DetectiveContact).filter(DetectiveContact.id == detective_id).first()

    def get_by_lawyer(
        self,
        lawyer_id: str,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[DetectiveContact], int]:
        """Get detective contacts for a lawyer with optional search"""
        query = self.db.query(DetectiveContact).filter(DetectiveContact.lawyer_id == lawyer_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    DetectiveContact.name.ilike(search_pattern),
                    DetectiveContact.phone.ilike(search_pattern),
                    DetectiveContact.email.ilike(search_pattern),
                    DetectiveContact.specialty.ilike(search_pattern),
                )
            )

        total = query.count()
        detectives = (
            query.order_by(DetectiveContact.name.asc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return detectives, total

    def update(
        self,
        detective_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        specialty: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> Optional[DetectiveContact]:
        """Update a detective contact"""
        detective = self.get_by_id(detective_id)
        if not detective:
            return None

        if name is not None:
            detective.name = name
        if phone is not None:
            detective.phone = phone
        if email is not None:
            detective.email = email
        if specialty is not None:
            detective.specialty = specialty
        if memo is not None:
            detective.memo = memo

        self.db.commit()
        self.db.refresh(detective)
        return detective

    def delete(self, detective_id: str) -> bool:
        """Delete a detective contact (hard delete)"""
        detective = self.get_by_id(detective_id)
        if detective:
            self.db.delete(detective)
            self.db.commit()
            return True
        return False

    def belongs_to_lawyer(self, detective_id: str, lawyer_id: str) -> bool:
        """Check if detective contact belongs to the lawyer"""
        detective = self.get_by_id(detective_id)
        return detective is not None and detective.lawyer_id == lawyer_id
