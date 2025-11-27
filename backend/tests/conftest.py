"""
Pytest configuration and shared fixtures for LEH Backend tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os
from pathlib import Path


def pytest_configure(config):
    """
    Configure environment for pytest.

    In CI environment (TESTING=true):
      - Set test-specific environment variables if not already set
      - These must be set BEFORE any app modules are imported

    In local environment:
      - Load .env file for integration tests
    """
    # CI environment: set test defaults if not already set
    if os.environ.get("TESTING") == "true":
        # These defaults are used in CI when env vars are not explicitly set
        # DATABASE_URL should be set by CI workflow, but provide fallback
        defaults = {
            "APP_ENV": "local",
            "APP_DEBUG": "true",
            "JWT_SECRET": "test-secret-key-for-ci-pipeline-32chars",
            "S3_EVIDENCE_BUCKET": "test-bucket",
            "DDB_EVIDENCE_TABLE": "test-evidence-table",
            "QDRANT_HOST": "",  # Empty = in-memory mode for tests
            "OPENAI_API_KEY": "test-openai-key",
        }
        for key, value in defaults.items():
            if not os.environ.get(key):
                os.environ[key] = value
        return

    # Local environment: load .env file
    # Skip if DATABASE_URL is already set (indicates pre-configured env)
    if os.environ.get("DATABASE_URL"):
        return

    # Load .env from backend directory for local integration tests
    from dotenv import load_dotenv
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)


@pytest.fixture(scope="session")
def test_env():
    """
    Set up test environment variables

    Respects CI environment variables if already set (e.g., DATABASE_URL from GitHub Actions)
    """
    # Default test values - only used if not already set in environment
    defaults = {
        "APP_ENV": "local",
        "APP_DEBUG": "true",
        "JWT_SECRET": "test-secret-key-do-not-use-in-production",
        "DATABASE_URL": "postgresql://test_user:test_pass@localhost:5432/test_db",
        "S3_EVIDENCE_BUCKET": "test-bucket",
        "DDB_EVIDENCE_TABLE": "test-evidence-table",
        "QDRANT_HOST": "",  # Empty = in-memory mode for tests
        "OPENAI_API_KEY": "test-openai-key",
    }

    # Store original env vars and set defaults only if not already set
    original_env = {}
    test_env_vars = {}
    for key, default_value in defaults.items():
        original_env[key] = os.environ.get(key)
        # Use existing env var if set, otherwise use default
        if os.environ.get(key):
            test_env_vars[key] = os.environ[key]
        else:
            os.environ[key] = default_value
            test_env_vars[key] = default_value

    yield test_env_vars

    # Restore original env vars
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture(scope="function")
def client(test_env):
    """
    FastAPI TestClient fixture

    Creates a fresh TestClient for each test function.
    Automatically uses test environment variables.
    """
    # Import here to ensure test_env is loaded first
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def mock_settings(test_env):
    """
    Mock settings object for unit tests

    Returns a settings object with test values.
    """
    from app.core.config import Settings

    settings = Settings(**test_env)
    return settings


@pytest.fixture(scope="function")
def mock_db_session():
    """
    Mock database session

    Use this for testing database operations without real DB.
    """
    session = Mock()
    yield session
    session.close()


@pytest.fixture(scope="function")
def mock_s3_client():
    """
    Mock boto3 S3 client
    """
    with patch('boto3.client') as mock_boto3:
        mock_client = Mock()
        mock_boto3.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def mock_dynamodb_client():
    """
    Mock boto3 DynamoDB client
    """
    with patch('boto3.resource') as mock_boto3:
        mock_resource = Mock()
        mock_boto3.return_value = mock_resource
        yield mock_resource


@pytest.fixture(scope="function")
def mock_qdrant_client():
    """
    Mock Qdrant client
    """
    with patch('qdrant_client.QdrantClient') as mock_qdrant:
        mock_client = Mock()
        mock_qdrant.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="function")
def mock_openai_client():
    """
    Mock OpenAI client
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_case_data():
    """
    Sample case data for testing
    """
    return {
        "id": "case_123",
        "title": "김○○ 이혼 사건",
        "description": "테스트 사건",
        "status": "active",
        "created_by": "user_456"
    }


@pytest.fixture
def sample_evidence_data():
    """
    Sample evidence metadata for testing
    """
    return {
        "case_id": "case_123",
        "evidence_id": "ev_001",
        "type": "text",
        "timestamp": "2024-12-25T10:20:00Z",
        "speaker": "원고",
        "labels": ["폭언", "계속적 불화"],
        "ai_summary": "피고가 고성을 지르며 폭언함",
        "content": "테스트 증거 내용",
        "s3_key": "cases/case_123/raw/test.txt",
        "status": "done"
    }


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing
    """
    return {
        "id": "user_456",
        "email": "test@example.com",
        "name": "테스트 사용자",
        "role": "lawyer"
    }


@pytest.fixture
def test_user(test_env):
    """
    Create a real user in the database for authentication tests

    Password: correct_password123
    """
    from app.db.session import get_db, init_db
    from app.db.models import User
    from app.core.security import hash_password
    from sqlalchemy.orm import Session

    # Initialize database
    init_db()

    # Create user
    db: Session = next(get_db())
    try:
        user = User(
            email="test@example.com",
            hashed_password=hash_password("correct_password123"),
            name="테스트 사용자",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        yield user

        # Cleanup - delete in correct order to respect foreign keys
        # Delete case_members first
        from app.db.models import Case, CaseMember, InviteToken
        db.query(InviteToken).filter(InviteToken.created_by == user.id).delete()
        db.query(CaseMember).filter(CaseMember.user_id == user.id).delete()
        # Delete cases created by user
        db.query(Case).filter(Case.created_by == user.id).delete()
        # Delete user
        db.delete(user)
        db.commit()
    finally:
        db.close()
        # Note: Tables are NOT dropped to allow other fixtures/tests to reuse the schema


@pytest.fixture
def auth_headers(test_user):
    """
    Generate authentication headers with JWT token for test_user

    Returns:
        dict: Headers with Authorization Bearer token
    """
    from app.core.security import create_access_token

    # Create JWT token for test user
    token = create_access_token(data={"sub": test_user.id, "role": test_user.role})

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def admin_user(test_env):
    """
    Create admin user in the database for admin tests

    Password: admin_password123
    """
    from app.db.session import get_db, init_db
    from app.db.models import User
    from app.core.security import hash_password
    from sqlalchemy.orm import Session

    # Initialize database
    init_db()

    # Create admin user
    db: Session = next(get_db())
    try:
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("admin_password123"),
            name="Admin User",
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        yield admin

        # Cleanup
        from app.db.models import Case, CaseMember, InviteToken
        # Delete invite tokens created by admin
        db.query(InviteToken).filter(InviteToken.created_by == admin.id).delete()
        # Delete case_members
        db.query(CaseMember).filter(CaseMember.user_id == admin.id).delete()
        # Delete cases
        db.query(Case).filter(Case.created_by == admin.id).delete()
        # Delete admin user
        db.delete(admin)
        db.commit()
    finally:
        db.close()
        # Note: Tables are NOT dropped to allow other fixtures/tests to reuse the schema


@pytest.fixture
def admin_auth_headers(admin_user):
    """
    Generate authentication headers with JWT token for admin_user

    Returns:
        dict: Headers with Authorization Bearer token
    """
    from app.core.security import create_access_token

    # Create JWT token for admin user
    token = create_access_token(data={"sub": admin_user.id, "role": admin_user.role})

    return {
        "Authorization": f"Bearer {token}"
    }
