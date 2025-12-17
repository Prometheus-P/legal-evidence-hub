"""
Dashboard Service for Today View (US7)
Task T091

Provides aggregated dashboard data including:
- Today's urgent items (deadlines, court dates)
- This week's upcoming tasks
"""

from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models import CalendarEvent, Case, CaseMember
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service for dashboard data aggregation
    """

    def __init__(self, db: Session):
        self.db = db

    def get_today_items(self, user_id: str) -> Dict[str, Any]:
        """
        Get today's dashboard items for a user

        Args:
            user_id: Current user ID

        Returns:
            Dict containing:
            - date: Today's date
            - urgent: List of today's items (sorted by time)
            - this_week: List of items within 7 days (sorted by days_remaining)
            - all_complete: True if no urgent items
        """
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
        week_end = today_start + timedelta(days=7)

        # Get user's cases (for context)
        user_cases = self._get_user_cases(user_id)
        case_map = {case.id: case for case in user_cases}

        # Get today's events (urgent)
        urgent_events = self._get_events_for_period(
            user_id=user_id,
            start=today_start,
            end=today_end
        )

        # Get this week's events (excluding today)
        tomorrow_start = today_start + timedelta(days=1)
        week_events = self._get_events_for_period(
            user_id=user_id,
            start=tomorrow_start,
            end=week_end
        )

        # Format responses
        urgent_items = self._format_urgent_items(urgent_events, case_map)
        week_items = self._format_week_items(week_events, case_map, today)

        return {
            "date": today.isoformat(),
            "urgent": urgent_items,
            "this_week": week_items,
            "all_complete": len(urgent_items) == 0
        }

    def _get_user_cases(self, user_id: str) -> List[Case]:
        """Get all cases the user has access to"""
        case_ids = self.db.query(CaseMember.case_id).filter(
            CaseMember.user_id == user_id
        ).subquery()

        return self.db.query(Case).filter(
            Case.id.in_(case_ids)
        ).all()

    def _get_events_for_period(
        self,
        user_id: str,
        start: datetime,
        end: datetime
    ) -> List[CalendarEvent]:
        """
        Get calendar events for a specific period

        Returns events that:
        - Belong to the user directly, OR
        - Are linked to cases the user has access to
        """
        # Get user's case IDs
        user_case_ids = self.db.query(CaseMember.case_id).filter(
            CaseMember.user_id == user_id
        ).subquery()

        events = self.db.query(CalendarEvent).filter(
            and_(
                CalendarEvent.start_time >= start,
                CalendarEvent.start_time <= end,
                or_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.case_id.in_(user_case_ids)
                )
            )
        ).order_by(CalendarEvent.start_time).all()

        return events

    def _format_urgent_items(
        self,
        events: List[CalendarEvent],
        case_map: Dict[str, Case]
    ) -> List[Dict[str, Any]]:
        """Format events as urgent items (today's items)"""
        items = []
        for event in events:
            case = case_map.get(event.case_id) if event.case_id else None
            items.append({
                "id": event.id,
                "title": event.title,
                "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                "start_time": event.start_time.strftime("%H:%M") if event.start_time else None,
                "location": event.location,
                "case_id": event.case_id,
                "case_title": case.title if case else None,
                "description": event.description
            })

        # Sort by time (earliest first)
        items.sort(key=lambda x: x.get("start_time") or "23:59")
        return items

    def _format_week_items(
        self,
        events: List[CalendarEvent],
        case_map: Dict[str, Case],
        today: date
    ) -> List[Dict[str, Any]]:
        """Format events as this week's items (future items)"""
        items = []
        for event in events:
            case = case_map.get(event.case_id) if event.case_id else None
            event_date = event.start_time.date() if event.start_time else today
            days_remaining = (event_date - today).days

            items.append({
                "id": event.id,
                "title": event.title,
                "event_type": event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                "start_date": event_date.isoformat(),
                "start_time": event.start_time.strftime("%H:%M") if event.start_time else None,
                "days_remaining": days_remaining,
                "location": event.location,
                "case_id": event.case_id,
                "case_title": case.title if case else None,
                "description": event.description
            })

        # Sort by days remaining (closest first)
        items.sort(key=lambda x: x.get("days_remaining", 999))
        return items
