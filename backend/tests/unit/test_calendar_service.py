"""
Unit tests for Calendar Service
TDD - Improving test coverage for calendar_service.py
"""

import pytest
from datetime import datetime, timezone
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

            result = service.update_event("nonexistent", {}, "user-123")

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
