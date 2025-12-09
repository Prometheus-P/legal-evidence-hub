"""
Unit tests for Message Service
TDD - Improving test coverage for message_service.py
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.message_service import MessageService
from app.schemas.message import MessageCreate


class TestSendMessage:
    """Unit tests for send_message method"""

    def test_send_message_no_case_access(self):
        """Raises PermissionError when sender has no case access"""
        mock_db = MagicMock()

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db
            service._has_case_access = MagicMock(return_value=False)

            message_data = MessageCreate(
                case_id="case-123",
                recipient_id="recipient-123",
                content="테스트 메시지"
            )

            with pytest.raises(PermissionError, match="접근 권한이 없습니다"):
                service.send_message("sender-123", message_data)

    def test_send_message_recipient_not_found(self):
        """Raises ValueError when recipient not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db
            service._has_case_access = MagicMock(return_value=True)

            message_data = MessageCreate(
                case_id="case-123",
                recipient_id="nonexistent",
                content="테스트 메시지"
            )

            with pytest.raises(ValueError, match="수신자를 찾을 수 없습니다"):
                service.send_message("sender-123", message_data)

    def test_send_message_recipient_no_access(self):
        """Raises ValueError when recipient has no case access"""
        mock_db = MagicMock()
        mock_recipient = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_recipient

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db
            # Sender has access, recipient doesn't
            service._has_case_access = MagicMock(side_effect=[True, False])

            message_data = MessageCreate(
                case_id="case-123",
                recipient_id="recipient-123",
                content="테스트 메시지"
            )

            with pytest.raises(ValueError, match="수신자가 이 케이스에 접근할 수 없습니다"):
                service.send_message("sender-123", message_data)


class TestGetMessages:
    """Unit tests for get_messages method"""

    def test_get_messages_no_access(self):
        """Raises PermissionError when user has no case access"""
        mock_db = MagicMock()

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db
            service._has_case_access = MagicMock(return_value=False)

            with pytest.raises(PermissionError, match="접근 권한이 없습니다"):
                service.get_messages("user-123", "case-123")


class TestGetConversations:
    """Unit tests for get_conversations method"""

    def test_get_conversations_returns_empty_list(self):
        """Returns empty list when no conversations"""
        mock_db = MagicMock()
        # Mock empty results from query
        mock_db.query.return_value.filter.return_value.all.return_value = []

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service.get_conversations("user-123")

            assert result.conversations == []


class TestHasCaseAccess:
    """Unit tests for _has_case_access method"""

    def test_has_case_access_as_owner(self):
        """Returns True when user is case owner"""
        mock_db = MagicMock()
        mock_case = MagicMock()
        mock_case.created_by = "user-123"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_case

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service._has_case_access("user-123", "case-123")

            assert result is True

    def test_has_case_access_case_not_found(self):
        """Returns False when case not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service._has_case_access("user-123", "nonexistent")

            assert result is False


class TestMarkAsRead:
    """Unit tests for mark_as_read method"""

    def test_mark_as_read_updates_messages(self):
        """Marks messages as read and returns count"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.update.return_value = 3

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service.mark_as_read("user-123", ["msg-1", "msg-2", "msg-3"])

            assert result == 3
            mock_db.commit.assert_called_once()


class TestGetUnreadCount:
    """Unit tests for get_unread_count method"""

    def test_get_unread_count_returns_total_and_by_case(self):
        """Returns unread count total and breakdown"""
        mock_db = MagicMock()
        mock_msg1 = MagicMock()
        mock_msg1.case_id = "case-1"
        mock_msg2 = MagicMock()
        mock_msg2.case_id = "case-1"
        mock_msg3 = MagicMock()
        mock_msg3.case_id = "case-2"

        mock_db.query.return_value.filter.return_value.all.return_value = [mock_msg1, mock_msg2, mock_msg3]

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service.get_unread_count("user-123")

            assert result.total == 3
            assert result.by_case["case-1"] == 2
            assert result.by_case["case-2"] == 1


