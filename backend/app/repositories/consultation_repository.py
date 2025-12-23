"""
Consultation Repository - Data access layer for Consultation model
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.db.models import (
    Consultation,
    ConsultationParticipant,
    ConsultationEvidence,
    ConsultationType,
)


class ConsultationRepository:
    """
    Repository for Consultation database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        case_id: str,
        date: datetime,
        type: ConsultationType,
        summary: str,
        created_by: str,
        time: Optional[datetime] = None,
        notes: Optional[str] = None,
        participants: Optional[List[str]] = None,
    ) -> Consultation:
        """
        Create a new consultation

        Args:
            case_id: Case ID
            date: Consultation date
            type: Consultation type (phone, in_person, online)
            summary: Consultation summary
            created_by: User ID who created
            time: Consultation time (optional)
            notes: Additional notes (optional)
            participants: List of participant names (optional)

        Returns:
            Created Consultation instance
        """
        consultation = Consultation(
            id=f"consult_{uuid.uuid4().hex[:12]}",
            case_id=case_id,
            date=date,
            time=time,
            type=type,
            summary=summary,
            notes=notes,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.session.add(consultation)
        self.session.flush()

        # Add participants
        if participants:
            for name in participants:
                participant = ConsultationParticipant(
                    id=f"cpart_{uuid.uuid4().hex[:12]}",
                    consultation_id=consultation.id,
                    name=name.strip(),
                )
                self.session.add(participant)

        self.session.flush()
        return consultation

    def get_by_id(self, consultation_id: str) -> Optional[Consultation]:
        """
        Get consultation by ID with participants and evidence links

        Args:
            consultation_id: Consultation ID

        Returns:
            Consultation instance if found, None otherwise
        """
        return (
            self.session.query(Consultation)
            .options(
                joinedload(Consultation.participants),
                joinedload(Consultation.evidence_links),
                joinedload(Consultation.creator),
            )
            .filter(Consultation.id == consultation_id)
            .first()
        )

    def get_by_case_id(self, case_id: str, limit: int = 100, offset: int = 0) -> List[Consultation]:
        """
        Get all consultations for a case, ordered by date desc

        Args:
            case_id: Case ID
            limit: Max number of results
            offset: Offset for pagination

        Returns:
            List of Consultation instances
        """
        return (
            self.session.query(Consultation)
            .options(
                joinedload(Consultation.participants),
                joinedload(Consultation.evidence_links),
                joinedload(Consultation.creator),
            )
            .filter(Consultation.case_id == case_id)
            .order_by(Consultation.date.desc(), Consultation.time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_case_id(self, case_id: str) -> int:
        """
        Count consultations for a case

        Args:
            case_id: Case ID

        Returns:
            Count of consultations
        """
        return (
            self.session.query(Consultation)
            .filter(Consultation.case_id == case_id)
            .count()
        )

    def update(
        self,
        consultation_id: str,
        date: Optional[datetime] = None,
        time: Optional[datetime] = None,
        type: Optional[ConsultationType] = None,
        summary: Optional[str] = None,
        notes: Optional[str] = None,
        participants: Optional[List[str]] = None,
    ) -> Optional[Consultation]:
        """
        Update a consultation

        Args:
            consultation_id: Consultation ID
            date: New date (optional)
            time: New time (optional)
            type: New type (optional)
            summary: New summary (optional)
            notes: New notes (optional)
            participants: New participant names (optional, replaces existing)

        Returns:
            Updated Consultation instance if found, None otherwise
        """
        consultation = self.get_by_id(consultation_id)
        if not consultation:
            return None

        if date is not None:
            consultation.date = date
        if time is not None:
            consultation.time = time
        if type is not None:
            consultation.type = type
        if summary is not None:
            consultation.summary = summary
        if notes is not None:
            consultation.notes = notes

        consultation.updated_at = datetime.now(timezone.utc)

        # Update participants if provided
        if participants is not None:
            # Remove existing participants
            self.session.query(ConsultationParticipant).filter(
                ConsultationParticipant.consultation_id == consultation_id
            ).delete()

            # Add new participants
            for name in participants:
                participant = ConsultationParticipant(
                    id=f"cpart_{uuid.uuid4().hex[:12]}",
                    consultation_id=consultation_id,
                    name=name.strip(),
                )
                self.session.add(participant)

        self.session.flush()
        return consultation

    def delete(self, consultation_id: str) -> bool:
        """
        Delete a consultation (cascade deletes participants and evidence links)

        Args:
            consultation_id: Consultation ID

        Returns:
            True if deleted, False if not found
        """
        consultation = self.session.query(Consultation).filter(
            Consultation.id == consultation_id
        ).first()

        if not consultation:
            return False

        self.session.delete(consultation)
        self.session.flush()
        return True

    # ============================================
    # Evidence Link Operations
    # ============================================
    def link_evidence(
        self,
        consultation_id: str,
        evidence_ids: List[str],
        linked_by: str,
    ) -> List[ConsultationEvidence]:
        """
        Link evidence to a consultation

        Args:
            consultation_id: Consultation ID
            evidence_ids: List of evidence IDs to link
            linked_by: User ID who linked

        Returns:
            List of created ConsultationEvidence instances
        """
        links = []
        for evidence_id in evidence_ids:
            # Check if already linked
            existing = (
                self.session.query(ConsultationEvidence)
                .filter(
                    ConsultationEvidence.consultation_id == consultation_id,
                    ConsultationEvidence.evidence_id == evidence_id,
                )
                .first()
            )

            if not existing:
                link = ConsultationEvidence(
                    consultation_id=consultation_id,
                    evidence_id=evidence_id,
                    linked_at=datetime.now(timezone.utc),
                    linked_by=linked_by,
                )
                self.session.add(link)
                links.append(link)

        self.session.flush()
        return links

    def unlink_evidence(self, consultation_id: str, evidence_id: str) -> bool:
        """
        Unlink evidence from a consultation

        Args:
            consultation_id: Consultation ID
            evidence_id: Evidence ID to unlink

        Returns:
            True if unlinked, False if not found
        """
        result = (
            self.session.query(ConsultationEvidence)
            .filter(
                ConsultationEvidence.consultation_id == consultation_id,
                ConsultationEvidence.evidence_id == evidence_id,
            )
            .delete()
        )
        self.session.flush()
        return result > 0

    def get_linked_evidence_ids(self, consultation_id: str) -> List[str]:
        """
        Get all evidence IDs linked to a consultation

        Args:
            consultation_id: Consultation ID

        Returns:
            List of evidence IDs
        """
        links = (
            self.session.query(ConsultationEvidence.evidence_id)
            .filter(ConsultationEvidence.consultation_id == consultation_id)
            .all()
        )
        return [link.evidence_id for link in links]
