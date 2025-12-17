"""
Search Service - Unified search across cases, clients, evidence, events
007-lawyer-portal-v1: US6 (Global Search)
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timezone
from app.db.models import (
    Case, CaseMember,
    User, UserRole, UserStatus,
    Evidence,
    CalendarEvent
)
import logging

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result item"""
    def __init__(
        self,
        category: str,
        id: str,
        title: str,
        subtitle: Optional[str] = None,
        icon: str = "",
        url: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        self.category = category
        self.id = id
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.url = url
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "icon": self.icon,
            "url": self.url,
            "metadata": self.metadata
        }


class SearchService:
    """
    Service for unified search across multiple entities
    """

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: str,
        user_id: str,
        categories: Optional[List[str]] = None,
        limit: int = 20
    ) -> dict:
        """
        Search across cases, clients, evidence, and calendar events

        Args:
            query: Search query string
            user_id: User performing the search (for access control)
            categories: Optional list of categories to search (cases, clients, evidence, events)
            limit: Maximum results per category

        Returns:
            Dict with categorized search results
        """
        if not query or len(query.strip()) < 2:
            return {"results": [], "total": 0}

        query = query.strip().lower()
        results = []

        # Default to all categories if not specified
        if not categories:
            categories = ["cases", "clients", "evidence", "events"]

        # Get user's accessible case IDs for filtering
        accessible_case_ids = self._get_accessible_case_ids(user_id)

        if "cases" in categories:
            results.extend(self._search_cases(query, accessible_case_ids, limit))

        if "clients" in categories:
            results.extend(self._search_clients(query, limit))

        if "evidence" in categories:
            results.extend(self._search_evidence(query, accessible_case_ids, limit))

        if "events" in categories:
            results.extend(self._search_events(query, user_id, accessible_case_ids, limit))

        logger.info(f"Search query '{query}' by user {user_id}: {len(results)} results")

        return {
            "results": [r.to_dict() for r in results],
            "total": len(results),
            "query": query
        }

    def _get_accessible_case_ids(self, user_id: str) -> List[str]:
        """Get list of case IDs the user has access to"""
        memberships = self.db.query(CaseMember.case_id).filter(
            CaseMember.user_id == user_id
        ).all()
        return [m.case_id for m in memberships]

    def _search_cases(
        self,
        query: str,
        accessible_case_ids: List[str],
        limit: int
    ) -> List[SearchResult]:
        """Search cases by title, description, client_name"""
        results = []

        if not accessible_case_ids:
            return results

        cases = self.db.query(Case).filter(
            and_(
                Case.id.in_(accessible_case_ids),
                Case.deleted_at.is_(None),
                or_(
                    Case.title.ilike(f"%{query}%"),
                    Case.description.ilike(f"%{query}%"),
                    Case.client_name.ilike(f"%{query}%")
                )
            )
        ).limit(limit).all()

        for case in cases:
            status_text = case.status.value if case.status else "unknown"
            results.append(SearchResult(
                category="cases",
                id=case.id,
                title=case.title,
                subtitle=f"{case.client_name or '의뢰인 미지정'} - {status_text}",
                icon="folder",
                url=f"/lawyer/cases/{case.id}",
                metadata={
                    "status": status_text,
                    "client_name": case.client_name,
                    "created_at": case.created_at.isoformat() if case.created_at else None
                }
            ))

        return results

    def _search_clients(
        self,
        query: str,
        limit: int
    ) -> List[SearchResult]:
        """Search clients (users with CLIENT role) by name, email"""
        results = []

        clients = self.db.query(User).filter(
            and_(
                User.role == UserRole.CLIENT,
                User.status == UserStatus.ACTIVE,
                or_(
                    User.name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%")
                )
            )
        ).limit(limit).all()

        for client in clients:
            results.append(SearchResult(
                category="clients",
                id=client.id,
                title=client.name,
                subtitle=client.email,
                icon="user",
                url=f"/lawyer/clients/{client.id}",
                metadata={
                    "email": client.email,
                    "created_at": client.created_at.isoformat() if client.created_at else None
                }
            ))

        return results

    def _search_evidence(
        self,
        query: str,
        accessible_case_ids: List[str],
        limit: int
    ) -> List[SearchResult]:
        """Search evidence by file_name, ai_summary, ai_labels"""
        results = []

        if not accessible_case_ids:
            return results

        evidence_items = self.db.query(Evidence).filter(
            and_(
                Evidence.case_id.in_(accessible_case_ids),
                or_(
                    Evidence.file_name.ilike(f"%{query}%"),
                    Evidence.description.ilike(f"%{query}%"),
                    Evidence.ai_summary.ilike(f"%{query}%"),
                    Evidence.ai_labels.ilike(f"%{query}%")
                )
            )
        ).limit(limit).all()

        for evidence in evidence_items:
            summary = evidence.ai_summary or evidence.description or evidence.file_name
            if len(summary) > 50:
                summary = summary[:50] + "..."

            date_str = evidence.created_at.strftime("%Y-%m-%d") if evidence.created_at else ""

            results.append(SearchResult(
                category="evidence",
                id=evidence.id,
                title=evidence.file_name,
                subtitle=f"{summary} ({date_str})",
                icon="paperclip",
                url=f"/lawyer/cases/{evidence.case_id}/evidence/{evidence.id}",
                metadata={
                    "case_id": evidence.case_id,
                    "file_type": evidence.file_type,
                    "status": evidence.status,
                    "ai_labels": evidence.ai_labels_list,
                    "created_at": evidence.created_at.isoformat() if evidence.created_at else None
                }
            ))

        return results

    def _search_events(
        self,
        query: str,
        user_id: str,
        accessible_case_ids: List[str],
        limit: int
    ) -> List[SearchResult]:
        """Search calendar events by title, description"""
        results = []

        # Events owned by user OR linked to accessible cases
        events = self.db.query(CalendarEvent).filter(
            and_(
                or_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.case_id.in_(accessible_case_ids) if accessible_case_ids else False
                ),
                or_(
                    CalendarEvent.title.ilike(f"%{query}%"),
                    CalendarEvent.description.ilike(f"%{query}%"),
                    CalendarEvent.location.ilike(f"%{query}%")
                )
            )
        ).order_by(CalendarEvent.start_time.desc()).limit(limit).all()

        for event in events:
            date_str = event.start_time.strftime("%Y-%m-%d %H:%M") if event.start_time else ""

            results.append(SearchResult(
                category="events",
                id=event.id,
                title=event.title,
                subtitle=f"{date_str} - {event.location or '장소 미정'}",
                icon="calendar",
                url=f"/lawyer/calendar?event={event.id}",
                metadata={
                    "case_id": event.case_id,
                    "event_type": event.event_type.value if event.event_type else None,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "location": event.location
                }
            ))

        return results

    def get_recent_searches(self, user_id: str, limit: int = 5) -> List[dict]:
        """
        Get recent search history for user
        Note: This is a placeholder - actual implementation would store search history

        Args:
            user_id: User ID
            limit: Max results

        Returns:
            List of recent search queries
        """
        # TODO: Implement search history storage
        return []

    def get_quick_access(self, user_id: str) -> dict:
        """
        Get quick access items for the user:
        - Today's deadlines
        - This week's cases

        Args:
            user_id: User ID

        Returns:
            Dict with quick access items
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get accessible case IDs
        accessible_case_ids = self._get_accessible_case_ids(user_id)

        # Today's events
        todays_events = self.db.query(CalendarEvent).filter(
            and_(
                or_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.case_id.in_(accessible_case_ids) if accessible_case_ids else False
                ),
                CalendarEvent.start_time >= today_start,
                CalendarEvent.start_time <= today_end
            )
        ).all()

        return {
            "todays_events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "time": e.start_time.strftime("%H:%M") if e.start_time else "",
                    "case_id": e.case_id
                }
                for e in todays_events
            ],
            "todays_events_count": len(todays_events)
        }
