"""
Investigator List Service
005-lawyer-portal-pages Feature - US3

Business logic for lawyer's investigator management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional
from datetime import datetime, timezone

from app.db.models import User, Case, CaseMember, UserRole, CaseStatus
from app.schemas.investigator_list import (
    InvestigatorFilter,
    InvestigatorItem,
    InvestigatorListResponse,
    InvestigatorDetail,
    InvestigatorStats,
    AssignedCase,
    InvestigatorSortField,
    SortOrder,
    AvailabilityStatus,
)


class InvestigatorListService:
    """Service for lawyer's investigator list operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_investigators(
        self,
        lawyer_id: str,
        filters: Optional[InvestigatorFilter] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: InvestigatorSortField = InvestigatorSortField.NAME,
        sort_order: SortOrder = SortOrder.ASC,
    ) -> InvestigatorListResponse:
        """
        Get paginated list of investigators for a lawyer.

        Investigators are users with role='detective' who are members of cases
        that the lawyer has access to.

        Args:
            lawyer_id: Current lawyer's user ID
            filters: Filter parameters
            page: Page number (1-indexed)
            page_size: Items per page
            sort_by: Field to sort by
            sort_order: Sort direction

        Returns:
            Paginated investigator list response
        """
        # Get cases that the lawyer has access to
        lawyer_case_ids = (
            self.db.query(CaseMember.case_id)
            .filter(CaseMember.user_id == lawyer_id)
            .subquery()
        )

        # Find investigators who are members of these cases
        query = (
            self.db.query(User)
            .join(CaseMember, CaseMember.user_id == User.id)
            .filter(
                User.role == UserRole.DETECTIVE,
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

            if filters.availability and filters.availability != AvailabilityStatus.ALL:
                # Availability is computed based on active assignments
                # We'll filter after fetching for now
                pass

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
        investigators = query.offset(offset).limit(page_size).all()

        # Build response items
        items = []
        for investigator in investigators:
            # Get assignment counts
            assignment_stats = self._get_assignment_stats(investigator.id, lawyer_case_ids)
            availability = self._compute_availability(assignment_stats["active"])

            # Apply availability filter if set
            if filters and filters.availability and filters.availability != AvailabilityStatus.ALL:
                if availability != filters.availability.value:
                    continue

            items.append(
                InvestigatorItem(
                    id=investigator.id,
                    name=investigator.name or "",
                    email=investigator.email,
                    phone=getattr(investigator, 'phone', None),
                    specialization=getattr(investigator, 'specialization', None),
                    active_assignments=assignment_stats["active"],
                    completed_assignments=assignment_stats["completed"],
                    availability=availability,
                    status=investigator.status.value if investigator.status else "active",
                    created_at=investigator.created_at or datetime.now(timezone.utc),
                )
            )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return InvestigatorListResponse(
            items=items,
            total=len(items),  # Adjusted for post-filter
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_investigator_detail(
        self,
        lawyer_id: str,
        investigator_id: str,
    ) -> Optional[InvestigatorDetail]:
        """
        Get detailed information for a specific investigator.

        Args:
            lawyer_id: Current lawyer's user ID
            investigator_id: Investigator's user ID

        Returns:
            InvestigatorDetail or None if not found/unauthorized
        """
        # Verify the investigator exists and is accessible by the lawyer
        lawyer_case_ids = (
            self.db.query(CaseMember.case_id)
            .filter(CaseMember.user_id == lawyer_id)
            .subquery()
        )

        investigator = (
            self.db.query(User)
            .join(CaseMember, CaseMember.user_id == User.id)
            .filter(
                User.id == investigator_id,
                User.role == UserRole.DETECTIVE,
                CaseMember.case_id.in_(lawyer_case_ids)
            )
            .first()
        )

        if not investigator:
            return None

        # Get assigned cases
        assigned_cases = self._get_assigned_cases(investigator_id, lawyer_case_ids)

        # Get stats
        stats = self._get_investigator_stats(investigator_id, lawyer_case_ids)

        # Compute availability
        availability = self._compute_availability(stats.active_assignments)

        return InvestigatorDetail(
            id=investigator.id,
            name=investigator.name or "",
            email=investigator.email,
            phone=getattr(investigator, 'phone', None),
            specialization=getattr(investigator, 'specialization', None),
            availability=availability,
            created_at=investigator.created_at or datetime.now(timezone.utc),
            assigned_cases=assigned_cases,
            stats=stats,
        )

    def _get_sort_column(self, sort_by: InvestigatorSortField):
        """Get SQLAlchemy column for sorting"""
        mapping = {
            InvestigatorSortField.NAME: User.name,
            InvestigatorSortField.CREATED_AT: User.created_at,
            InvestigatorSortField.ACTIVE_ASSIGNMENTS: User.name,  # Computed field
            InvestigatorSortField.COMPLETED_ASSIGNMENTS: User.name,  # Computed field
        }
        return mapping.get(sort_by, User.name)

    def _get_assignment_stats(self, investigator_id: str, lawyer_case_ids) -> dict:
        """Get assignment statistics for an investigator"""
        cases = (
            self.db.query(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .filter(
                CaseMember.user_id == investigator_id,
                Case.id.in_(lawyer_case_ids)
            )
            .all()
        )

        active = sum(
            1 for c in cases
            if c.status in [CaseStatus.ACTIVE, CaseStatus.OPEN, CaseStatus.IN_PROGRESS]
        )
        completed = sum(1 for c in cases if c.status == CaseStatus.CLOSED)

        return {
            "total": len(cases),
            "active": active,
            "completed": completed,
        }

    def _compute_availability(self, active_assignments: int) -> str:
        """Compute availability status based on active assignments"""
        if active_assignments == 0:
            return "available"
        elif active_assignments < 3:
            return "busy"
        else:
            return "unavailable"

    def _get_assigned_cases(self, investigator_id: str, lawyer_case_ids) -> list:
        """Get cases assigned to an investigator"""
        case_members = (
            self.db.query(CaseMember, Case)
            .join(Case, Case.id == CaseMember.case_id)
            .filter(
                CaseMember.user_id == investigator_id,
                Case.id.in_(lawyer_case_ids)
            )
            .all()
        )

        return [
            AssignedCase(
                id=case.id,
                title=case.title or "",
                status=case.status.value if case.status else "active",
                role=member.role.value if member.role else "member",
                client_name=case.client_name,
                assigned_at=member.created_at or datetime.now(timezone.utc),
                last_updated=case.updated_at or datetime.now(timezone.utc),
            )
            for member, case in case_members
        ]

    def _get_investigator_stats(self, investigator_id: str, lawyer_case_ids) -> InvestigatorStats:
        """Get statistics for an investigator"""
        cases = (
            self.db.query(Case)
            .join(CaseMember, CaseMember.case_id == Case.id)
            .filter(
                CaseMember.user_id == investigator_id,
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

        return InvestigatorStats(
            total_assignments=total,
            active_assignments=active,
            completed_assignments=completed,
            total_evidence_collected=0,  # Would need evidence query
            average_response_time_hours=None,
        )
