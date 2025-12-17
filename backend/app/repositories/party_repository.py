"""
Party Repository - Data access layer for PartyNode model
Implements Repository pattern per BACKEND_SERVICE_REPOSITORY_GUIDE.md
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import PartyNode, PartyType
from datetime import datetime, timezone
import uuid


class PartyRepository:
    """
    Repository for PartyNode database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        case_id: str,
        type: PartyType,
        name: str,
        alias: Optional[str] = None,
        birth_year: Optional[int] = None,
        occupation: Optional[str] = None,
        position_x: int = 0,
        position_y: int = 0,
        extra_data: Optional[dict] = None
    ) -> PartyNode:
        """
        Create a new party node in the database
        """
        party = PartyNode(
            id=f"party_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            type=type,
            name=name,
            alias=alias,
            birth_year=birth_year,
            occupation=occupation,
            position_x=position_x,
            position_y=position_y,
            extra_data=extra_data or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        self.session.add(party)
        self.session.flush()

        return party

    def get_by_id(self, party_id: str) -> Optional[PartyNode]:
        """Get party node by ID"""
        return self.session.query(PartyNode).filter(PartyNode.id == party_id).first()

    def get_all_for_case(self, case_id: str) -> List[PartyNode]:
        """Get all party nodes for a case"""
        return (
            self.session.query(PartyNode)
            .filter(PartyNode.case_id == case_id)
            .order_by(PartyNode.created_at)
            .all()
        )

    def get_by_type(self, case_id: str, party_type: PartyType) -> List[PartyNode]:
        """Get all party nodes of a specific type for a case"""
        return (
            self.session.query(PartyNode)
            .filter(PartyNode.case_id == case_id, PartyNode.type == party_type)
            .order_by(PartyNode.created_at)
            .all()
        )

    def update(
        self,
        party_id: str,
        name: Optional[str] = None,
        alias: Optional[str] = None,
        birth_year: Optional[int] = None,
        occupation: Optional[str] = None,
        position_x: Optional[int] = None,
        position_y: Optional[int] = None,
        extra_data: Optional[dict] = None
    ) -> Optional[PartyNode]:
        """Update a party node"""
        party = self.get_by_id(party_id)
        if not party:
            return None

        if name is not None:
            party.name = name
        if alias is not None:
            party.alias = alias
        if birth_year is not None:
            party.birth_year = birth_year
        if occupation is not None:
            party.occupation = occupation
        if position_x is not None:
            party.position_x = position_x
        if position_y is not None:
            party.position_y = position_y
        if extra_data is not None:
            party.extra_data = extra_data

        party.updated_at = datetime.now(timezone.utc)
        self.session.flush()

        return party

    def delete(self, party_id: str) -> bool:
        """Delete a party node"""
        party = self.get_by_id(party_id)
        if not party:
            return False

        self.session.delete(party)
        self.session.flush()

        return True

    def count_for_case(self, case_id: str) -> int:
        """Count party nodes for a case"""
        return (
            self.session.query(PartyNode)
            .filter(PartyNode.case_id == case_id)
            .count()
        )
