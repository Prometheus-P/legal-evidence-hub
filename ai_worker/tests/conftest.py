"""
Pytest configuration for AI Worker tests.
Loads environment variables from .env file before tests run.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"\n[conftest] Loaded environment from {env_file}")
else:
    print(f"\n[conftest] Warning: {env_file} not found")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Ensure environment variables are set for all tests.

    Provides test defaults for CI environment where real credentials
    are not needed (all external calls are mocked).
    """
    # Test defaults - used when real env vars are not set
    # These are safe dummy values for CI - all external calls are mocked
    test_defaults = {
        "AWS_REGION": "ap-northeast-2",
        "AWS_ACCESS_KEY_ID": "test-access-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret-key",
        "OPENAI_API_KEY": "test-openai-key",
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_API_KEY": "test-qdrant-key",
        "QDRANT_COLLECTION": "leh_evidence",
        "QDRANT_VECTOR_SIZE": "1536",
        "S3_EVIDENCE_BUCKET": "test-bucket",
        "DDB_EVIDENCE_TABLE": "test-evidence-table",
    }

    # Set defaults for missing env vars
    for key, default_value in test_defaults.items():
        if not os.getenv(key):
            os.environ[key] = default_value

    yield


def pytest_collection_modifyitems(config, items):
    """
    Skip integration tests when required environment variables are missing.
    Unit tests always run.
    """
    # Integration tests require real credentials (not dummy values)
    integration_env_vars = ["QDRANT_URL", "OPENAI_API_KEY"]

    # Check if real credentials exist (not dummy values starting with "test-")
    def has_real_credential(var_name):
        value = os.getenv(var_name)
        if not value:
            return False
        # Dummy values from test_defaults start with "test-" or are localhost URLs
        if value.startswith("test-"):
            return False
        if var_name == "QDRANT_URL" and "localhost" in value:
            return False
        return True

    missing_real_creds = not all(
        has_real_credential(var) for var in integration_env_vars
    )

    if missing_real_creds:
        skip_integration = pytest.mark.skip(
            reason="Integration tests skipped: real credentials not configured"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
