"""
Unit tests for Case List Service
TDD - Improving test coverage for case_list_service.py
"""

from datetime import datetime, timezone
import uuid

from app.services.case_list_service import CaseListService
from app.db.models import Case, CaseMember, User, CaseStatus, CaseMemberRole
from app.schemas.case_list import (
    CaseFilter,
    SortOrder,
    BulkActionType,
)


class TestCaseListService:
    """Unit tests for CaseListService"""

    def test_get_cases_returns_empty_list_for_new_user(self, test_env):
        """User with no cases gets empty list"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"empty_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Empty User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = CaseListService(db)
        result = service.get_cases(user.id)

        assert result.items == []
        assert result.total == 0

        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_returns_user_cases(self, test_env):
        """User with cases gets their cases"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"with_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Test Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.get_cases(user.id)

        assert result.total == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_with_status_filter(self, test_env):
        """Filter cases by status"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"filter_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        cases = []
        for status in [CaseStatus.ACTIVE, CaseStatus.OPEN]:
            case = Case(
                title=f"Case {status.value}",
                status=status,
                created_by=user.id,
                created_at=now,
                updated_at=now
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            cases.append(case)

            member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
            db.add(member)
            db.commit()

        service = CaseListService(db)
        filters = CaseFilter(status=[CaseStatus.ACTIVE])
        result = service.get_cases(user.id, filters=filters)

        assert result.total == 1

        for case in cases:
            db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
            db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_sort_asc(self, test_env):
        """Sort cases in ascending order (line 83)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"asc_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="ASC Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.get_cases(user.id, sort_order=SortOrder.ASC)

        assert result.total == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_with_client_name_filter(self, test_env):
        """Filter cases by client_name (line 112)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"cn_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Client Filter Case",
            client_name="John Doe Client",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        filters = CaseFilter(client_name="John")
        result = service.get_cases(user.id, filters=filters)

        assert result.total == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_with_search_filter(self, test_env):
        """Filter cases by search term (lines 117-118)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"srch_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Searchable Case Title",
            description="Contains important keyword",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        filters = CaseFilter(search="Searchable")
        result = service.get_cases(user.id, filters=filters)

        assert result.total == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_with_date_filters(self, test_env):
        """Filter cases by date range (lines 127, 130)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from datetime import timedelta

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"date_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Date Range Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        filters = CaseFilter(
            date_from=now - timedelta(days=1),
            date_to=now + timedelta(days=1)
        )
        result = service.get_cases(user.id, filters=filters)

        assert result.total == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_cases_pagination(self, test_env):
        """Pagination works correctly"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"page_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        cases = []
        for i in range(10):
            case = Case(
                title=f"Case {i}",
                status=CaseStatus.ACTIVE,
                created_by=user.id,
                created_at=now,
                updated_at=now
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            cases.append(case)

            member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
            db.add(member)
            db.commit()

        service = CaseListService(db)
        result = service.get_cases(user.id, page=2, page_size=3)

        assert result.total == 10
        assert len(result.items) == 3
        assert result.page == 2

        for case in cases:
            db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
            db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestBulkActions:
    """Unit tests for bulk actions"""

    def test_bulk_action_change_status(self, test_env):
        """Bulk status change works"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"bulk_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Bulk Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.execute_bulk_action(
            user.id,
            [case.id],
            BulkActionType.CHANGE_STATUS,
            {"new_status": "in_progress"}
        )

        assert result.successful == 1
        db.refresh(case)
        assert case.status == CaseStatus.IN_PROGRESS

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_invalid_case(self, test_env):
        """Invalid case returns failure"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"inv_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        service = CaseListService(db)
        result = service.execute_bulk_action(
            user.id,
            ["invalid-id"],
            BulkActionType.REQUEST_AI_ANALYSIS
        )

        assert result.failed == 1

        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_delete(self, test_env):
        """Bulk delete soft deletes case"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"del_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Delete Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.execute_bulk_action(user.id, [case.id], BulkActionType.DELETE)

        assert result.successful == 1
        db.refresh(case)
        assert case.status == CaseStatus.CLOSED

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_export(self, test_env):
        """Bulk export returns success"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"exp_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Export Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.execute_bulk_action(user.id, [case.id], BulkActionType.EXPORT)

        assert result.successful == 1

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestCaseDetail:
    """Unit tests for case detail"""

    def test_get_case_detail_success(self, test_env):
        """Get case detail with access"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"det_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Detail User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Detail Case",
            client_name="Client",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.get_case_detail(user.id, case.id)

        assert result is not None
        assert result.title == "Detail Case"

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_case_detail_no_access(self, test_env):
        """No access returns None"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        other = User(
            email=f"oth_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Other",
            role="lawyer"
        )
        db.add(other)
        db.commit()
        db.refresh(other)

        case = Case(
            title="Private",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.get_case_detail(other.id, case.id)

        assert result is None

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(other)
        db.commit()
        db.close()


class TestEdgeCases:
    """Edge case tests for case_list_service"""

    def test_case_without_updated_at(self, test_env):
        """Case without updated_at has days_since_update=0 (line 158)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"noupd_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="No Update Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=None  # No updated_at
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.get_cases(user.id)

        assert result.total == 1
        # days_since_update should be 0 when updated_at is None
        assert result.items[0].days_since_update == 0

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_exception_handling(self, test_env):
        """Exception during bulk action is caught (lines 246-252)"""
        from app.db.session import get_db
        from app.core.security import hash_password
        from unittest.mock import patch

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"exc_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Exception Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)

        # Patch _execute_single_action to raise exception
        with patch.object(service, '_execute_single_action', side_effect=Exception("Test error")):
            result = service.execute_bulk_action(
                user.id,
                [case.id],
                BulkActionType.CHANGE_STATUS,
                {"new_status": "in_progress"}
            )

        assert result.failed == 1
        assert result.results[0].success is False
        assert "Test error" in result.results[0].error

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_request_ai_analysis(self, test_env):
        """REQUEST_AI_ANALYSIS action succeeds (line 283)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"ai_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="AI Analysis Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.execute_bulk_action(user.id, [case.id], BulkActionType.REQUEST_AI_ANALYSIS)

        assert result.successful == 1
        assert "AI 분석이 요청" in result.results[0].message

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_change_status_missing_param(self, test_env):
        """CHANGE_STATUS without new_status fails (line 292)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"miss_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Missing Param Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        # Call without new_status param
        result = service.execute_bulk_action(
            user.id,
            [case.id],
            BulkActionType.CHANGE_STATUS,
            {}  # Missing new_status
        )

        assert result.failed == 1
        assert "상태가 지정되지 않았습니다" in result.results[0].error

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_change_status_invalid(self, test_env):
        """CHANGE_STATUS with invalid status fails (lines 305-306)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"invst_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Invalid Status Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        result = service.execute_bulk_action(
            user.id,
            [case.id],
            BulkActionType.CHANGE_STATUS,
            {"new_status": "invalid_status_xyz"}
        )

        assert result.failed == 1
        assert "유효하지 않은 상태" in result.results[0].error

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_bulk_action_assign_member_unsupported(self, test_env):
        """ASSIGN_MEMBER action returns unsupported error (line 329)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"unsup_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Unsupported Action Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        member = CaseMember(case_id=case.id, user_id=user.id, role=CaseMemberRole.OWNER)
        db.add(member)
        db.commit()

        service = CaseListService(db)
        # ASSIGN_MEMBER is defined but not implemented in the service
        result = service.execute_bulk_action(user.id, [case.id], BulkActionType.ASSIGN_MEMBER)

        assert result.failed == 1
        assert "지원되지 않는 작업" in result.results[0].error

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_case_with_access_as_member(self, test_env):
        """Member (not owner) can access case (line 355)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"own2_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        member_user = User(
            email=f"mem_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Member",
            role="lawyer"
        )
        db.add(owner)
        db.add(member_user)
        db.commit()
        db.refresh(owner)
        db.refresh(member_user)

        case = Case(
            title="Member Access Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Add both owner and member
        owner_member = CaseMember(case_id=case.id, user_id=owner.id, role=CaseMemberRole.OWNER)
        member_member = CaseMember(case_id=case.id, user_id=member_user.id, role=CaseMemberRole.MEMBER)
        db.add(owner_member)
        db.add(member_member)
        db.commit()

        service = CaseListService(db)
        # Member should be able to get case detail
        result = service.get_case_detail(member_user.id, case.id)

        assert result is not None
        assert result.title == "Member Access Case"

        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(member_user)
        db.commit()
        db.close()
