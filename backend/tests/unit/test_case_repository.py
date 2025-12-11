"""
Unit tests for Case Repository
TDD - Improving test coverage for case_repository.py
"""

from datetime import datetime, timezone
import uuid

from app.repositories.case_repository import CaseRepository
from app.db.models import Case, User, CaseStatus


class TestUpdate:
    """Unit tests for update method"""

    def test_update_case_success(self, test_env):
        """Successfully updates a case (lines 92-94)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"up_case_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Update User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Original Title",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        repo = CaseRepository(db)

        # Modify the case
        case.title = "Updated Title"
        result = repo.update(case)

        assert result.title == "Updated Title"
        assert result.id == case.id

        # Cleanup
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestSoftDelete:
    """Unit tests for soft_delete method"""

    def test_soft_delete_not_found(self, test_env):
        """Returns False when case not found (line 108)"""
        from app.db.session import get_db

        db = next(get_db())
        repo = CaseRepository(db)

        result = repo.soft_delete("nonexistent-case-id")

        assert result is False
        db.close()

    def test_soft_delete_success(self, test_env):
        """Successfully soft deletes a case"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        user = User(
            email=f"sd_case_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="SoftDelete User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="To Delete Case",
            status=CaseStatus.ACTIVE,
            created_by=user.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        case_id = case.id

        repo = CaseRepository(db)

        result = repo.soft_delete(case_id)

        assert result is True

        # Verify case status is closed
        db.refresh(case)
        assert case.status == "closed"

        # Cleanup
        db.query(Case).filter(Case.id == case_id).delete()
        db.delete(user)
        db.commit()
        db.close()
