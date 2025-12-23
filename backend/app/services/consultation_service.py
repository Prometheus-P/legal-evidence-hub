"""
Consultation Service - Business logic for consultation management
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models import ConsultationType
from app.db.schemas.consultation import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationOut,
    ConsultationListResponse,
    LinkEvidenceRequest,
    LinkEvidenceResponse,
)
from app.repositories.consultation_repository import ConsultationRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.user_repository import UserRepository
from app.middleware import NotFoundError, PermissionError
from app.services.audit_service import AuditService
from app.utils.qdrant import (
    index_consultation_document,
    delete_consultation_document,
)
import logging

logger = logging.getLogger(__name__)


class ConsultationService:
    """
    Service for consultation management business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = ConsultationRepository(db)
        self.case_repo = CaseRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    def _check_case_access(self, case_id: str, user_id: str) -> None:
        """Check if user has access to the case"""
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError(f"Case {case_id} not found")

        if not self.case_repo.is_user_member_of_case(user_id, case_id):
            raise PermissionError("You don't have access to this case")

    def _consultation_to_out(self, consultation) -> ConsultationOut:
        """Convert Consultation model to ConsultationOut schema"""
        # Get creator name
        creator_name = None
        if consultation.creator:
            creator_name = consultation.creator.name

        # Get participant names
        participants = [p.name for p in consultation.participants]

        # Get linked evidence IDs
        linked_evidence = [link.evidence_id for link in consultation.evidence_links]

        return ConsultationOut(
            id=consultation.id,
            case_id=consultation.case_id,
            date=consultation.date,
            time=consultation.time,
            type=consultation.type.value if isinstance(consultation.type, ConsultationType) else consultation.type,
            participants=participants,
            summary=consultation.summary,
            notes=consultation.notes,
            created_by=consultation.created_by,
            created_by_name=creator_name,
            created_at=consultation.created_at,
            updated_at=consultation.updated_at,
            linked_evidence=linked_evidence,
        )

    def create_consultation(
        self,
        case_id: str,
        data: ConsultationCreate,
        user_id: str,
    ) -> ConsultationOut:
        """
        Create a new consultation

        Args:
            case_id: Case ID
            data: Consultation creation data
            user_id: ID of user creating the consultation

        Returns:
            Created consultation data
        """
        self._check_case_access(case_id, user_id)

        # Map type string to enum
        consultation_type = ConsultationType(data.type)

        consultation = self.repo.create(
            case_id=case_id,
            date=data.date,
            time=data.time,
            type=consultation_type,
            summary=data.summary,
            notes=data.notes,
            created_by=user_id,
            participants=data.participants,
        )

        # Audit log
        self.audit_service.log(
            user_id=user_id,
            action="CONSULTATION_CREATE",
            resource_type="consultation",
            resource_id=consultation.id,
            details={"case_id": case_id, "type": data.type},
        )

        self.db.commit()
        self.db.refresh(consultation)

        # Index in Qdrant for RAG search (Issue #403)
        try:
            self._index_consultation_in_qdrant(consultation)
        except Exception as e:
            logger.warning(f"Failed to index consultation in Qdrant: {e}")

        return self._consultation_to_out(consultation)

    def get_consultation(
        self,
        consultation_id: str,
        user_id: str,
    ) -> ConsultationOut:
        """
        Get a consultation by ID

        Args:
            consultation_id: Consultation ID
            user_id: ID of user requesting

        Returns:
            Consultation data
        """
        consultation = self.repo.get_by_id(consultation_id)
        if not consultation:
            raise NotFoundError(f"Consultation {consultation_id} not found")

        self._check_case_access(consultation.case_id, user_id)

        return self._consultation_to_out(consultation)

    def list_consultations(
        self,
        case_id: str,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> ConsultationListResponse:
        """
        List all consultations for a case

        Args:
            case_id: Case ID
            user_id: ID of user requesting
            limit: Max results
            offset: Pagination offset

        Returns:
            List of consultations with total count
        """
        self._check_case_access(case_id, user_id)

        consultations = self.repo.get_by_case_id(case_id, limit=limit, offset=offset)
        total = self.repo.count_by_case_id(case_id)

        return ConsultationListResponse(
            consultations=[self._consultation_to_out(c) for c in consultations],
            total=total,
        )

    def update_consultation(
        self,
        consultation_id: str,
        data: ConsultationUpdate,
        user_id: str,
    ) -> ConsultationOut:
        """
        Update a consultation

        Args:
            consultation_id: Consultation ID
            data: Update data
            user_id: ID of user updating

        Returns:
            Updated consultation data
        """
        consultation = self.repo.get_by_id(consultation_id)
        if not consultation:
            raise NotFoundError(f"Consultation {consultation_id} not found")

        self._check_case_access(consultation.case_id, user_id)

        # Map type string to enum if provided
        consultation_type = None
        if data.type is not None:
            consultation_type = ConsultationType(data.type)

        updated = self.repo.update(
            consultation_id=consultation_id,
            date=data.date,
            time=data.time,
            type=consultation_type,
            summary=data.summary,
            notes=data.notes,
            participants=data.participants,
        )

        # Audit log
        self.audit_service.log(
            user_id=user_id,
            action="CONSULTATION_UPDATE",
            resource_type="consultation",
            resource_id=consultation_id,
            details={"case_id": consultation.case_id},
        )

        self.db.commit()
        self.db.refresh(updated)

        # Re-index in Qdrant for RAG search (Issue #403)
        try:
            self._index_consultation_in_qdrant(updated)
        except Exception as e:
            logger.warning(f"Failed to re-index consultation in Qdrant: {e}")

        return self._consultation_to_out(updated)

    def delete_consultation(
        self,
        consultation_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a consultation

        Args:
            consultation_id: Consultation ID
            user_id: ID of user deleting

        Returns:
            True if deleted
        """
        consultation = self.repo.get_by_id(consultation_id)
        if not consultation:
            raise NotFoundError(f"Consultation {consultation_id} not found")

        self._check_case_access(consultation.case_id, user_id)

        case_id = consultation.case_id
        success = self.repo.delete(consultation_id)

        if success:
            # Audit log
            self.audit_service.log(
                user_id=user_id,
                action="CONSULTATION_DELETE",
                resource_type="consultation",
                resource_id=consultation_id,
                details={"case_id": case_id},
            )
            self.db.commit()

            # Remove from Qdrant (Issue #403)
            try:
                delete_consultation_document(case_id, consultation_id)
            except Exception as e:
                logger.warning(f"Failed to delete consultation from Qdrant: {e}")

        return success

    def _index_consultation_in_qdrant(self, consultation) -> None:
        """
        Index consultation in Qdrant for RAG search (Issue #403)

        Args:
            consultation: Consultation model instance
        """
        # Build dict for Qdrant indexing
        consultation_dict = {
            "id": consultation.id,
            "summary": consultation.summary,
            "notes": consultation.notes,
            "date": consultation.date,
            "type": consultation.type.value if hasattr(consultation.type, 'value') else str(consultation.type),
            "participants": [p.name for p in consultation.participants],
        }

        index_consultation_document(consultation.case_id, consultation_dict)
        logger.info(f"Indexed consultation {consultation.id} in Qdrant")

    # ============================================
    # Evidence Link Operations
    # ============================================
    def link_evidence(
        self,
        consultation_id: str,
        request: LinkEvidenceRequest,
        user_id: str,
    ) -> LinkEvidenceResponse:
        """
        Link evidence to a consultation

        Args:
            consultation_id: Consultation ID
            request: Link evidence request
            user_id: ID of user linking

        Returns:
            Link evidence response
        """
        consultation = self.repo.get_by_id(consultation_id)
        if not consultation:
            raise NotFoundError(f"Consultation {consultation_id} not found")

        self._check_case_access(consultation.case_id, user_id)

        links = self.repo.link_evidence(
            consultation_id=consultation_id,
            evidence_ids=request.evidence_ids,
            linked_by=user_id,
        )

        # Audit log
        self.audit_service.log(
            user_id=user_id,
            action="CONSULTATION_EVIDENCE_LINK",
            resource_type="consultation",
            resource_id=consultation_id,
            details={
                "case_id": consultation.case_id,
                "evidence_ids": request.evidence_ids,
            },
        )

        self.db.commit()

        return LinkEvidenceResponse(
            consultation_id=consultation_id,
            linked_evidence_ids=[link.evidence_id for link in links],
            linked_at=datetime.now(timezone.utc),
        )

    def unlink_evidence(
        self,
        consultation_id: str,
        evidence_id: str,
        user_id: str,
    ) -> bool:
        """
        Unlink evidence from a consultation

        Args:
            consultation_id: Consultation ID
            evidence_id: Evidence ID to unlink
            user_id: ID of user unlinking

        Returns:
            True if unlinked
        """
        consultation = self.repo.get_by_id(consultation_id)
        if not consultation:
            raise NotFoundError(f"Consultation {consultation_id} not found")

        self._check_case_access(consultation.case_id, user_id)

        success = self.repo.unlink_evidence(consultation_id, evidence_id)

        if success:
            # Audit log
            self.audit_service.log(
                user_id=user_id,
                action="CONSULTATION_EVIDENCE_UNLINK",
                resource_type="consultation",
                resource_id=consultation_id,
                details={
                    "case_id": consultation.case_id,
                    "evidence_id": evidence_id,
                },
            )
            self.db.commit()

        return success
