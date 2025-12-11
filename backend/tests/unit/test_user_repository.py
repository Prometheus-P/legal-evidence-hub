"""
Unit tests for User Repository
TDD - Improving test coverage for user_repository.py
"""

import uuid

from app.repositories.user_repository import UserRepository
from app.db.models import User, UserStatus


class TestGetAllFilters:
    """Unit tests for get_all method with filters"""

    def test_get_all_filter_by_email(self, test_env):
        """Filter users by email (line 105)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create users with different emails
        user1 = User(
            email=f"filter_john_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="John",
            role="lawyer"
        )
        user2 = User(
            email=f"filter_jane_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Jane",
            role="lawyer"
        )
        db.add(user1)
        db.add(user2)
        db.commit()

        repo = UserRepository(db)

        # Filter by email containing "john"
        result = repo.get_all(email="john")

        # Should include user1
        user_emails = [u.email for u in result]
        assert any("john" in e for e in user_emails)

        # Cleanup
        db.delete(user1)
        db.delete(user2)
        db.commit()
        db.close()

    def test_get_all_filter_by_name(self, test_env):
        """Filter users by name (line 107)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"name_filter_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name=f"UniqueTestName_{unique_id}",
            role="lawyer"
        )
        db.add(user)
        db.commit()

        repo = UserRepository(db)

        # Filter by name
        result = repo.get_all(name=f"UniqueTestName_{unique_id}")

        assert len(result) == 1
        assert result[0].name == f"UniqueTestName_{unique_id}"

        # Cleanup
        db.delete(user)
        db.commit()
        db.close()

    def test_get_all_filter_by_status(self, test_env):
        """Filter users by status (line 111)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create inactive user
        inactive_user = User(
            email=f"inactive_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Inactive User",
            role="lawyer",
            status=UserStatus.INACTIVE
        )
        db.add(inactive_user)
        db.commit()
        db.refresh(inactive_user)

        repo = UserRepository(db)

        # Filter by status
        result = repo.get_all(status=UserStatus.INACTIVE)

        # Should include inactive user
        user_ids = [u.id for u in result]
        assert inactive_user.id in user_ids

        # Cleanup
        db.delete(inactive_user)
        db.commit()
        db.close()