class TestGetOfflineMessages:
    """Unit tests for get_offline_messages method"""

    def test_get_offline_messages_returns_list(self):
        """Returns list of unread messages for offline queue"""
        mock_db = MagicMock()
        mock_msg = MagicMock()
        mock_msg.id = "msg-1"
        mock_msg.case_id = "case-1"
        mock_msg.sender_id = "sender-1"
        mock_msg.recipient_id = "user-1"
        mock_msg.content = "Test message"
        mock_msg.attachments = None
        mock_msg.read_at = None
        mock_msg.created_at = datetime.now(timezone.utc)

        mock_sender = MagicMock()
        mock_sender.id = "sender-1"
        mock_sender.name = "Sender Name"
        mock_sender.role = MagicMock()
        mock_sender.role.value = "lawyer"

        # Set up query chain for messages
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_msg]
        # Set up query for sender info
        mock_db.query.return_value.filter.return_value.first.return_value = mock_sender

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service.get_offline_messages("user-1")

            assert len(result) == 1
            assert result[0].id == "msg-1"


class TestToMessageResponse:
    """Unit tests for _to_message_response helper"""

    def test_to_message_response_with_attachments(self):
        """Converts message with JSON attachments"""
        import json
        mock_db = MagicMock()
        mock_msg = MagicMock()
        mock_msg.id = "msg-1"
        mock_msg.case_id = "case-1"
        mock_msg.sender_id = "sender-1"
        mock_msg.recipient_id = "user-1"
        mock_msg.content = "Test"
        mock_msg.attachments = json.dumps(["file1.pdf", "file2.jpg"])
        mock_msg.read_at = None
        mock_msg.created_at = datetime.now(timezone.utc)

        mock_sender = MagicMock()
        mock_sender.id = "sender-1"
        mock_sender.name = "Sender"
        mock_sender.role = MagicMock()
        mock_sender.role.value = "lawyer"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_sender

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service._to_message_response(mock_msg, "user-1")

            assert result.id == "msg-1"
            assert result.attachments == ["file1.pdf", "file2.jpg"]
            assert result.is_mine is False

    def test_to_message_response_invalid_json_attachments(self):
        """Handles invalid JSON in attachments gracefully"""
        mock_db = MagicMock()
        mock_msg = MagicMock()
        mock_msg.id = "msg-1"
        mock_msg.case_id = "case-1"
        mock_msg.sender_id = "sender-1"
        mock_msg.recipient_id = "user-1"
        mock_msg.content = "Test"
        mock_msg.attachments = "invalid json {{"
        mock_msg.read_at = None
        mock_msg.created_at = datetime.now(timezone.utc)

        mock_sender = MagicMock()
        mock_sender.id = "sender-1"
        mock_sender.name = "Sender"
        mock_sender.role = MagicMock()
        mock_sender.role.value = "lawyer"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_sender

        with patch.object(MessageService, '__init__', lambda x, y: None):
            service = MessageService(mock_db)
            service.db = mock_db

            result = service._to_message_response(mock_msg, "user-1")

            assert result.id == "msg-1"
            assert result.attachments is None  # Invalid JSON returns None


