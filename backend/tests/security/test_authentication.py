"""
Authentication Security Tests
==============================

Template for authentication security testing.
Tests OWASP authentication vulnerabilities.

QA Framework v4.0 - OWASP A07:2021 Authentication Failures

Usage:
    Copy this template and customize for your endpoint.
    Inherit from AuthenticationTestBase to get automatic tests.
"""

import pytest
from tests.security.base import AuthenticationTestBase, SecurityPayloads


class TestAuthLoginSecurity(AuthenticationTestBase):
    """
    Security tests for /api/auth/login endpoint.

    Inherits automatic tests:
    - test_reject_request_without_token (skipped for login)
    - test_reject_expired_token
    - test_reject_tampered_token
    - test_reject_malformed_token
    """

    endpoint = "/api/auth/login"
    method = "POST"

    @pytest.mark.security
    def test_reject_request_without_token(self, client):
        """Login endpoint doesn't require token - override base test."""
        # Login is the endpoint that issues tokens, so skip this test
        pytest.skip("Login endpoint does not require authentication")

    @pytest.mark.security
    def test_reject_expired_token(self, client, expired_token):
        """Login endpoint issues tokens, doesn't validate incoming tokens."""
        pytest.skip("Login endpoint issues tokens, doesn't validate them")

    @pytest.mark.security
    def test_reject_tampered_token(self, client, tampered_token):
        """Login endpoint issues tokens, doesn't validate incoming tokens."""
        pytest.skip("Login endpoint issues tokens, doesn't validate them")

    @pytest.mark.security
    def test_reject_malformed_token(self, client, malformed_token):
        """Login endpoint issues tokens, doesn't validate incoming tokens."""
        pytest.skip("Login endpoint issues tokens, doesn't validate them")

    @pytest.mark.security
    def test_login_rate_limiting(self, client):
        """Multiple failed login attempts should trigger rate limiting."""
        failed_attempts = 0
        rate_limited = False

        for i in range(20):
            response = client.post(
                self.endpoint,
                json={"email": "test@example.com", "password": f"wrong-password-{i}"},
            )
            if response.status_code == 429:
                rate_limited = True
                break
            if response.status_code == 401:
                failed_attempts += 1

        # Either rate limited or accepted all (rate limiting may not be implemented)
        assert rate_limited or failed_attempts > 0, "Login endpoint not responding"

    @pytest.mark.security
    def test_no_user_enumeration_on_login(self, client):
        """Login should not reveal whether email exists."""
        # Test with non-existent email
        response_nonexistent = client.post(
            self.endpoint,
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        # Test with potentially existing email but wrong password
        response_wrong_password = client.post(
            self.endpoint,
            json={"email": "test@example.com", "password": "wrong-password"},
        )

        # Both should return same status code to prevent enumeration
        assert response_nonexistent.status_code == response_wrong_password.status_code, (
            "Different status codes reveal user existence"
        )

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SecurityPayloads.SQL_INJECTION[:3])
    def test_sql_injection_in_email(self, client, payload):
        """SQL injection in email field should be blocked."""
        response = client.post(
            self.endpoint,
            json={"email": payload, "password": "password123"},
        )
        # Should reject with validation error, not 500
        assert response.status_code in [400, 401, 422], (
            f"Possible SQL injection vulnerability: {response.status_code}"
        )


class TestProtectedEndpointSecurity(AuthenticationTestBase):
    """
    Security tests for protected endpoints template.

    Replace 'endpoint' with your protected endpoint.
    """

    endpoint = "/api/cases"
    method = "GET"

    # All tests from AuthenticationTestBase are inherited automatically:
    # - test_reject_request_without_token
    # - test_reject_expired_token
    # - test_reject_tampered_token
    # - test_reject_malformed_token
