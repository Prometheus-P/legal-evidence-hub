"""
Notification Repository
Issue #295 - FR-007

Data access layer for notification operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models import Notification, NotificationType


class NotificationRepository:
    """Repository for notification CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str,
        title: str,
        content: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        related_id: Optional[str] = None,
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            related_id=related_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        return self.db.query(Notification).filter(Notification.id == notification_id).first()

    def get_by_user(
        self,
        user_id: str,
        limit: int = 10,
        unread_only: bool = False,
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read.is_(False))

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .count()
        )

    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        count = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .update({"is_read": True})
        )
        self.db.commit()
        return count

    def delete(self, notification_id: str) -> bool:
        """Delete a notification"""
        notification = self.get_by_id(notification_id)
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False
