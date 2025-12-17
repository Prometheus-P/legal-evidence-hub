"""
Party API Router - REST endpoints for party node management
007-lawyer-portal-v1: US1 (Party Relationship Graph)
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
from app.db.models import PartyType
from app.db.schemas import (
    PartyNodeCreate,
    PartyNodeUpdate,
    PartyNodeResponse,
    AutoExtractedPartyRequest,
    AutoExtractedPartyResponse
)
from app.services.party_service import PartyService

router = APIRouter(
    prefix="/cases/{case_id}/parties",
    tags=["parties"]
)


@router.post(
    "",
    response_model=PartyNodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new party node"
)
async def create_party(
    case_id: str,
    data: PartyNodeCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new party node for a case.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = PartyService(db)
    return service.create_party(case_id, data, user_id)


@router.get(
    "",
    response_model=dict,
    summary="Get all parties for a case"
)
async def get_parties(
    case_id: str,
    type: Optional[PartyType] = Query(None, description="Filter by party type"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all party nodes for a case.

    Optionally filter by party type.
    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = PartyService(db)
    parties = service.get_parties_for_case(case_id, type)

    return {
        "items": parties,
        "total": len(parties)
    }


@router.get(
    "/{party_id}",
    response_model=PartyNodeResponse,
    summary="Get a specific party node"
)
async def get_party(
    case_id: str,
    party_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific party node by ID.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = PartyService(db)
    return service.get_party(party_id)


@router.patch(
    "/{party_id}",
    response_model=PartyNodeResponse,
    summary="Update a party node"
)
async def update_party(
    case_id: str,
    party_id: str,
    data: PartyNodeUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a party node.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = PartyService(db)
    return service.update_party(party_id, data, user_id)


@router.delete(
    "/{party_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a party node"
)
async def delete_party(
    case_id: str,
    party_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a party node.

    Warning: This will also delete all relationships and evidence links
    associated with this party.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = PartyService(db)
    service.delete_party(party_id, user_id)

    return None


# Graph endpoint (separate prefix from parties)
graph_router = APIRouter(
    prefix="/cases/{case_id}",
    tags=["parties"]
)


@graph_router.get(
    "/graph",
    response_model=dict,
    summary="Get the full party graph for a case"
)
async def get_graph(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get the complete party relationship graph for a case.

    Returns both party nodes and relationships in a single response
    for efficient React Flow rendering.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = PartyService(db)
    return service.get_graph(case_id)


# ============================================
# 012-precedent-integration: T040 자동 추출 엔드포인트
# ============================================
@router.post(
    "/auto-extract",
    response_model=AutoExtractedPartyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save auto-extracted party from AI Worker"
)
async def auto_extract_party(
    case_id: str,
    data: AutoExtractedPartyRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Save a party auto-extracted by AI Worker.

    - Checks for duplicate names (similarity threshold 0.8)
    - Minimum confidence threshold: 0.7
    - Requires write access to the case.

    Returns:
        - id: New or existing party ID
        - is_duplicate: True if matched existing party
        - matched_party_id: Existing party ID if duplicate
    """
    verify_case_write_access(case_id, db, user_id)

    # Confidence threshold check
    if data.extraction_confidence < 0.7:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extraction confidence must be at least 0.7"
        )

    service = PartyService(db)
    return service.create_auto_extracted_party(case_id, data, user_id)
