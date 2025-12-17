"""
Detective Contact API Routes
Issue #298 - FR-011~012, FR-016

API endpoints for detective contact management.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_id
from app.core.error_messages import ErrorMessages
from app.services.detective_contact_service import DetectiveContactService
from app.db.schemas import (
    DetectiveContactCreate,
    DetectiveContactUpdate,
    DetectiveContactResponse,
    DetectiveContactListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/detectives", tags=["detectives"])


@router.get(
    "",
    response_model=DetectiveContactListResponse,
    summary="Get detective contacts",
    description="Get current lawyer's detective contacts with optional search",
)
async def get_detectives(
    search: str = Query(None, description="Search by name, phone, email, or specialty"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get detective contacts for the current lawyer.

    - **Lawyer role required**
    - Supports search by name, phone, email, or specialty
    - Paginated results

    Returns:
        - items: List of detective contacts
        - total: Total number of matching contacts
        - page: Current page number
        - limit: Items per page
    """
    service = DetectiveContactService(db)
    try:
        return service.get_detectives(
            lawyer_id=user_id,
            search=search,
            page=page,
            limit=limit,
        )
    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id}: {e}")
        raise HTTPException(status_code=403, detail=ErrorMessages.PERMISSION_DENIED)


@router.post(
    "",
    response_model=DetectiveContactResponse,
    status_code=201,
    summary="Create detective contact",
    description="Create a new detective contact",
)
async def create_detective(
    data: DetectiveContactCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new detective contact.

    - **Lawyer role required**
    - Name is required
    - Either phone or email must be provided

    Returns:
        - Created detective contact object
    """
    service = DetectiveContactService(db)
    try:
        return service.create_detective(lawyer_id=user_id, data=data)
    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id} creating detective: {e}")
        raise HTTPException(status_code=403, detail=ErrorMessages.PERMISSION_DENIED)
    except ValueError as e:
        logger.warning(f"Validation error creating detective: {e}")
        raise HTTPException(status_code=400, detail="탐정 연락처 생성에 실패했습니다. 입력값을 확인해주세요")


@router.get(
    "/{detective_id}",
    response_model=DetectiveContactResponse,
    summary="Get detective contact",
    description="Get a specific detective contact by ID",
)
async def get_detective(
    detective_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get a specific detective contact.

    - **Lawyer role required**
    - Only returns contacts owned by the current lawyer
    """
    service = DetectiveContactService(db)
    try:
        return service.get_detective(detective_id=detective_id, lawyer_id=user_id)
    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id} accessing detective {detective_id}: {e}")
        raise HTTPException(status_code=403, detail=ErrorMessages.PERMISSION_DENIED)
    except KeyError:
        raise HTTPException(status_code=404, detail=ErrorMessages.DETECTIVE_NOT_FOUND)


@router.put(
    "/{detective_id}",
    response_model=DetectiveContactResponse,
    summary="Update detective contact",
    description="Update a detective contact's information",
)
async def update_detective(
    detective_id: str,
    data: DetectiveContactUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Update a detective contact.

    - **Lawyer role required**
    - Only updates contacts owned by the current lawyer
    - Must maintain at least one contact method (phone or email)
    """
    service = DetectiveContactService(db)
    try:
        return service.update_detective(
            detective_id=detective_id,
            lawyer_id=user_id,
            data=data,
        )
    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id} updating detective {detective_id}: {e}")
        raise HTTPException(status_code=403, detail=ErrorMessages.PERMISSION_DENIED)
    except KeyError:
        raise HTTPException(status_code=404, detail=ErrorMessages.DETECTIVE_NOT_FOUND)
    except ValueError as e:
        logger.warning(f"Validation error updating detective {detective_id}: {e}")
        raise HTTPException(status_code=400, detail="탐정 연락처 수정에 실패했습니다. 입력값을 확인해주세요")


@router.delete(
    "/{detective_id}",
    status_code=204,
    summary="Delete detective contact",
    description="Delete a detective contact (hard delete)",
)
async def delete_detective(
    detective_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Delete a detective contact.

    - **Lawyer role required**
    - Only deletes contacts owned by the current lawyer
    - This is a permanent deletion
    """
    service = DetectiveContactService(db)
    try:
        result = service.delete_detective(detective_id=detective_id, lawyer_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorMessages.DETECTIVE_NOT_FOUND)
    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id} deleting detective {detective_id}: {e}")
        raise HTTPException(status_code=403, detail=ErrorMessages.PERMISSION_DENIED)
