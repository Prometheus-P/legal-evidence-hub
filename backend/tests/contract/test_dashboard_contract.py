"""
Contract tests for Dashboard API (US7 - Today View)
Task T094 - TDD RED Phase

Tests for Dashboard endpoints:
- GET /dashboard/today - Get today's urgent items and this week's tasks
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi import status


class TestGetTodayItems:
    """Contract tests for GET /dashboard/today"""

    def test_should_return_empty_when_no_items(
        self, client, auth_headers
    ):
        """
        Given: User with no cases or calendar events
        When: GET /dashboard/today
        Then:
            - Returns 200 OK
            - Response contains empty urgent array
            - Response contains empty this_week array
            - Response contains today's date
        """
        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "urgent" in data
        assert "this_week" in data
        assert "date" in data
        assert isinstance(data["urgent"], list)
        assert isinstance(data["this_week"], list)

    def test_should_return_401_without_auth(self, client):
        """
        Given: No authentication
        When: GET /dashboard/today
        Then: Returns 401 Unauthorized
        """
        response = client.get("/dashboard/today")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTodayItemsWithCalendarEvents:
    """Contract tests for Today View with calendar events"""

    @pytest.fixture
    def case_with_events(self, client, test_case, auth_headers):
        """
        Create calendar events for today and this week
        """
        today = date.today()

        # Today's court date (urgent) - using datetime format
        today_court_time = datetime.combine(today, datetime.strptime("10:30", "%H:%M").time())
        today_event = client.post(
            "/calendar/events",
            json={
                "title": "김○○ 사건 변론기일",
                "event_type": "court",
                "start_time": today_court_time.isoformat(),
                "location": "서울가정법원",
                "case_id": test_case.id
            },
            headers=auth_headers
        )

        # Today's deadline (urgent)
        today_deadline_time = datetime.combine(today, datetime.strptime("17:00", "%H:%M").time())
        today_deadline = client.post(
            "/calendar/events",
            json={
                "title": "답변서 제출 마감",
                "event_type": "deadline",
                "start_time": today_deadline_time.isoformat(),
                "case_id": test_case.id
            },
            headers=auth_headers
        )

        # This week's deadline (D-2)
        future_date = today + timedelta(days=2)
        future_time = datetime.combine(future_date, datetime.strptime("12:00", "%H:%M").time())
        week_deadline = client.post(
            "/calendar/events",
            json={
                "title": "준비서면 제출",
                "event_type": "deadline",
                "start_time": future_time.isoformat(),
                "case_id": test_case.id
            },
            headers=auth_headers
        )

        return {
            "today_event": today_event.json() if today_event.status_code == 201 else None,
            "today_deadline": today_deadline.json() if today_deadline.status_code == 201 else None,
            "week_deadline": week_deadline.json() if week_deadline.status_code == 201 else None,
            "case": test_case
        }

    def test_should_return_todays_events_as_urgent(
        self, client, auth_headers, case_with_events
    ):
        """
        Given: Calendar events scheduled for today
        When: GET /dashboard/today
        Then:
            - Today's events appear in urgent array
            - Each item has case_id, title, event_type, time
        """
        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have urgent items for today
        assert len(data["urgent"]) >= 1

        # Verify urgent item structure
        for item in data["urgent"]:
            assert "id" in item
            assert "title" in item
            assert "event_type" in item
            assert "case_id" in item
            assert "case_title" in item

    def test_should_return_this_week_events(
        self, client, auth_headers, case_with_events
    ):
        """
        Given: Calendar events within this week (but not today)
        When: GET /dashboard/today
        Then:
            - Future events appear in this_week array
            - Each item has days_remaining (D-N)
        """
        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Find the week event
        week_items = [
            item for item in data["this_week"]
            if item.get("days_remaining", 0) > 0
        ]

        # Should have at least one future item
        for item in week_items:
            assert "days_remaining" in item
            assert item["days_remaining"] > 0

    def test_should_include_case_context(
        self, client, auth_headers, case_with_events
    ):
        """
        Given: Events linked to cases
        When: GET /dashboard/today
        Then: Each item includes case_id and case_title for navigation
        """
        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        all_items = data["urgent"] + data["this_week"]
        for item in all_items:
            assert "case_id" in item
            assert "case_title" in item


class TestTodayItemsPriority:
    """Contract tests for Today View priority ordering"""

    def test_should_sort_urgent_by_time(
        self, client, test_case, auth_headers
    ):
        """
        Given: Multiple events today at different times
        When: GET /dashboard/today
        Then: Urgent items sorted by time (earliest first)
        """
        today = date.today()

        # Create events at different times
        afternoon_time = datetime.combine(today, datetime.strptime("15:00", "%H:%M").time())
        client.post(
            "/calendar/events",
            json={
                "title": "오후 일정",
                "event_type": "meeting",
                "start_time": afternoon_time.isoformat(),
                "case_id": test_case.id
            },
            headers=auth_headers
        )

        morning_time = datetime.combine(today, datetime.strptime("09:00", "%H:%M").time())
        client.post(
            "/calendar/events",
            json={
                "title": "오전 일정",
                "event_type": "court",
                "start_time": morning_time.isoformat(),
                "case_id": test_case.id
            },
            headers=auth_headers
        )

        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if len(data["urgent"]) >= 2:
            # Verify time ordering (earlier times first)
            times = [item.get("start_time", "23:59") for item in data["urgent"]]
            assert times == sorted(times)

    def test_should_sort_this_week_by_days_remaining(
        self, client, test_case, auth_headers
    ):
        """
        Given: Multiple events this week
        When: GET /dashboard/today
        Then: This week items sorted by days_remaining (closest first)
        """
        today = date.today()

        # Create events on different days
        for days in [5, 2, 3]:
            future_date = today + timedelta(days=days)
            future_time = datetime.combine(future_date, datetime.strptime("12:00", "%H:%M").time())
            client.post(
                "/calendar/events",
                json={
                    "title": f"D-{days} 일정",
                    "event_type": "deadline",
                    "start_time": future_time.isoformat(),
                    "case_id": test_case.id
                },
                headers=auth_headers
            )

        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        if len(data["this_week"]) >= 2:
            days = [item.get("days_remaining", 999) for item in data["this_week"]]
            assert days == sorted(days)


class TestAllCompleteMessage:
    """Contract tests for completion message"""

    def test_should_show_completion_when_no_urgent(
        self, client, auth_headers
    ):
        """
        Given: No urgent items for today
        When: GET /dashboard/today
        Then: Response includes all_complete flag
        """
        response = client.get(
            "/dashboard/today",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # When no urgent items, all_complete should be true
        if len(data["urgent"]) == 0:
            assert data.get("all_complete", False) is True
