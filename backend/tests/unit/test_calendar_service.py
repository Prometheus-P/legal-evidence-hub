"""
Unit tests for Calendar Service
TDD - Improving test coverage for calendar_service.py
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from app.services.calendar_service import CalendarService
from app.db.models import CalendarEvent, CalendarEventType


class TestGetEventById:
    """Unit tests for get_event_by_id method"""

    def test_get_event_not_found(self):
        """Returns None when event not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_event_by_id("nonexistent", "user-123")

            assert result is None


class TestUpdateEvent:
    """Unit tests for update_event method"""

    def test_update_event_not_found(self):
        """Returns None when event not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.update_event("nonexistent", "user-123", {})

            assert result is None


class TestDeleteEvent:
    """Unit tests for delete_event method"""

    def test_delete_event_not_found(self):
        """Returns False when event not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.delete_event("nonexistent", "user-123")

            assert result is False


class TestGetEventColor:
    """Unit tests for get_event_color method"""

    def test_get_event_color_court(self):
        """Returns correct color for court event"""
        mock_db = MagicMock()

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_event_color(CalendarEventType.COURT)

            assert isinstance(result, str)
            assert result.startswith("#")

    def test_get_event_color_meeting(self):
        """Returns correct color for meeting event"""
        mock_db = MagicMock()

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_event_color(CalendarEventType.MEETING)

            assert isinstance(result, str)


