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
    Position,
    AutoExtractedPartyRequest,
    AutoExtractedPartyResponse
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
            # 012-precedent-integration: T036-T038 자동 추출 필드
            is_auto_extracted=party.is_auto_extracted,
            extraction_confidence=party.extraction_confidence,
            source_evidence_id=party.source_evidence_id,
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

    # ============================================
    # 012-precedent-integration: T040-T041 자동 추출 메서드
    # ============================================
    def create_auto_extracted_party(
        self,
        case_id: str,
        data: AutoExtractedPartyRequest,
        user_id: str
    ) -> AutoExtractedPartyResponse:
        """
        Create or find existing party from AI Worker extraction (T040-T041)

        Args:
            case_id: Case ID
            data: Auto-extracted party data
            user_id: User performing the action

        Returns:
            AutoExtractedPartyResponse with duplicate detection info
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # T041: Check for duplicate (similar name)
        existing_parties = self.party_repo.get_all_for_case(case_id)
        matched_party = self._detect_duplicate(data.name, existing_parties)

        if matched_party:
            logger.info(f"Duplicate party detected: {data.name} matches {matched_party.name} ({matched_party.id})")
            return AutoExtractedPartyResponse(
                id=matched_party.id,
                name=matched_party.name,
                is_duplicate=True,
                matched_party_id=matched_party.id
            )

        # Create new auto-extracted party
        party = PartyNode(
            case_id=case_id,
            type=data.type,
            name=data.name,
            alias=data.alias,
            birth_year=data.birth_year,
            occupation=data.occupation,
            position_x=0,
            position_y=0,
            is_auto_extracted=True,
            extraction_confidence=data.extraction_confidence,
            source_evidence_id=data.source_evidence_id
        )

        self.db.add(party)
        self.db.commit()
        self.db.refresh(party)

        logger.info(f"Auto-extracted party created: {party.id} ({party.name}) for case {case_id}")

        return AutoExtractedPartyResponse(
            id=party.id,
            name=party.name,
            is_duplicate=False,
            matched_party_id=None
        )

    def _detect_duplicate(self, new_name: str, existing_parties: list, threshold: float = 0.8) -> Optional[PartyNode]:
        """
        Detect duplicate party by name similarity (T041)

        Uses simple character-based similarity for Korean names.
        Threshold 0.8 = 80% character overlap required.
        """
        import difflib

        new_name_normalized = new_name.strip().lower()

        for existing in existing_parties:
            existing_name_normalized = existing.name.strip().lower()

            # Calculate similarity ratio
            similarity = difflib.SequenceMatcher(
                None,
                new_name_normalized,
                existing_name_normalized
            ).ratio()

            if similarity >= threshold:
                return existing

        return None
