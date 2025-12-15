"""
Lawyer Clients API Router
005-lawyer-portal-pages Feature - US2
Issue #300 - FR-009, FR-010, FR-015: Client Contact CRUD

API endpoints for lawyer's client management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ClientContact
from app.core.dependencies import get_current_user_id
from app.services.client_list_service import ClientListService
from app.schemas.client_list import (
    ClientListResponse,
    ClientDetail,
    ClientFilter,
    ClientSortField,
    SortOrder,
    ClientStatus,
    ClientContactCreate,
    ClientContactUpdate,
    ClientContactResponse,
    ClientContactListResponse,
)


router = APIRouter(prefix="/lawyer/clients", tags=["lawyer-clients"])


@router.get("", response_model=ClientListResponse)
async def get_clients(
    search: Optional[str] = Query(None, description="Search by name or email"),
    status: Optional[ClientStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: ClientSortField = Query(
        ClientSortField.NAME, description="Field to sort by"
    ),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get list of lawyer's clients with filters and pagination.

    Clients are users with role='client' who are members of cases
    that the current lawyer has access to.
    """
    service = ClientListService(db)

    filters = ClientFilter(
        search=search,
        status=status,
    )

    return service.get_clients(
        lawyer_id=user_id,
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{client_id}", response_model=ClientDetail)
async def get_client_detail(
    client_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get detailed information for a specific client.

    Returns 404 if client is not found or lawyer doesn't have access.
    """
    service = ClientListService(db)

    client = service.get_client_detail(
        lawyer_id=user_id,
        client_id=client_id,
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found or access denied",
        )

    return client


# ============================================
# Client Contact CRUD Endpoints (Issue #300)
# ============================================
@router.get("/contacts", response_model=ClientContactListResponse)
async def list_client_contacts(
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    List all client contacts for the current lawyer.
    FR-009: 의뢰인 목록 조회
    """
    query = db.query(ClientContact).filter(ClientContact.lawyer_id == user_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (ClientContact.name.ilike(search_filter)) |
            (ClientContact.email.ilike(search_filter)) |
            (ClientContact.phone.ilike(search_filter))
        )

    total = query.count()
    contacts = (
        query
        .order_by(ClientContact.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ClientContactListResponse(
        items=[ClientContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/contacts", response_model=ClientContactResponse, status_code=status.HTTP_201_CREATED)
async def create_client_contact(
    payload: ClientContactCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new client contact.
    FR-009: 의뢰인 등록
    """
    contact = ClientContact(
        lawyer_id=user_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        memo=payload.memo,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return ClientContactResponse.model_validate(contact)


@router.get("/contacts/{contact_id}", response_model=ClientContactResponse)
async def get_client_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific client contact by ID.
    """
    contact = (
        db.query(ClientContact)
        .filter(ClientContact.id == contact_id, ClientContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client contact not found",
        )

    return ClientContactResponse.model_validate(contact)


@router.put("/contacts/{contact_id}", response_model=ClientContactResponse)
async def update_client_contact(
    contact_id: str,
    payload: ClientContactUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update an existing client contact.
    FR-010: 의뢰인 수정
    """
    contact = (
        db.query(ClientContact)
        .filter(ClientContact.id == contact_id, ClientContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client contact not found",
        )

    # Update only provided fields
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return ClientContactResponse.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_contact(
    contact_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a client contact.
    FR-015: 의뢰인 삭제
    """
    contact = (
        db.query(ClientContact)
        .filter(ClientContact.id == contact_id, ClientContact.lawyer_id == user_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client contact not found",
        )

    db.delete(contact)
    db.commit()

    return None