class TestGetReminders:
    """Unit tests for get_reminders method"""

    def test_get_reminders_empty(self):
        """Returns empty list when no upcoming events"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_reminders("user-123")

            assert result == []


class TestDeleteEventSuccess:
    """Unit tests for delete_event success case"""

    def test_delete_event_success(self):
        """Successfully deletes an event"""
        mock_db = MagicMock()
        mock_event = MagicMock()
        mock_event.id = "event-123"
        mock_event.user_id = "user-123"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_event

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.delete_event("event-123", "user-123")

            assert result is True
            mock_db.delete.assert_called_once_with(mock_event)
            mock_db.commit.assert_called_once()


class TestUpdateEventFields:
    """Unit tests for update_event with various field updates"""

    def test_update_event_case_not_found(self):
        """Raises ValueError when updating with invalid case_id"""
        mock_db = MagicMock()
        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-123"
        mock_event.user_id = "user-123"

        # First query returns event, second query returns None (case not found)
        call_count = [0]

        def query_side_effect(*args):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                # CalendarEvent query
                result.filter.return_value.first.return_value = mock_event
            else:
                # Case query - returns None
                result.filter.return_value.first.return_value = None
            return result

        mock_db.query.side_effect = query_side_effect

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            mock_event_data = MagicMock()
            mock_event_data.case_id = "nonexistent-case"
            mock_event_data.title = None
            mock_event_data.description = None
            mock_event_data.event_type = None
            mock_event_data.start_time = None
            mock_event_data.end_time = None
            mock_event_data.location = None
            mock_event_data.reminder_minutes = None

            with pytest.raises(ValueError, match="Case not found"):
                service.update_event("event-123", "user-123", mock_event_data)

    def test_update_event_with_description_location_reminder(self):
        """Updates event with description, location, and reminder_minutes"""
        mock_db = MagicMock()
        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-123"
        mock_event.user_id = "user-123"
        mock_event.case_id = None
        mock_event.case = None
        mock_event.title = "Original Title"
        mock_event.description = "Original"
        mock_event.event_type = CalendarEventType.MEETING
        mock_event.start_time = datetime.now(timezone.utc)
        mock_event.end_time = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_event.location = "Old location"
        mock_event.reminder_minutes = "30"
        mock_event.created_at = datetime.now(timezone.utc)

        mock_db.query.return_value.filter.return_value.first.return_value = mock_event

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            mock_event_data = MagicMock()
            mock_event_data.case_id = None
            mock_event_data.title = None
            mock_event_data.description = "Updated description"
            mock_event_data.event_type = None
            mock_event_data.start_time = None
            mock_event_data.end_time = None
            mock_event_data.location = "New location"
            mock_event_data.reminder_minutes = 60

            service.update_event("event-123", "user-123", mock_event_data)

            # Check fields were updated (lines 176, 184, 186)
            assert mock_event.description == "Updated description"
            assert mock_event.location == "New location"
            assert mock_event.reminder_minutes == "60"
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_event)


class TestGetRemindersEdgeCases:
    """Unit tests for get_reminders edge cases"""

    def test_get_reminders_skips_past_events(self):
        """Skips events that have already started (line 271)"""
        mock_db = MagicMock()

        # Create a past event (start_time in the past)
        mock_past_event = MagicMock(spec=CalendarEvent)
        mock_past_event.id = "past-event"
        mock_past_event.user_id = "user-123"
        mock_past_event.start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        mock_past_event.reminder_minutes = "30"

        mock_db.query.return_value.filter.return_value.all.return_value = [mock_past_event]

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_reminders("user-123")

            # Past event should be skipped
            assert result == []

    def test_get_reminders_invalid_reminder_minutes(self):
        """Uses default 30 minutes when reminder_minutes is invalid (lines 275-276)"""
        mock_db = MagicMock()

        # Create event with invalid reminder_minutes
        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-123"
        mock_event.user_id = "user-123"
        mock_event.case_id = None
        mock_event.case = None
        mock_event.title = "Test Event"
        mock_event.description = None
        mock_event.event_type = CalendarEventType.MEETING
        # Event starts in 15 minutes (within 30-minute default reminder window)
        mock_event.start_time = datetime.now(timezone.utc) + timedelta(minutes=15)
        mock_event.end_time = mock_event.start_time + timedelta(hours=1)
        mock_event.location = None
        mock_event.reminder_minutes = "invalid"  # Invalid value
        mock_event.created_at = datetime.now(timezone.utc)

        mock_db.query.return_value.filter.return_value.all.return_value = [mock_event]

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_reminders("user-123")

            # Event should be returned with default 30-minute reminder
            assert len(result) == 1
            assert result[0]["id"] == "event-123"
            assert result[0]["reminder_due"] is True

    def test_get_reminders_none_reminder_minutes(self):
        """Uses default 30 minutes when reminder_minutes is None (lines 275-276)"""
        mock_db = MagicMock()

        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-456"
        mock_event.user_id = "user-123"
        mock_event.case_id = None
        mock_event.case = None
        mock_event.title = "Test Event"
        mock_event.description = None
        mock_event.event_type = CalendarEventType.MEETING
        mock_event.start_time = datetime.now(timezone.utc) + timedelta(minutes=20)
        mock_event.end_time = mock_event.start_time + timedelta(hours=1)
        mock_event.location = None
        mock_event.reminder_minutes = None  # None value
        mock_event.created_at = datetime.now(timezone.utc)

        mock_db.query.return_value.filter.return_value.all.return_value = [mock_event]

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service.get_reminders("user-123")

            assert len(result) == 1
            assert result[0]["reminder_due"] is True


class TestEventToDict:
    """Unit tests for _event_to_dict method"""

    def test_event_to_dict_invalid_reminder_minutes(self):
        """Uses default 30 when reminder_minutes cannot be parsed (lines 301-302)"""
        mock_db = MagicMock()

        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-123"
        mock_event.user_id = "user-123"
        mock_event.case_id = None
        mock_event.case = None
        mock_event.title = "Test Event"
        mock_event.description = "Test"
        mock_event.event_type = CalendarEventType.MEETING
        mock_event.start_time = datetime.now(timezone.utc)
        mock_event.end_time = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_event.location = "Test Location"
        mock_event.reminder_minutes = "not_a_number"  # Invalid
        mock_event.created_at = datetime.now(timezone.utc)

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service._event_to_dict(mock_event)

            assert result["id"] == "event-123"
            assert result["reminder_minutes"] == 30  # Default value

    def test_event_to_dict_none_reminder_minutes(self):
        """Uses default 30 when reminder_minutes is None (lines 301-302)"""
        mock_db = MagicMock()

        mock_event = MagicMock(spec=CalendarEvent)
        mock_event.id = "event-456"
        mock_event.user_id = "user-123"
        mock_event.case_id = None
        mock_event.case = None
        mock_event.title = "Another Event"
        mock_event.description = None
        mock_event.event_type = CalendarEventType.COURT
        mock_event.start_time = datetime.now(timezone.utc)
        mock_event.end_time = None
        mock_event.location = None
        mock_event.reminder_minutes = None  # None value
        mock_event.created_at = datetime.now(timezone.utc)

        with patch.object(CalendarService, '__init__', lambda x, y: None):
            service = CalendarService(mock_db)
            service.db = mock_db

            result = service._event_to_dict(mock_event)

            assert result["id"] == "event-456"
            assert result["reminder_minutes"] == 30
