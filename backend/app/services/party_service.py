"""
Party Service - Business logic for party management
007-lawyer-portal-v1: US1 (Party Relationship Graph)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import PartyNode, PartyType
from app.db.schemas import (
    PartyNodeCreate,
    PartyNodeUpdate,
    PartyNodeResponse,
    Position
)
from app.repositories.party_repository import PartyRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.case_repository import CaseRepository
from app.middleware import NotFoundError
import logging

logger = logging.getLogger(__name__)


class PartyService:
    """
    Service for party node business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.party_repo = PartyRepository(db)
        self.relationship_repo = RelationshipRepository(db)
        self.case_repo = CaseRepository(db)

    def create_party(
        self,
        case_id: str,
        data: PartyNodeCreate,
        user_id: str
    ) -> PartyNodeResponse:
        """
        Create a new party node for a case

        Args:
            case_id: Case ID
            data: Party creation data
            user_id: User performing the action

        Returns:
            Created party node response

        Raises:
            NotFoundError: Case not found
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # Create party node
        party = self.party_repo.create(
            case_id=case_id,
            type=data.type,
            name=data.name,
            alias=data.alias,
            birth_year=data.birth_year,
            occupation=data.occupation,
            position_x=int(data.position.x) if data.position else 0,
            position_y=int(data.position.y) if data.position else 0,
            extra_data=data.extra_data
        )

        self.db.commit()
        logger.info(f"Party created: {party.id} for case {case_id} by user {user_id}")

        return self._to_response(party)

    def get_party(self, party_id: str) -> PartyNodeResponse:
        """
        Get a party node by ID

        Args:
            party_id: Party node ID

        Returns:
            Party node response

        Raises:
            NotFoundError: Party not found
        """
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise NotFoundError(f"당사자를 찾을 수 없습니다: {party_id}")

        return self._to_response(party)

    def get_parties_for_case(
        self,
        case_id: str,
        party_type: Optional[PartyType] = None
    ) -> List[PartyNodeResponse]:
        """
        Get all parties for a case

        Args:
            case_id: Case ID
            party_type: Optional filter by party type

        Returns:
            List of party node responses
        """
        if party_type:
            parties = self.party_repo.get_by_type(case_id, party_type)
        else:
            parties = self.party_repo.get_all_for_case(case_id)

        return [self._to_response(p) for p in parties]

    def update_party(
        self,
        party_id: str,
        data: PartyNodeUpdate,
        user_id: str
    ) -> PartyNodeResponse:
        """
        Update a party node

        Args:
            party_id: Party node ID
            data: Update data
            user_id: User performing the action

        Returns:
            Updated party node response

        Raises:
            NotFoundError: Party not found
        """
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise NotFoundError(f"당사자를 찾을 수 없습니다: {party_id}")

        position_x = int(data.position.x) if data.position else None
        position_y = int(data.position.y) if data.position else None

        updated = self.party_repo.update(
            party_id=party_id,
            name=data.name,
            alias=data.alias,
            birth_year=data.birth_year,
            occupation=data.occupation,
            position_x=position_x,
            position_y=position_y,
            extra_data=data.extra_data
        )

        self.db.commit()
        logger.info(f"Party updated: {party_id} by user {user_id}")

        return self._to_response(updated)

    def delete_party(self, party_id: str, user_id: str) -> bool:
        """
        Delete a party node

        Args:
            party_id: Party node ID
            user_id: User performing the action

        Returns:
            True if deleted

        Raises:
            NotFoundError: Party not found
        """
        party = self.party_repo.get_by_id(party_id)
        if not party:
            raise NotFoundError(f"당사자를 찾을 수 없습니다: {party_id}")

        result = self.party_repo.delete(party_id)
        self.db.commit()
        logger.info(f"Party deleted: {party_id} by user {user_id}")

        return result

    def get_graph(self, case_id: str) -> dict:
        """
        Get the complete party relationship graph for a case

        Args:
            case_id: Case ID

        Returns:
            Dict with nodes (parties) and relationships arrays
        """
        party_nodes = self.party_repo.get_all_for_case(case_id)
        relationships = self.relationship_repo.get_by_case_id(case_id)

        return {
            "nodes": [self._to_response(p) for p in party_nodes],
            "relationships": [self._rel_to_response(r) for r in relationships]
        }

    def _to_response(self, party: PartyNode) -> PartyNodeResponse:
        """Convert PartyNode model to response schema"""
        return PartyNodeResponse(
            id=party.id,
            case_id=party.case_id,
            type=party.type,
            name=party.name,
            alias=party.alias,
            birth_year=party.birth_year,
            occupation=party.occupation,
            position=Position(x=party.position_x, y=party.position_y),
            extra_data=party.extra_data,
            created_at=party.created_at,
            updated_at=party.updated_at
        )

    def _rel_to_response(self, relationship) -> dict:
        """Convert PartyRelationship model to response dict"""
        return {
            "id": relationship.id,
            "case_id": relationship.case_id,
            "source_party_id": relationship.source_party_id,
            "target_party_id": relationship.target_party_id,
            "type": relationship.type.value if hasattr(relationship.type, 'value') else relationship.type,
            "start_date": relationship.start_date.isoformat() if relationship.start_date else None,
            "end_date": relationship.end_date.isoformat() if relationship.end_date else None,
            "notes": relationship.notes,
            "created_at": relationship.created_at.isoformat() if relationship.created_at else None,
            "updated_at": relationship.updated_at.isoformat() if relationship.updated_at else None
        }
