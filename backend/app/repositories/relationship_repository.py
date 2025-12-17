"""
Relationship Repository - Data access layer for party relationships
007-lawyer-portal-v1: US1 (Party Relationship Graph)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date
import uuid

from app.db.models import PartyRelationship, RelationshipType


class RelationshipRepository:
    """Repository for PartyRelationship CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, relationship_id: str) -> Optional[PartyRelationship]:
        """Get relationship by ID"""
        return self.db.query(PartyRelationship).filter(
            PartyRelationship.id == relationship_id
        ).first()

    def get_by_case_id(
        self,
        case_id: str,
        relationship_type: Optional[RelationshipType] = None,
        party_id: Optional[str] = None
    ) -> List[PartyRelationship]:
        """
        Get all relationships for a case, optionally filtered.

        Args:
            case_id: Case UUID
            relationship_type: Optional filter by relationship type
            party_id: Optional filter by party involvement (source or target)

        Returns:
            List of PartyRelationship objects
        """
        query = self.db.query(PartyRelationship).filter(
            PartyRelationship.case_id == case_id
        )

        if relationship_type:
            query = query.filter(PartyRelationship.type == relationship_type)

        if party_id:
            query = query.filter(
                or_(
                    PartyRelationship.source_party_id == party_id,
                    PartyRelationship.target_party_id == party_id
                )
            )

        return query.order_by(PartyRelationship.created_at.asc()).all()

    def get_by_parties(
        self,
        source_party_id: str,
        target_party_id: str,
        relationship_type: Optional[RelationshipType] = None
    ) -> Optional[PartyRelationship]:
        """
        Get relationship between two specific parties.

        Args:
            source_party_id: Source party UUID
            target_party_id: Target party UUID
            relationship_type: Optional specific type

        Returns:
            PartyRelationship if exists, None otherwise
        """
        query = self.db.query(PartyRelationship).filter(
            and_(
                PartyRelationship.source_party_id == source_party_id,
                PartyRelationship.target_party_id == target_party_id
            )
        )

        if relationship_type:
            query = query.filter(PartyRelationship.type == relationship_type)

        return query.first()

    def check_duplicate(
        self,
        case_id: str,
        source_party_id: str,
        target_party_id: str,
        relationship_type: RelationshipType
    ) -> bool:
        """
        Check if a duplicate relationship exists.

        Returns True if a relationship with the same type between
        the same two parties already exists.
        """
        existing = self.db.query(PartyRelationship).filter(
            and_(
                PartyRelationship.case_id == case_id,
                PartyRelationship.source_party_id == source_party_id,
                PartyRelationship.target_party_id == target_party_id,
                PartyRelationship.type == relationship_type
            )
        ).first()

        return existing is not None

    def create(
        self,
        case_id: str,
        source_party_id: str,
        target_party_id: str,
        type: RelationshipType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> PartyRelationship:
        """
        Create a new relationship between parties.

        Args:
            case_id: Case UUID
            source_party_id: Source party UUID
            target_party_id: Target party UUID
            type: Relationship type
            start_date: Optional relationship start date
            end_date: Optional relationship end date
            notes: Optional notes

        Returns:
            Created PartyRelationship object
        """
        now = datetime.utcnow()

        # Convert date to datetime if provided
        start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_dt = datetime.combine(end_date, datetime.min.time()) if end_date else None

        relationship = PartyRelationship(
            id=str(uuid.uuid4()),
            case_id=case_id,
            source_party_id=source_party_id,
            target_party_id=target_party_id,
            type=type,
            start_date=start_dt,
            end_date=end_dt,
            notes=notes,
            created_at=now,
            updated_at=now
        )

        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)

        return relationship

    def update(
        self,
        relationship: PartyRelationship,
        type: Optional[RelationshipType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> PartyRelationship:
        """
        Update a relationship.

        Args:
            relationship: PartyRelationship object to update
            Other args: Fields to update (None = no change)

        Returns:
            Updated PartyRelationship object
        """
        if type is not None:
            relationship.type = type
        if start_date is not None:
            relationship.start_date = datetime.combine(start_date, datetime.min.time())
        if end_date is not None:
            relationship.end_date = datetime.combine(end_date, datetime.min.time())
        if notes is not None:
            relationship.notes = notes

        relationship.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(relationship)

        return relationship

    def delete(self, relationship: PartyRelationship) -> bool:
        """
        Delete a relationship.

        Note: This will cascade delete related evidence links.

        Args:
            relationship: PartyRelationship object to delete

        Returns:
            True if deleted successfully
        """
        self.db.delete(relationship)
        self.db.commit()
        return True

    def count_by_case_id(self, case_id: str) -> int:
        """Count relationships for a case"""
        return self.db.query(PartyRelationship).filter(
            PartyRelationship.case_id == case_id
        ).count()
