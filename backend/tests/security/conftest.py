"""
Security Test Fixtures
======================

Provides fixtures for security testing including invalid tokens,
security payloads, and test resources.

QA Framework v4.0
"""

import pytest
import jwt
from datetime import datetime, timedelta
from typing import Dict, List


@pytest.fixture
def expired_token() -> str:
    """
    Generate a JWT token that has already expired.

    Returns:
        str: An expired JWT token
    """
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "lawyer",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        "iat": datetime.utcnow() - timedelta(hours=2),
    }
    # Use the test secret key
    return jwt.encode(payload, "test-secret-key-that-is-at-least-32-chars-long", algorithm="HS256")


@pytest.fixture
def tampered_token() -> str:
    """
    Generate a JWT token with a tampered signature.

    Returns:
        str: A JWT token with invalid signature
    """
    payload = {
        "sub": "test-user-id",
        "email": "test@example.com",
        "role": "admin",  # Elevated role attempt
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    # Sign with a different key
    token = jwt.encode(payload, "wrong-secret-key-that-is-at-least-32-chars", algorithm="HS256")
    return token


@pytest.fixture
def malformed_token() -> str:
    """
    Generate a malformed JWT token.

    Returns:
        str: A malformed token string
    """
    return "not.a.valid.jwt.token.at.all"


@pytest.fixture
def security_payloads() -> Dict[str, List[str]]:
    """
    Provide common security test payloads.

    Returns:
        Dict containing SQL injection, XSS, path traversal, and command injection payloads
    """
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users",
            "' UNION SELECT * FROM users --",
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "javascript:alert('xss')",
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(id)",
        ],
    }


@pytest.fixture
def other_user_resource_id() -> str:
    """
    Provide a resource ID belonging to another user.

    Used for testing unauthorized access attempts.

    Returns:
        str: A UUID of a resource owned by a different user
    """
    return "00000000-0000-0000-0000-000000000999"


@pytest.fixture
def admin_only_endpoint() -> str:
    """
    Provide an admin-only endpoint for testing role-based access.

    Returns:
        str: An endpoint that requires admin role
    """
    return "/api/admin/users"


@pytest.fixture
def sensitive_endpoints() -> List[str]:
    """
    List of endpoints that handle sensitive data.

    These should have enhanced security testing.

    Returns:
        List[str]: Endpoints handling sensitive information
    """
    return [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/reset-password",
        "/api/users/me",
        "/api/cases",
        "/api/evidence",
    ]
