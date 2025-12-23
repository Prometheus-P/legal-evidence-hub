"""
Consultation API Router - REST endpoints for consultation management
Issue #399: 상담내역 API
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user_id,
    verify_case_read_access,
    verify_case_write_access,
)
from app.db.schemas.consultation import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationOut,
    ConsultationListResponse,
    LinkEvidenceRequest,
    LinkEvidenceResponse,
)
from app.services.consultation_service import ConsultationService

router = APIRouter(
    prefix="/cases/{case_id}/consultations",
    tags=["consultations"]
)


@router.post(
    "",
    response_model=ConsultationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new consultation"
)
async def create_consultation(
    case_id: str,
    data: ConsultationCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new consultation record for a case.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = ConsultationService(db)
    return service.create_consultation(case_id, data, user_id)


@router.get(
    "",
    response_model=ConsultationListResponse,
    summary="List consultations for a case"
)
async def list_consultations(
    case_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all consultations for a case, ordered by date descending.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = ConsultationService(db)
    return service.list_consultations(case_id, user_id, limit=limit, offset=offset)


@router.get(
    "/{consultation_id}",
    response_model=ConsultationOut,
    summary="Get a specific consultation"
)
async def get_consultation(
    case_id: str,
    consultation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific consultation by ID.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = ConsultationService(db)
    return service.get_consultation(consultation_id, user_id)


@router.put(
    "/{consultation_id}",
    response_model=ConsultationOut,
    summary="Update a consultation"
)
async def update_consultation(
    case_id: str,
    consultation_id: str,
    data: ConsultationUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a consultation record.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = ConsultationService(db)
    return service.update_consultation(consultation_id, data, user_id)


@router.delete(
    "/{consultation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a consultation"
)
async def delete_consultation(
    case_id: str,
    consultation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a consultation record.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = ConsultationService(db)
    service.delete_consultation(consultation_id, user_id)


# ============================================
# Evidence Link Endpoints
# ============================================
@router.post(
    "/{consultation_id}/evidence",
    response_model=LinkEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Link evidence to a consultation"
)
async def link_evidence(
    case_id: str,
    consultation_id: str,
    data: LinkEvidenceRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Link one or more evidence items to a consultation.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = ConsultationService(db)
    return service.link_evidence(consultation_id, data, user_id)


@router.delete(
    "/{consultation_id}/evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlink evidence from a consultation"
)
async def unlink_evidence(
    case_id: str,
    consultation_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Unlink an evidence item from a consultation.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = ConsultationService(db)
    service.unlink_evidence(consultation_id, evidence_id, user_id)
