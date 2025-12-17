"""
Lawyer Investigators API Router
005-lawyer-portal-pages Feature - US3
Issue #301 - FR-011, FR-012, FR-016: Detective Contact CRUD

API endpoints for lawyer's investigator management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import DetectiveContact
from app.core.dependencies import get_current_user_id
from app.services.investigator_list_service import InvestigatorListService
from app.schemas.investigator_list import (
    InvestigatorListResponse,
    InvestigatorDetail,
    InvestigatorFilter,
    InvestigatorSortField,
    SortOrder,
    AvailabilityStatus,
    DetectiveContactCreate,
    DetectiveContactUpdate,
    DetectiveContactResponse,
    DetectiveContactListResponse,
)


router = APIRouter(prefix="/lawyer/investigators", tags=["lawyer-investigators"])


@router.get("", response_model=InvestigatorListResponse)
async def get_investigators(
    search: Optional[str] = Query(None, description="Search by name or email"),
    availability: Optional[AvailabilityStatus] = Query(
        None, description="Filter by availability"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: InvestigatorSortField = Query(
        InvestigatorSortField.NAME, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get list of lawyer's investigators with filters and pagination.

    Investigators are users with role='detective' who are members of cases
    that the current lawyer has access to.
    """
    service = InvestigatorListService(db)

    filters = InvestigatorFilter(
        search=search,
        availability=availability,
    )

    return service.get_investigators(
        lawyer_id=user_id,
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{investigator_id}", response_model=InvestigatorDetail)
async def get_investigator_detail(
    investigator_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get detailed information for a specific investigator.

    Returns 404 if investigator is not found or lawyer doesn't have access.
    """
    service = InvestigatorListService(db)

    investigator = service.get_investigator_detail(
        lawyer_id=user_id,
        investigator_id=investigator_id,
    )

    if not investigator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigator not found or access denied",
        )

    return investigator


# ============================================
# Detective Contact CRUD Endpoints (Issue #301)
# ============================================
@router.get("/contacts", response_model=DetectiveContactListResponse)
async def list_detective_contacts(
    search: Optional[str] = Query(None, description="Search by name, email, phone, or specialty"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    List all detective contacts for the current lawyer.
    FR-011: 탐정 목록 조회
    """
    query = db.query(DetectiveContact).filter(DetectiveContact.lawyer_id == user_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (DetectiveContact.name.ilike(search_filter)) |
            (DetectiveContact.email.ilike(search_filter)) |
            (DetectiveContact.phone.ilike(search_filter)) |
            (DetectiveContact.specialty.ilike(search_filter))
        )

    total = query.count()
    contacts = (
        query
        .order_by(DetectiveContact.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return DetectiveContactListResponse(
        items=[DetectiveContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/contacts", response_model=DetectiveContactResponse, status_code=status.HTTP_201_CREATED)
async def create_detective_contact(
    payload: DetectiveContactCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new detective contact.
    FR-011: 탐정 등록
    """
    contact = DetectiveContact(
        lawyer_id=user_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        specialty=payload.specialty,
        memo=payload.memo,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return DetectiveContactResponse.model_validate(contact)


@router.get("/contacts/{contact_id}", response_model=DetectiveContactResponse)
async def get_detective_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific detective contact by ID.
    """
    contact = (
        db.query(DetectiveContact)
        .filter(DetectiveContact.id == contact_id, DetectiveContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detective contact not found",
        )

    return DetectiveContactResponse.model_validate(contact)


@router.put("/contacts/{contact_id}", response_model=DetectiveContactResponse)
async def update_detective_contact(
    contact_id: str,
    payload: DetectiveContactUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update an existing detective contact.
    FR-012: 탐정 수정
    """
    contact = (
        db.query(DetectiveContact)
        .filter(DetectiveContact.id == contact_id, DetectiveContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detective contact not found",
        )

    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return DetectiveContactResponse.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detective_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a detective contact.
    FR-016: 탐정 삭제
    """
    contact = (
        db.query(DetectiveContact)
        .filter(DetectiveContact.id == contact_id, DetectiveContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detective contact not found",
        )

    db.delete(contact)
    db.commit()

    return None
