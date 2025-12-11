"""
Unit tests for Case Member Repository
TDD - Improving test coverage for case_member_repository.py
"""

from datetime import datetime, timezone
import uuid

from app.repositories.case_member_repository import CaseMemberRepository
from app.db.models import Case, CaseMember, User, CaseStatus, CaseMemberRole


class TestRemoveMember:
    """Unit tests for remove_member method"""

    def test_remove_member_success(self, test_env):
        """Successfully removes a member (lines 84-90)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        # Create owner
        owner = User(
            email=f"rm_own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        # Create user to be removed
        member_user = User(
            email=f"rm_mem_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Member",
            role="lawyer"
        )
        db.add(member_user)
        db.commit()
        db.refresh(member_user)

        # Create case
        case = Case(
            title="Remove Test Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Add owner as owner
        owner_member = CaseMember(
            case_id=case.id,
            user_id=owner.id,
            role=CaseMemberRole.OWNER
        )
        db.add(owner_member)
        # Add user as member
        member = CaseMember(
            case_id=case.id,
            user_id=member_user.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(member)
        db.commit()

        repo = CaseMemberRepository(db)

        # Remove the member
        result = repo.remove_member(case.id, member_user.id)

        assert result is True

        # Verify member is removed
        remaining = db.query(CaseMember).filter(
            CaseMember.case_id == case.id,
            CaseMember.user_id == member_user.id
        ).first()
        assert remaining is None

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(member_user)
        db.commit()
        db.close()

    def test_remove_member_not_found(self, test_env):
        """Returns False when member not found (line 86)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"rmf_own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        case = Case(
            title="Not Found Test Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        repo = CaseMemberRepository(db)

        # Try to remove non-existent member
        result = repo.remove_member(case.id, "nonexistent-user-id")

        assert result is False

        # Cleanup
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.commit()
        db.close()


class TestAddMembersBatch:
    """Unit tests for add_members_batch method"""

    def test_add_members_batch_update_role(self, test_env):
        """Updates role when member already exists with different role (lines 145-147)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"amb_own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        member_user = User(
            email=f"amb_mem_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Member",
            role="lawyer"
        )
        db.add(member_user)
        db.commit()
        db.refresh(member_user)

        case = Case(
            title="Update Role Test Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Add user as MEMBER initially
        existing_member = CaseMember(
            case_id=case.id,
            user_id=member_user.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(existing_member)
        db.commit()
        db.refresh(existing_member)

        repo = CaseMemberRepository(db)

        # Now batch add with different role (VIEWER)
        result = repo.add_members_batch(
            case.id,
            [(member_user.id, CaseMemberRole.VIEWER)]
        )

        assert len(result) == 1

        # Verify role was updated
        db.refresh(existing_member)
        assert existing_member.role == CaseMemberRole.VIEWER

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(member_user)
        db.commit()
        db.close()

    def test_add_members_batch_same_role(self, test_env):
        """Does not update when member exists with same role (line 145 - condition false)"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]
        now = datetime.now(timezone.utc)

        owner = User(
            email=f"ambs_own_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Owner",
            role="lawyer"
        )
        db.add(owner)
        db.commit()
        db.refresh(owner)

        member_user = User(
            email=f"ambs_mem_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Member",
            role="lawyer"
        )
        db.add(member_user)
        db.commit()
        db.refresh(member_user)

        case = Case(
            title="Same Role Test Case",
            status=CaseStatus.ACTIVE,
            created_by=owner.id,
            created_at=now,
            updated_at=now
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Add user as MEMBER initially
        existing_member = CaseMember(
            case_id=case.id,
            user_id=member_user.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(existing_member)
        db.commit()

        repo = CaseMemberRepository(db)

        # Batch add with same role (MEMBER)
        result = repo.add_members_batch(
            case.id,
            [(member_user.id, CaseMemberRole.MEMBER)]
        )

        assert len(result) == 1

        # Role should still be MEMBER
        db.refresh(existing_member)
        assert existing_member.role == CaseMemberRole.MEMBER

        # Cleanup
        db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(owner)
        db.delete(member_user)
        db.commit()
        db.close()
