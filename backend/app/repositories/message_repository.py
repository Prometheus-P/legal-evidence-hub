"""
Message Repository
Issue #296 - FR-008

Data access layer for message operations.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from app.db.models import Message


class MessageRepository:
    """Repository for message CRUD operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        subject: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> Message:
        """Create a new message"""
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject=subject,
            content=content,
            case_id=case_id,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID with sender/recipient info"""
        return (
            self.db.query(Message)
            .options(joinedload(Message.sender), joinedload(Message.recipient))
            .filter(Message.id == message_id)
            .first()
        )

    def get_inbox(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Message], int]:
        """Get received messages (inbox)"""
        query = (
            self.db.query(Message)
            .options(joinedload(Message.sender))
            .filter(
                Message.recipient_id == user_id,
                Message.is_deleted_by_recipient.is_(False),
            )
            .order_by(Message.created_at.desc())
        )

        total = query.count()
        messages = query.offset((page - 1) * limit).limit(limit).all()
        return messages, total

    def get_sent(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Message], int]:
        """Get sent messages"""
        query = (
            self.db.query(Message)
            .options(joinedload(Message.recipient))
            .filter(
                Message.sender_id == user_id,
                Message.is_deleted_by_sender.is_(False),
            )
            .order_by(Message.created_at.desc())
        )

        total = query.count()
        messages = query.offset((page - 1) * limit).limit(limit).all()
        return messages, total

    def mark_as_read(self, message_id: str) -> Optional[Message]:
        """Mark a message as read"""
        message = self.get_by_id(message_id)
        if message and not message.is_read:
            message.is_read = True
            message.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(message)
        return message

    def soft_delete(self, message_id: str, user_id: str) -> Optional[Message]:
        """Soft delete a message (mark as deleted by sender or recipient)"""
        message = self.get_by_id(message_id)
        if not message:
            return None

        if message.sender_id == user_id:
            message.is_deleted_by_sender = True
        elif message.recipient_id == user_id:
            message.is_deleted_by_recipient = True
        else:
            return None

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread messages for a user"""
        return (
            self.db.query(Message)
            .filter(
                Message.recipient_id == user_id,
                Message.is_read.is_(False),
                Message.is_deleted_by_recipient.is_(False),
            )
            .count()
        )