class TestGetMessagesPagination:
    """Integration tests for get_messages pagination (lines 129-131, 141)"""

    def test_get_messages_with_before_id_pagination(self, test_env):
        """Get messages with before_id filters by created_at (lines 129-131)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from app.db.models import User, Case, Message, CaseMember
        import uuid
        from datetime import timedelta

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        # Create user
        user = User(
            email=f"msg_pag_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Msg Pag User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create case
        case = Case(
            title=f"Test Case {unique_id}",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Create case member
        member = CaseMember(case_id=case.id, user_id=user.id, role="owner")
        db.add(member)
        db.commit()

        # Create messages with different timestamps
        messages = []
        for i in range(5):
            msg = Message(
                case_id=case.id,
                sender_id=user.id,
                recipient_id=user.id,
                content=f"Message {i}",
                created_at=now - timedelta(hours=5-i)  # msg 0 is oldest, msg 4 is newest
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            messages.append(msg)

        from app.services.message_service import MessageService
        service = MessageService(db)

        # Get messages before msg[2] (should exclude msg[2], msg[3], msg[4])
        result = service.get_messages(user.id, case.id, before_id=messages[2].id, limit=10)

        # Should only have messages before msg[2]'s created_at
        assert len(result.messages) == 2  # msg[0], msg[1]
        for msg in result.messages:
            assert msg.created_at < messages[2].created_at

        # Cleanup
        for msg in messages:
            db.query(Message).filter(Message.id == msg.id).delete()
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.delete(case)
        db.delete(user)
        db.commit()
        db.close()

    def test_get_messages_has_more_truncation(self, test_env):
        """Has more truncates messages to limit (line 141)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from app.db.models import User, Case, Message, CaseMember
        import uuid
        from datetime import timedelta

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        # Create user
        user = User(
            email=f"msg_hasmore_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="HasMore User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create case
        case = Case(
            title=f"Test Case {unique_id}",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Create case member
        member = CaseMember(case_id=case.id, user_id=user.id, role="owner")
        db.add(member)
        db.commit()

        # Create 5 messages
        messages = []
        for i in range(5):
            msg = Message(
                case_id=case.id,
                sender_id=user.id,
                recipient_id=user.id,
                content=f"Message {i}",
                created_at=now - timedelta(hours=5-i)
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            messages.append(msg)

        from app.services.message_service import MessageService
        service = MessageService(db)

        # Get with limit=3 - should trigger has_more and truncation
        result = service.get_messages(user.id, case.id, limit=3)

        assert len(result.messages) == 3  # Truncated to limit
        assert result.has_more is True  # More messages available

        # Cleanup
        for msg in messages:
            db.query(Message).filter(Message.id == msg.id).delete()
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.delete(case)
        db.delete(user)
        db.commit()
        db.close()


class TestGetConversationsEdgeCases:
    """Integration tests for get_conversations edge cases"""

    def test_get_conversations_skips_orphaned_messages(self, test_env):
        """Skips messages where case or user not found (line 195)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from app.db.models import User, Case, Message, CaseMember
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        # Create users
        user1 = User(
            email=f"conv_user1_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Conv User1",
            role="lawyer"
        )
        user2 = User(
            email=f"conv_user2_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Conv User2",
            role="client"
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        user2_id = user2.id

        # Create case
        case = Case(
            title=f"Test Case {unique_id}",
            status="active",
            created_by=user1.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Create case member
        member = CaseMember(case_id=case.id, user_id=user1.id, role="owner")
        db.add(member)
        db.commit()

        # Create message from user2 to user1
        msg = Message(
            case_id=case.id,
            sender_id=user2.id,
            recipient_id=user1.id,
            content="Test message",
            created_at=now
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        msg_id = msg.id

        # Delete user2 (creates orphaned message)
        db.delete(user2)
        db.commit()

        from app.services.message_service import MessageService
        service = MessageService(db)

        # Get conversations - should skip the orphaned message
        result = service.get_conversations(user1.id)

        # The message with deleted user should be skipped (line 195)
        assert result.conversations == []  # No valid conversations

        # Cleanup
        db.query(Message).filter(Message.id == msg_id).delete()
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.delete(case)
        db.delete(user1)
        db.commit()
        db.close()

    def test_get_conversations_counts_unread(self, test_env):
        """Counts unread messages correctly (lines 212-213)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from app.db.models import User, Case, Message, CaseMember
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        # Create users
        user1 = User(
            email=f"unread_user1_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Unread User1",
            role="lawyer"
        )
        user2 = User(
            email=f"unread_user2_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Unread User2",
            role="client"
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        # Create case
        case = Case(
            title=f"Test Case {unique_id}",
            status="active",
            created_by=user1.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Create case members
        member1 = CaseMember(case_id=case.id, user_id=user1.id, role="owner")
        member2 = CaseMember(case_id=case.id, user_id=user2.id, role="MEMBER")
        db.add(member1)
        db.add(member2)
        db.commit()

        # Create messages: 2 unread for user1 from user2
        messages = []
        for i in range(3):
            msg = Message(
                case_id=case.id,
                sender_id=user2.id,
                recipient_id=user1.id,
                content=f"Unread message {i}",
                created_at=now,
                read_at=now if i == 0 else None  # Only first message is read
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            messages.append(msg)

        from app.services.message_service import MessageService
        service = MessageService(db)

        # Get conversations for user1
        result = service.get_conversations(user1.id)

        # Should have 1 conversation with 2 unread messages
        assert len(result.conversations) == 1
        assert result.conversations[0].unread_count == 2  # 2 messages with read_at=None
        assert result.total_unread == 2

        # Cleanup
        for msg in messages:
            db.query(Message).filter(Message.id == msg.id).delete()
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.delete(case)
        db.delete(user2)
        db.delete(user1)
        db.commit()
        db.close()
