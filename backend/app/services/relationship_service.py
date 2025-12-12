"""
Relationship Service - Business logic for party relationships
007-lawyer-portal-v1: US1 (Party Relationship Graph)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import PartyRelationship, RelationshipType
from app.db.schemas import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    PartyGraphResponse,
    PartyNodeResponse,
    Position,
    AutoExtractedRelationshipRequest,
    AutoExtractedRelationshipResponse
)
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.party_repository import PartyRepository
from app.repositories.case_repository import CaseRepository
from app.middleware import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class RelationshipService:
    """
    Service for party relationship business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.relationship_repo = RelationshipRepository(db)
        self.party_repo = PartyRepository(db)
        self.case_repo = CaseRepository(db)

    def create_relationship(
        self,
        case_id: str,
        data: RelationshipCreate,
        user_id: str
    ) -> RelationshipResponse:
        """
        Create a new relationship between parties

        Args:
            case_id: Case ID
            data: Relationship creation data
            user_id: User performing the action

        Returns:
            Created relationship response

        Raises:
            NotFoundError: Case or party not found
            ValidationError: Self-reference or duplicate relationship
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # Verify source party exists and belongs to case
        source_party = self.party_repo.get_by_id(data.source_party_id)
        if not source_party:
            raise NotFoundError(f"출발 당사자를 찾을 수 없습니다: {data.source_party_id}")
        if source_party.case_id != case_id:
            raise ValidationError("출발 당사자가 이 케이스에 속하지 않습니다")

        # Verify target party exists and belongs to case
        target_party = self.party_repo.get_by_id(data.target_party_id)
        if not target_party:
            raise NotFoundError(f"도착 당사자를 찾을 수 없습니다: {data.target_party_id}")
        if target_party.case_id != case_id:
            raise ValidationError("도착 당사자가 이 케이스에 속하지 않습니다")

        # Validate no self-reference
        if data.source_party_id == data.target_party_id:
            raise ValidationError("출발 당사자와 도착 당사자가 동일할 수 없습니다")

        # Check for duplicate relationship
        if self.relationship_repo.check_duplicate(
            case_id=case_id,
            source_party_id=data.source_party_id,
            target_party_id=data.target_party_id,
            relationship_type=data.type
        ):
            raise ValidationError("동일한 관계가 이미 존재합니다")

        # Create relationship
        # Convert datetime to date if provided
        start_date = data.start_date.date() if data.start_date else None
        end_date = data.end_date.date() if data.end_date else None

        relationship = self.relationship_repo.create(
            case_id=case_id,
            source_party_id=data.source_party_id,
            target_party_id=data.target_party_id,
            type=data.type,
            start_date=start_date,
            end_date=end_date,
            notes=data.notes
        )

        logger.info(f"Relationship created: {relationship.id} for case {case_id} by user {user_id}")

        return self._to_response(relationship)

    def get_relationship(self, relationship_id: str) -> RelationshipResponse:
        """
        Get a relationship by ID

        Args:
            relationship_id: Relationship ID

        Returns:
            Relationship response

        Raises:
            NotFoundError: Relationship not found
        """
        relationship = self.relationship_repo.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"관계를 찾을 수 없습니다: {relationship_id}")

        return self._to_response(relationship)

    def get_relationships_for_case(
        self,
        case_id: str,
        relationship_type: Optional[RelationshipType] = None,
        party_id: Optional[str] = None
    ) -> List[RelationshipResponse]:
        """
        Get all relationships for a case

        Args:
            case_id: Case ID
            relationship_type: Optional filter by relationship type
            party_id: Optional filter by party involvement

        Returns:
            List of relationship responses
        """
        relationships = self.relationship_repo.get_by_case_id(
            case_id=case_id,
            relationship_type=relationship_type,
            party_id=party_id
        )

        return [self._to_response(r) for r in relationships]

    def update_relationship(
        self,
        relationship_id: str,
        data: RelationshipUpdate,
        user_id: str
    ) -> RelationshipResponse:
        """
        Update a relationship

        Args:
            relationship_id: Relationship ID
            data: Update data
            user_id: User performing the action

        Returns:
            Updated relationship response

        Raises:
            NotFoundError: Relationship not found
        """
        relationship = self.relationship_repo.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"관계를 찾을 수 없습니다: {relationship_id}")

        # Convert datetime to date if provided
        start_date = data.start_date.date() if data.start_date else None
        end_date = data.end_date.date() if data.end_date else None

        updated = self.relationship_repo.update(
            relationship=relationship,
            type=data.type,
            start_date=start_date,
            end_date=end_date,
            notes=data.notes
        )

        logger.info(f"Relationship updated: {relationship_id} by user {user_id}")

        return self._to_response(updated)

    def delete_relationship(self, relationship_id: str, user_id: str) -> bool:
        """
        Delete a relationship

        Args:
            relationship_id: Relationship ID
            user_id: User performing the action

        Returns:
            True if deleted

        Raises:
            NotFoundError: Relationship not found
        """
        relationship = self.relationship_repo.get_by_id(relationship_id)
        if not relationship:
            raise NotFoundError(f"관계를 찾을 수 없습니다: {relationship_id}")

        result = self.relationship_repo.delete(relationship)
        logger.info(f"Relationship deleted: {relationship_id} by user {user_id}")

        return result

    def get_party_graph(self, case_id: str) -> PartyGraphResponse:
        """
        Get complete party graph for a case (nodes + relationships)

        Args:
            case_id: Case ID

        Returns:
            PartyGraphResponse with nodes and relationships

        Raises:
            NotFoundError: Case not found
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # Get all parties for case
        parties = self.party_repo.get_all_for_case(case_id)
        nodes = [self._party_to_response(p) for p in parties]

        # Get all relationships for case
        relationships = self.relationship_repo.get_by_case_id(case_id)
        edges = [self._to_response(r) for r in relationships]

        return PartyGraphResponse(nodes=nodes, relationships=edges)

    def _to_response(self, relationship: PartyRelationship) -> RelationshipResponse:
        """Convert PartyRelationship model to response schema"""
        return RelationshipResponse(
            id=relationship.id,
            case_id=relationship.case_id,
            source_party_id=relationship.source_party_id,
            target_party_id=relationship.target_party_id,
            type=relationship.type,
            start_date=relationship.start_date,
            end_date=relationship.end_date,
            notes=relationship.notes,
            # 012-precedent-integration: T039 자동 추출 필드
            is_auto_extracted=relationship.is_auto_extracted,
            extraction_confidence=relationship.extraction_confidence,
            evidence_text=relationship.evidence_text,
            created_at=relationship.created_at,
            updated_at=relationship.updated_at
        )

    def _party_to_response(self, party) -> PartyNodeResponse:
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

    # ============================================
    # 012-precedent-integration: T042-T043 자동 추출 메서드
    # ============================================
    def create_auto_extracted_relationship(
        self,
        case_id: str,
        data: AutoExtractedRelationshipRequest,
        user_id: str
    ) -> AutoExtractedRelationshipResponse:
        """
        Create relationship from AI Worker extraction (T042-T043)

        Args:
            case_id: Case ID
            data: Auto-extracted relationship data
            user_id: User performing the action

        Returns:
            AutoExtractedRelationshipResponse
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # T043: Confidence threshold check (already enforced in schema, but double-check)
        if data.extraction_confidence < 0.7:
            raise ValidationError("추출 신뢰도는 0.7 이상이어야 합니다")

        # Validate both parties exist
        source_party = self.party_repo.get_by_id(data.source_party_id)
        if not source_party:
            raise NotFoundError(f"출발 인물을 찾을 수 없습니다: {data.source_party_id}")

        target_party = self.party_repo.get_by_id(data.target_party_id)
        if not target_party:
            raise NotFoundError(f"도착 인물을 찾을 수 없습니다: {data.target_party_id}")

        # Validate parties belong to the case
        if source_party.case_id != case_id or target_party.case_id != case_id:
            raise ValidationError("인물이 해당 케이스에 속하지 않습니다")

        # Create auto-extracted relationship
        relationship = PartyRelationship(
            case_id=case_id,
            source_party_id=data.source_party_id,
            target_party_id=data.target_party_id,
            type=data.type,
            is_auto_extracted=True,
            extraction_confidence=data.extraction_confidence,
            evidence_text=data.evidence_text
        )

        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)

        logger.info(
            f"Auto-extracted relationship created: {relationship.id} "
            f"({source_party.name} -> {target_party.name}, type={data.type.value}) "
            f"for case {case_id}"
        )

        return AutoExtractedRelationshipResponse(
            id=relationship.id,
            created=True
        )
