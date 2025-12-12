"""
Relationships API Router - REST endpoints for party relationship management
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
from app.db.models import RelationshipType
from app.db.schemas import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    PartyGraphResponse,
    AutoExtractedRelationshipRequest,
    AutoExtractedRelationshipResponse
)
from app.services.relationship_service import RelationshipService

router = APIRouter(
    prefix="/cases/{case_id}",
    tags=["relationships"]
)


# ============================================================
# Relationship CRUD Endpoints
# ============================================================

@router.post(
    "/relationships",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new relationship"
)
async def create_relationship(
    case_id: str,
    data: RelationshipCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new relationship between two parties.

    Validates:
    - Both parties exist and belong to the case
    - No self-reference (source != target)
    - No duplicate relationship of the same type

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = RelationshipService(db)
    return service.create_relationship(case_id, data, user_id)


@router.get(
    "/relationships",
    response_model=dict,
    summary="Get all relationships for a case"
)
async def get_relationships(
    case_id: str,
    type: Optional[RelationshipType] = Query(None, description="Filter by relationship type"),
    party_id: Optional[str] = Query(None, description="Filter by party involvement (source or target)"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all relationships for a case.

    Optional filters:
    - type: Filter by relationship type (marriage, affair, parent_child, etc.)
    - party_id: Filter by party involvement (returns relationships where party is source or target)

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = RelationshipService(db)
    relationships = service.get_relationships_for_case(case_id, type, party_id)

    return {
        "items": relationships,
        "total": len(relationships)
    }


@router.get(
    "/relationships/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Get a specific relationship"
)
async def get_relationship(
    case_id: str,
    relationship_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific relationship by ID.

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = RelationshipService(db)
    return service.get_relationship(relationship_id)


@router.patch(
    "/relationships/{relationship_id}",
    response_model=RelationshipResponse,
    summary="Update a relationship"
)
async def update_relationship(
    case_id: str,
    relationship_id: str,
    data: RelationshipUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a relationship.

    Can update:
    - type: Relationship type
    - start_date: Relationship start date
    - end_date: Relationship end date
    - notes: Additional notes

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = RelationshipService(db)
    return service.update_relationship(relationship_id, data, user_id)


@router.delete(
    "/relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a relationship"
)
async def delete_relationship(
    case_id: str,
    relationship_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a relationship.

    Warning: This will also delete all evidence links associated with this relationship.

    Requires write access to the case.
    """
    verify_case_write_access(case_id, db, user_id)

    service = RelationshipService(db)
    service.delete_relationship(relationship_id, user_id)

    return None


# ============================================================
# Party Graph Endpoint (combined data for React Flow)
# ============================================================

@router.get(
    "/graph",
    response_model=PartyGraphResponse,
    summary="Get complete party graph"
)
async def get_party_graph(
    case_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get the complete party graph for a case.

    Returns all party nodes and relationships in a single response,
    optimized for React Flow rendering.

    Response format:
    ```json
    {
        "nodes": [
            {
                "id": "party_xxx",
                "case_id": "...",
                "type": "plaintiff",
                "name": "김철수",
                "position": {"x": 100, "y": 200},
                ...
            }
        ],
        "relationships": [
            {
                "id": "rel_xxx",
                "source_party_id": "party_xxx",
                "target_party_id": "party_yyy",
                "type": "marriage",
                ...
            }
        ]
    }
    ```

    Requires read access to the case.
    """
    verify_case_read_access(case_id, db, user_id)

    service = RelationshipService(db)
    return service.get_party_graph(case_id)

# ============================================
# 012-precedent-integration: T042 자동 추출 엔드포인트
# ============================================
@router.post(
    "/relationships/auto-extract",
    response_model=AutoExtractedRelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save auto-extracted relationship from AI Worker"
)
async def auto_extract_relationship(
    case_id: str,
    data: AutoExtractedRelationshipRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Save a relationship auto-extracted by AI Worker.

    - Minimum confidence threshold: 0.7 (enforced in schema)
    - Validates both parties exist
    - Requires write access to the case.

    Returns:
        - id: New relationship ID
        - created: True if newly created
    """
    verify_case_write_access(case_id, db, user_id)

    service = RelationshipService(db)
    return service.create_auto_extracted_relationship(case_id, data, user_id)
