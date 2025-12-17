"""
Notification Service
Issue #295 - FR-007

Business logic for notification operations.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.db.schemas import (
    NotificationResponse,
    NotificationListResponse,
    NotificationReadAllResponse,
)


class NotificationService:
    """Service for notification business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)

    def create_notification(
        self,
        user_id: str,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        related_id: Optional[str] = None,
    ) -> NotificationResponse:
        """Create a new notification"""
        notification = self.repository.create(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            related_id=related_id,
        )
        return NotificationResponse.model_validate(notification)

    def get_notifications(
        self,
        user_id: str,
        limit: int = 10,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        """Get notifications for a user"""
        notifications = self.repository.get_by_user(
            user_id=user_id,
            limit=limit,
            unread_only=unread_only,
        )
        unread_count = self.repository.get_unread_count(user_id)

        return NotificationListResponse(
            notifications=[NotificationResponse.model_validate(n) for n in notifications],
            unread_count=unread_count,
        )

    def mark_as_read(self, notification_id: str, user_id: str) -> NotificationResponse:
        """Mark a notification as read"""
        notification = self.repository.get_by_id(notification_id)

        if not notification:
            raise KeyError("Notification not found")

        if notification.user_id != user_id:
            raise PermissionError("Not authorized to access this notification")

        updated = self.repository.mark_as_read(notification_id)
        return NotificationResponse.model_validate(updated)

    def mark_all_as_read(self, user_id: str) -> NotificationReadAllResponse:
        """Mark all notifications as read for a user"""
        count = self.repository.mark_all_as_read(user_id)
        return NotificationReadAllResponse(updated_count=count)

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return self.repository.get_unread_count(user_id)
