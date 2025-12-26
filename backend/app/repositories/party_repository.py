"""
Party Repository - Data access layer for PartyNode model
Implements Repository pattern per BACKEND_SERVICE_REPOSITORY_GUIDE.md
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.models import PartyNode, PartyRelationship, PartyType, RelationshipType
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

    # ============================================
    # 017-party-graph-improvement: Extended methods for party extraction
    # ============================================

    def get_parties_by_case(self, case_id: str) -> List[PartyNode]:
        """Alias for get_all_for_case - used by extraction service"""
        return self.get_all_for_case(case_id)

    def create_party(
        self,
        case_id: str,
        party_type: PartyType,
        name: str,
        alias: Optional[str] = None,
        birth_year: Optional[int] = None,
        occupation: Optional[str] = None,
        position_x: int = 0,
        position_y: int = 0,
        is_auto_extracted: bool = False,
        extraction_confidence: Optional[float] = None,
        source_evidence_id: Optional[str] = None,
        extra_data: Optional[dict] = None
    ) -> PartyNode:
        """
        Create a new party node with auto-extraction fields
        """
        party = PartyNode(
            id=f"party_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            type=party_type,
            name=name,
            alias=alias,
            birth_year=birth_year,
            occupation=occupation,
            position_x=position_x,
            position_y=position_y,
            is_auto_extracted=is_auto_extracted,
            extraction_confidence=extraction_confidence,
            source_evidence_id=source_evidence_id,
            extra_data=extra_data or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        self.session.add(party)
        self.session.flush()

        return party

    def get_relationship_by_parties(
        self,
        case_id: str,
        source_party_id: str,
        target_party_id: str
    ) -> Optional[PartyRelationship]:
        """
        Get relationship between two parties (in either direction)
        """
        return (
            self.session.query(PartyRelationship)
            .filter(
                PartyRelationship.case_id == case_id,
                or_(
                    (PartyRelationship.source_party_id == source_party_id) &
                    (PartyRelationship.target_party_id == target_party_id),
                    (PartyRelationship.source_party_id == target_party_id) &
                    (PartyRelationship.target_party_id == source_party_id)
                )
            )
            .first()
        )

    def create_relationship(
        self,
        case_id: str,
        source_party_id: str,
        target_party_id: str,
        relationship_type: RelationshipType,
        is_auto_extracted: bool = False,
        extraction_confidence: Optional[float] = None,
        evidence_text: Optional[str] = None,
        notes: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PartyRelationship:
        """
        Create a new relationship between parties
        """
        relationship = PartyRelationship(
            id=f"rel_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            source_party_id=source_party_id,
            target_party_id=target_party_id,
            type=relationship_type,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            is_auto_extracted=is_auto_extracted,
            extraction_confidence=extraction_confidence,
            evidence_text=evidence_text,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        self.session.add(relationship)
        self.session.flush()

        return relationship

    # ============================================
    # 019-party-extraction-prompt: 자동추출 인물/관계 삭제
    # ============================================

    def delete_auto_extracted_parties(self, case_id: str) -> int:
        """
        Delete all auto-extracted parties for a case.
        Also deletes related relationships (CASCADE).

        Returns:
            Number of deleted parties
        """
        parties = (
            self.session.query(PartyNode)
            .filter(
                PartyNode.case_id == case_id,
                PartyNode.is_auto_extracted.is_(True)
            )
            .all()
        )

        count = len(parties)
        for party in parties:
            self.session.delete(party)

        self.session.flush()
        return count

    def delete_auto_extracted_relationships(self, case_id: str) -> int:
        """
        Delete all auto-extracted relationships for a case.

        Returns:
            Number of deleted relationships
        """
        # Get party IDs for this case
        party_ids = [
            p.id for p in
            self.session.query(PartyNode.id).filter(PartyNode.case_id == case_id).all()
        ]

        if not party_ids:
            return 0

        relationships = (
            self.session.query(PartyRelationship)
            .filter(
                PartyRelationship.source_party_id.in_(party_ids),
                PartyRelationship.is_auto_extracted.is_(True)
            )
            .all()
        )

        count = len(relationships)
        for rel in relationships:
            self.session.delete(rel)

        self.session.flush()
        return count
