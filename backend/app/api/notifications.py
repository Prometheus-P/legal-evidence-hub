"""
Notification API Routes
Issue #295 - FR-007

API endpoints for notification operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user_id
from app.services.notification_service import NotificationService
from app.db.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationReadAllResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Get notifications",
    description="Get current user's notifications with optional filtering",
)
async def get_notifications(
    limit: int = Query(10, ge=1, le=100, description="Maximum notifications to return"),
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get notifications for the current user.

    Returns:
        - notifications: List of notification objects
        - unread_count: Total number of unread notifications
    """
    service = NotificationService(db)
    return service.get_notifications(
        user_id=user_id,
        limit=limit,
        unread_only=unread_only,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
    description="Mark a specific notification as read",
)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Mark a notification as read.

    Returns:
        - Updated notification object
    """
    service = NotificationService(db)
    try:
        return service.mark_as_read(notification_id, user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Notification not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")


@router.patch(
    "/read-all",
    response_model=NotificationReadAllResponse,
    summary="Mark all notifications as read",
    description="Mark all notifications as read for the current user",
)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Mark all notifications as read.

    Returns:
        - updated_count: Number of notifications marked as read
    """
    service = NotificationService(db)
    return service.mark_all_as_read(user_id)
