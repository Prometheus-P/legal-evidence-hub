"""
Client List Service
005-lawyer-portal-pages Feature - US2

Business logic for lawyer's client management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional
from datetime import datetime, timezone

from app.db.models import User, Case, CaseMember, UserRole, UserStatus, CaseStatus
from app.schemas.client_list import (
    ClientFilter,
    ClientItem,
    ClientListResponse,
    ClientDetail,
    ClientStats,
    LinkedCase,
    ActivityItem,
    ClientSortField,
    SortOrder,
    ClientStatus as ClientStatusFilter,
)


class ClientListService:
    """Service for lawyer's client list operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_clients(
        self,
        lawyer_id: str,
        filters: Optional[ClientFilter] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: ClientSortField = ClientSortField.NAME,
        sort_order: SortOrder = SortOrder.ASC,
    ) -> ClientListResponse:
        """
        Get paginated list of clients for a lawyer.

        Clients are users with role='client' who are members of cases
        that the lawyer has access to.

        Args:
            lawyer_id: Current lawyer's user ID
            filters: Filter parameters
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Field to sort by
            sort_order: Sort direction

        Returns:
            Paginated client list response
        """
        # Get cases that the lawyer has access to
        lawyer_case_ids = (
            self.db.query(CaseMember.case_id)
            .filter(CaseMember.user_id == lawyer_id)
            .subquery()
        )

        # Find clients who are members of these cases
        # A client is a user with role='client' who is a member of a case
        query = (
            self.db.query(User)
            .join(CaseMember, CaseMember.user_id == User.id)
            .filter(
                User.role == UserRole.CLIENT,
                CaseMember.case_id.in_(lawyer_case_ids)
            )
            .distinct()
        )

        # Apply filters
        if filters:
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )

            if filters.status and filters.status != ClientStatusFilter.ALL:
                if filters.status == ClientStatusFilter.ACTIVE:
                    query = query.filter(User.status == UserStatus.ACTIVE)
                elif filters.status == ClientStatusFilter.INACTIVE:
                    query = query.filter(User.status == UserStatus.INACTIVE)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Apply pagination
        offset = (page - 1) * page_size
        clients = query.offset(offset).limit(page_size).all()

        # Build response items
        items = []
        for client in clients:
            # Get case counts for this client
            case_stats = self._get_client_case_stats(client.id, lawyer_case_ids)

            items.append(
                ClientItem(
                    id=client.id,
                    name=client.name or "",
                    email=client.email,
                    phone=getattr(client, 'phone', None),
                    case_count=case_stats["total"],
                    active_cases=case_stats["active"],
                    last_activity=case_stats.get("last_activity"),
                    status=client.status.value if client.status else "active",
                    created_at=client.created_at or datetime.now(timezone.utc),
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return ClientListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_client_detail(
        self,
        lawyer_id: str,
        client_id: str,
    ) -> Optional[ClientDetail]:
        """
        Get detailed information for a specific client.

        Args:
            lawyer_id: Current lawyer's user ID
            client_id: Client's user ID

        Returns:
            ClientDetail or None if not found/unauthorized
        """
        # Verify the client exists and is accessible by the lawyer
        lawyer_case_ids = (
            self.db.query(CaseMember.case_id)
            .filter(CaseMember.user_id == lawyer_id)
            .subquery()
        )

        client = (
            self.db.query(User)
            .join(CaseMember, CaseMember.user_id == User.id)
            .filter(
                User.id == client_id,
                User.role == UserRole.CLIENT,
                CaseMember.case_id.in_(lawyer_case_ids)
            )
            .first()
        )

        if not client:
            return None

        # Get linked cases
        linked_cases = self._get_linked_cases(client_id, lawyer_case_ids)

        # Get client stats
        stats = self._get_client_stats(client_id, lawyer_case_ids)

        # Get recent activity (simplified - just case updates)
        recent_activity = self._get_recent_activity(client_id, lawyer_case_ids)

        return ClientDetail(
            id=client.id,
            name=client.name or "",
            email=client.email,
            phone=getattr(client, 'phone', None),
            created_at=client.created_at or datetime.now(timezone.utc),
            linked_cases=linked_cases,
            recent_activity=recent_activity,
            stats=stats,
        )

    def _get_sort_column(self, sort_by: ClientSortField):
        """Get SQLAlchemy column for sorting"""
        mapping = {
            ClientSortField.NAME: User.name,
            ClientSortField.CREATED_AT: User.created_at,
            ClientSortField.CASE_COUNT: User.name,  # Default to name (computed field)
            ClientSortField.LAST_ACTIVITY: User.created_at,  # Use created_at (User has no updated_at)
        }
        return mapping.get(sort_by, User.name)

    def _get_client_case_stats(self, client_id: str, lawyer_case_ids) -> dict:
        """Get case statistics for a client"""
        cases = (
            self.db.query(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .filter(
                CaseMember.user_id == client_id,
                Case.id.in_(lawyer_case_ids)
            )
            .all()
        )

        total = len(cases)
        active = sum(
            1 for c in cases
            if c.status in [CaseStatus.ACTIVE, CaseStatus.OPEN, CaseStatus.IN_PROGRESS]
        )

        last_activity = None
        if cases:
            latest_case = max(cases, key=lambda c: c.updated_at or c.created_at)
            last_activity = latest_case.updated_at or latest_case.created_at

        return {
            "total": total,
            "active": active,
            "last_activity": last_activity,
        }

    def _get_linked_cases(self, client_id: str, lawyer_case_ids) -> list:
        """Get cases linked to a client"""
        case_members = (
            self.db.query(CaseMember, Case)
            .join(Case, Case.id == CaseMember.case_id)
            .filter(
                CaseMember.user_id == client_id,
                Case.id.in_(lawyer_case_ids)
            )
            .all()
        )

        return [
            LinkedCase(
                id=case.id,
                title=case.title or "",
                status=case.status.value if case.status else "active",
                role=member.role.value if member.role else "member",
                created_at=case.created_at or datetime.now(timezone.utc),
                updated_at=case.updated_at or datetime.now(timezone.utc),
            )
            for member, case in case_members
        ]

    def _get_client_stats(self, client_id: str, lawyer_case_ids) -> ClientStats:
        """Get statistics for a client"""
        cases = (
            self.db.query(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .filter(
                CaseMember.user_id == client_id,
                Case.id.in_(lawyer_case_ids)
            )
            .all()
        )

        total = len(cases)
        active = sum(
            1 for c in cases
            if c.status in [CaseStatus.ACTIVE, CaseStatus.OPEN, CaseStatus.IN_PROGRESS]
        )
        completed = sum(1 for c in cases if c.status == CaseStatus.CLOSED)

        return ClientStats(
            total_cases=total,
            active_cases=active,
            completed_cases=completed,
            total_evidence=0,  # Would need evidence query
            total_messages=0,  # Would need messages query
        )

    def _get_recent_activity(self, client_id: str, lawyer_case_ids) -> list:
        """Get recent activity for a client"""
        # Simplified: return recent case updates
        cases = (
            self.db.query(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .filter(
                CaseMember.user_id == client_id,
                Case.id.in_(lawyer_case_ids)
            )
            .order_by(desc(Case.updated_at))
            .limit(5)
            .all()
        )

        return [
            ActivityItem(
                type="case_update",
                case_id=case.id,
                description=f"케이스 '{case.title}' 업데이트",
                timestamp=case.updated_at or datetime.now(timezone.utc),
            )
            for case in cases
        ]
