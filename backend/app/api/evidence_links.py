"""
Evidence Links API Router - REST endpoints for evidence-party link management
007-lawyer-portal-v1: US4 (Evidence-Party Linking)
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.dependencies import (
    get_db,
    get_current_user_id,
    verify_case_read_access,
    verify_case_write_access
)
from app.db.schemas import (
    EvidenceLinkCreate,
    EvidenceLinkResponse,
    EvidenceLinksResponse
)
from app.services.evidence_link_service import EvidenceLinkService

router = APIRouter(
    prefix="/cases/{case_id}/evidence-links",
    tags=["evidence-links"]
)


@router.post(
    "",
    response_model=EvidenceLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an evidence-party link"
)
async def create_evidence_link(
    case_id: str,
    data: EvidenceLinkCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new link between evidence and a party or relationship.

    At least one of party_id or relationship_id must be provided.

    Link types:
    - mentions: Evidence mentions the party/relationship
    - proves: Evidence proves something about the party/relationship
    - involves: Evidence involves the party/relationship
    - contradicts: Evidence contradicts claims about the party/relationship

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    return service.create_link(case_id, data, user_id)


@router.get(
    "",
    response_model=EvidenceLinksResponse,
    summary="Get all evidence links for a case"
)
async def get_evidence_links(
    case_id: str,
    evidence_id: Optional[str] = Query(None, description="Filter by evidence ID"),
    party_id: Optional[str] = Query(None, description="Filter by party ID"),
    relationship_id: Optional[str] = Query(None, description="Filter by relationship ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all evidence links for a case.

    Optional filters:
    - evidence_id: Filter by specific evidence
    - party_id: Filter by specific party
    - relationship_id: Filter by specific relationship

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    return service.get_links_for_case(
        case_id,
        evidence_id=evidence_id,
        party_id=party_id,
        relationship_id=relationship_id
    )


@router.get(
    "/{link_id}",
    response_model=EvidenceLinkResponse,
    summary="Get a specific evidence link"
)
async def get_evidence_link(
    case_id: str,
    link_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific evidence link by ID.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    return service.get_link(link_id)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an evidence link"
)
async def delete_evidence_link(
    case_id: str,
    link_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete an evidence link.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    service.delete_link(link_id, user_id)

    return None


# ============================================================
# Convenience endpoints for querying by evidence or party
# ============================================================

@router.get(
    "/by-evidence/{evidence_id}",
    response_model=EvidenceLinksResponse,
    summary="Get all links for a specific evidence"
)
async def get_links_for_evidence(
    case_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all links for a specific evidence item.

    This is a convenience endpoint equivalent to:
    GET /cases/{case_id}/evidence-links?evidence_id={evidence_id}

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    return service.get_links_for_evidence(case_id, evidence_id)


@router.get(
    "/by-party/{party_id}",
    response_model=EvidenceLinksResponse,
    summary="Get all links for a specific party"
)
async def get_links_for_party(
    case_id: str,
    party_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all links for a specific party.

    This is a convenience endpoint equivalent to:
    GET /cases/{case_id}/evidence-links?party_id={party_id}

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = EvidenceLinkService(db)
    return service.get_links_for_party(case_id, party_id)
