"""
Evidence Link Repository - Data access layer for evidence-party links
007-lawyer-portal-v1: US4 (Evidence-Party Linking)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid

from app.db.models import EvidencePartyLink, LinkType


class EvidenceLinkRepository:
    """Repository for EvidencePartyLink CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, link_id: str) -> Optional[EvidencePartyLink]:
        """Get evidence link by ID"""
        return self.db.query(EvidencePartyLink).filter(
            EvidencePartyLink.id == link_id
        ).first()

    def get_by_case_id(
        self,
        case_id: str,
        evidence_id: Optional[str] = None,
        party_id: Optional[str] = None,
        relationship_id: Optional[str] = None
    ) -> List[EvidencePartyLink]:
        """
        Get all evidence links for a case with optional filters.

        Args:
            case_id: Case UUID
            evidence_id: Optional filter by evidence
            party_id: Optional filter by party
            relationship_id: Optional filter by relationship

        Returns:
            List of EvidencePartyLink objects
        """
        query = self.db.query(EvidencePartyLink).filter(
            EvidencePartyLink.case_id == case_id
        )

        if evidence_id:
            query = query.filter(EvidencePartyLink.evidence_id == evidence_id)

        if party_id:
            query = query.filter(EvidencePartyLink.party_id == party_id)

        if relationship_id:
            query = query.filter(EvidencePartyLink.relationship_id == relationship_id)

        return query.order_by(EvidencePartyLink.created_at.asc()).all()

    def get_by_evidence_id(self, case_id: str, evidence_id: str) -> List[EvidencePartyLink]:
        """Get all links for a specific evidence item"""
        return self.db.query(EvidencePartyLink).filter(
            and_(
                EvidencePartyLink.case_id == case_id,
                EvidencePartyLink.evidence_id == evidence_id
            )
        ).order_by(EvidencePartyLink.created_at.asc()).all()

    def get_by_party_id(self, case_id: str, party_id: str) -> List[EvidencePartyLink]:
        """Get all links for a specific party"""
        return self.db.query(EvidencePartyLink).filter(
            and_(
                EvidencePartyLink.case_id == case_id,
                EvidencePartyLink.party_id == party_id
            )
        ).order_by(EvidencePartyLink.created_at.asc()).all()

    def check_duplicate(
        self,
        case_id: str,
        evidence_id: str,
        party_id: Optional[str] = None,
        relationship_id: Optional[str] = None,
        link_type: Optional[LinkType] = None
    ) -> bool:
        """
        Check if a duplicate link exists.

        Returns True if a link with the same evidence_id and target
        (party or relationship) already exists.
        """
        query = self.db.query(EvidencePartyLink).filter(
            and_(
                EvidencePartyLink.case_id == case_id,
                EvidencePartyLink.evidence_id == evidence_id
            )
        )

        if party_id:
            query = query.filter(EvidencePartyLink.party_id == party_id)

        if relationship_id:
            query = query.filter(EvidencePartyLink.relationship_id == relationship_id)

        if link_type:
            query = query.filter(EvidencePartyLink.link_type == link_type)

        return query.first() is not None

    def create(
        self,
        case_id: str,
        evidence_id: str,
        party_id: Optional[str] = None,
        relationship_id: Optional[str] = None,
        link_type: LinkType = LinkType.MENTIONS
    ) -> EvidencePartyLink:
        """
        Create a new evidence-party link.

        Args:
            case_id: Case UUID
            evidence_id: Evidence ID (from DynamoDB)
            party_id: Optional party UUID
            relationship_id: Optional relationship UUID
            link_type: Type of link

        Returns:
            Created EvidencePartyLink object
        """
        now = datetime.utcnow()

        link = EvidencePartyLink(
            id=f"link_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            evidence_id=evidence_id,
            party_id=party_id,
            relationship_id=relationship_id,
            link_type=link_type,
            created_at=now
        )

        self.db.add(link)
        self.db.flush()

        return link

    def delete(self, link_id: str) -> bool:
        """
        Delete an evidence link.

        Args:
            link_id: Link ID to delete

        Returns:
            True if deleted successfully
        """
        link = self.get_by_id(link_id)
        if not link:
            return False

        self.db.delete(link)
        self.db.flush()

        return True

    def delete_by_evidence_id(self, case_id: str, evidence_id: str) -> int:
        """
        Delete all links for a specific evidence item.

        Returns number of deleted links.
        """
        count = self.db.query(EvidencePartyLink).filter(
            and_(
                EvidencePartyLink.case_id == case_id,
                EvidencePartyLink.evidence_id == evidence_id
            )
        ).delete()

        self.db.flush()
        return count

    def delete_by_party_id(self, case_id: str, party_id: str) -> int:
        """
        Delete all links for a specific party.

        Returns number of deleted links.
        """
        count = self.db.query(EvidencePartyLink).filter(
            and_(
                EvidencePartyLink.case_id == case_id,
                EvidencePartyLink.party_id == party_id
            )
        ).delete()

        self.db.flush()
        return count

    def count_by_case_id(self, case_id: str) -> int:
        """Count evidence links for a case"""
        return self.db.query(EvidencePartyLink).filter(
            EvidencePartyLink.case_id == case_id
        ).count()
