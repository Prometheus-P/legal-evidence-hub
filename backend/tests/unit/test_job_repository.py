"""
Unit tests for Job Repository
TDD - Improving test coverage for job_repository.py
"""

import uuid

from app.repositories.job_repository import JobRepository
from app.db.models import JobStatus, JobType, User, Case, CaseStatus


class TestJobRepositoryInit:
    """Unit tests for JobRepository __init__ method (line 17)"""

    def test_init_creates_repository(self, test_env):
        """Instantiating JobRepository stores db session"""
        from app.db.session import get_db

        db = next(get_db())

        repo = JobRepository(db)

        assert repo.db == db

        db.close()


class TestCreate:
    """Unit tests for create method (lines 28-39)"""

    def test_create_job_success(self, test_env):
        """Successfully creates a job in database"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create required user and case
        user = User(
            email=f"jobrepo_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Job Repo User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title=f"Job Repo Case {unique_id}",
            status=CaseStatus.ACTIVE,
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        repo = JobRepository(db)

        job = repo.create(
            case_id=case.id,
            user_id=user.id,
            job_type=JobType.OCR
        )

        assert job.id is not None
        assert job.case_id == case.id
        assert job.user_id == user.id
        assert job.job_type == JobType.OCR
        assert job.status == JobStatus.QUEUED

        # Cleanup
        db.delete(job)
        db.delete(case)
        db.delete(user)
        db.commit()
        db.close()


class TestGetById:
    """Unit tests for get_by_id method (lines 43, 53-60)"""

    def test_get_by_id_success(self, test_env):
        """Returns job when found"""
        from app.db.session import get_db
        from app.core.security import hash_password

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"getjob_{unique_id}@test.com",
            hashed_password=hash_password("pass"),
            name="Get Job User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title=f"Get Job Case {unique_id}",
            status=CaseStatus.ACTIVE,
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        repo = JobRepository(db)
        created_job = repo.create(case_id=case.id, user_id=user.id, job_type=JobType.OCR)

        result = repo.get_by_id(created_job.id)

        assert result is not None
        assert result.id == created_job.id

        # Cleanup
        db.delete(created_job)
        db.delete(case)
        db.delete(user)
        db.commit()
        db.close()

    def test_get_by_id_not_found(self, test_env):
        """Returns None when job not found"""
        from app.db.session import get_db

        db = next(get_db())
        repo = JobRepository(db)

        result = repo.get_by_id("nonexistent-job-id")

        assert result is None

        db.close()
