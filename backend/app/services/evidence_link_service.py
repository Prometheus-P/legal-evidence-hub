"""
Evidence Link Service - Business logic for evidence-party linking
007-lawyer-portal-v1: US4 (Evidence-Party Linking)
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.db.models import EvidencePartyLink
from app.db.schemas import (
    EvidenceLinkCreate,
    EvidenceLinkResponse,
    EvidenceLinksResponse
)
from app.repositories.evidence_link_repository import EvidenceLinkRepository
from app.repositories.party_repository import PartyRepository
from app.repositories.relationship_repository import RelationshipRepository
from app.repositories.case_repository import CaseRepository
from app.middleware import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class EvidenceLinkService:
    """
    Service for evidence-party link business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.link_repo = EvidenceLinkRepository(db)
        self.party_repo = PartyRepository(db)
        self.relationship_repo = RelationshipRepository(db)
        self.case_repo = CaseRepository(db)

    def create_link(
        self,
        case_id: str,
        data: EvidenceLinkCreate,
        user_id: str
    ) -> EvidenceLinkResponse:
        """
        Create a new evidence-party link

        Args:
            case_id: Case ID
            data: Link creation data
            user_id: User performing the action

        Returns:
            Created link response

        Raises:
            NotFoundError: Case, party, or relationship not found
            ValidationError: No target specified or duplicate link
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"케이스를 찾을 수 없습니다: {case_id}")

        # Validate at least one target is specified
        if not data.party_id and not data.relationship_id:
            raise ValidationError("party_id 또는 relationship_id 중 하나는 필수입니다")

        # Verify party exists if specified
        if data.party_id:
            party = self.party_repo.get_by_id(data.party_id)
            if not party:
                raise NotFoundError(f"당사자를 찾을 수 없습니다: {data.party_id}")
            if party.case_id != case_id:
                raise ValidationError("당사자가 이 케이스에 속하지 않습니다")

        # Verify relationship exists if specified
        if data.relationship_id:
            relationship = self.relationship_repo.get_by_id(data.relationship_id)
            if not relationship:
                raise NotFoundError(f"관계를 찾을 수 없습니다: {data.relationship_id}")
            if relationship.case_id != case_id:
                raise ValidationError("관계가 이 케이스에 속하지 않습니다")

        # Check for duplicate link
        if self.link_repo.check_duplicate(
            case_id=case_id,
            evidence_id=data.evidence_id,
            party_id=data.party_id,
            relationship_id=data.relationship_id,
            link_type=data.link_type
        ):
            raise ValidationError("동일한 링크가 이미 존재합니다")

        # Create link
        link = self.link_repo.create(
            case_id=case_id,
            evidence_id=data.evidence_id,
            party_id=data.party_id,
            relationship_id=data.relationship_id,
            link_type=data.link_type
        )

        self.db.commit()
        logger.info(f"Evidence link created: {link.id} for case {case_id} by user {user_id}")

        return self._to_response(link)

    def get_link(self, link_id: str) -> EvidenceLinkResponse:
        """
        Get an evidence link by ID

        Args:
            link_id: Link ID

        Returns:
            Link response

        Raises:
            NotFoundError: Link not found
        """
        link = self.link_repo.get_by_id(link_id)
        if not link:
            raise NotFoundError(f"링크를 찾을 수 없습니다: {link_id}")

        return self._to_response(link)

    def get_links_for_case(
        self,
        case_id: str,
        evidence_id: Optional[str] = None,
        party_id: Optional[str] = None,
        relationship_id: Optional[str] = None
    ) -> EvidenceLinksResponse:
        """
        Get all evidence links for a case

        Args:
            case_id: Case ID
            evidence_id: Optional filter by evidence
            party_id: Optional filter by party
            relationship_id: Optional filter by relationship

        Returns:
            List of link responses with total count
        """
        links = self.link_repo.get_by_case_id(
            case_id=case_id,
            evidence_id=evidence_id,
            party_id=party_id,
            relationship_id=relationship_id
        )

        return EvidenceLinksResponse(
            links=[self._to_response(link) for link in links],
            total=len(links)
        )

    def get_links_for_evidence(
        self,
        case_id: str,
        evidence_id: str
    ) -> EvidenceLinksResponse:
        """
        Get all links for a specific evidence item

        Args:
            case_id: Case ID
            evidence_id: Evidence ID

        Returns:
            List of link responses
        """
        links = self.link_repo.get_by_evidence_id(case_id, evidence_id)

        return EvidenceLinksResponse(
            links=[self._to_response(link) for link in links],
            total=len(links)
        )

    def get_links_for_party(
        self,
        case_id: str,
        party_id: str
    ) -> EvidenceLinksResponse:
        """
        Get all links for a specific party

        Args:
            case_id: Case ID
            party_id: Party ID

        Returns:
            List of link responses
        """
        links = self.link_repo.get_by_party_id(case_id, party_id)

        return EvidenceLinksResponse(
            links=[self._to_response(link) for link in links],
            total=len(links)
        )

    def delete_link(self, link_id: str, user_id: str) -> bool:
        """
        Delete an evidence link

        Args:
            link_id: Link ID
            user_id: User performing the action

        Returns:
            True if deleted

        Raises:
            NotFoundError: Link not found
        """
        link = self.link_repo.get_by_id(link_id)
        if not link:
            raise NotFoundError(f"링크를 찾을 수 없습니다: {link_id}")

        result = self.link_repo.delete(link_id)
        self.db.commit()
        logger.info(f"Evidence link deleted: {link_id} by user {user_id}")

        return result

    def _to_response(self, link: EvidencePartyLink) -> EvidenceLinkResponse:
        """Convert EvidencePartyLink model to response schema"""
        return EvidenceLinkResponse(
            id=link.id,
            case_id=link.case_id,
            evidence_id=link.evidence_id,
            party_id=link.party_id,
            relationship_id=link.relationship_id,
            link_type=link.link_type,
            created_at=link.created_at
        )
