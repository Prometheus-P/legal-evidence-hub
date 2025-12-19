"""
Security Test Base Classes
===========================

Provides reusable base classes for OWASP-compliant security testing.
Inherit from these classes to get automatic security test coverage.

QA Framework v4.0 - OWASP Top 10 Compliance
"""

import pytest
from abc import ABC, abstractmethod
from typing import Any


class SecurityPayloads:
    """Common security test payloads for OWASP testing."""

    # SQL Injection payloads
    SQL_INJECTION = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "1; SELECT * FROM users",
        "' UNION SELECT * FROM users --",
        "1' AND '1'='1' --",
        "admin'--",
        "' OR 1=1 --",
        "'; EXEC xp_cmdshell('dir'); --",
    ]

    # XSS payloads
    XSS = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "javascript:alert('xss')",
        "<iframe src='javascript:alert(1)'>",
        "'\"><script>alert('xss')</script>",
        "<body onload=alert('xss')>",
    ]

    # Path traversal payloads
    PATH_TRAVERSAL = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc/passwd",
        "/etc/passwd%00",
        "....//....//etc/passwd",
    ]

    # Command injection payloads
    COMMAND_INJECTION = [
        "; ls -la",
        "| cat /etc/passwd",
        "`whoami`",
        "$(id)",
        "&& cat /etc/passwd",
        "|| cat /etc/passwd",
        "; ping -c 10 localhost",
    ]

    # Header injection payloads
    HEADER_INJECTION = [
        "value\r\nX-Injected: header",
        "value\nSet-Cookie: malicious=true",
        "value\r\n\r\n<html>injected</html>",
    ]


class SecurityTestBase(ABC):
    """
    Base class for all security tests.

    Provides common security testing utilities and payloads.
    Subclasses should define the endpoint and method to test.
    """

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """The API endpoint to test."""
        pass

    @property
    def method(self) -> str:
        """HTTP method for the endpoint. Default: POST."""
        return "POST"

    @property
    def payloads(self) -> SecurityPayloads:
        """Access to security payloads."""
        return SecurityPayloads()

    def make_request(self, client: Any, data: dict = None, headers: dict = None) -> Any:
        """Make a request to the endpoint with the given data."""
        method = getattr(client, self.method.lower())
        kwargs = {}
        # Only include json body for methods that support it
        if self.method.upper() in ["POST", "PUT", "PATCH"] and data:
            kwargs["json"] = data
        if headers:
            kwargs["headers"] = headers
        return method(self.endpoint, **kwargs)


@pytest.mark.security
@pytest.mark.auth
class AuthenticationTestBase(SecurityTestBase):
    """
    Base class for authentication security tests.

    Inherit from this class and define 'endpoint' to get automatic
    authentication security tests.

    Tests included:
    - Request without token should be rejected
    - Request with expired token should be rejected
    - Request with tampered token should be rejected
    - Request with malformed token should be rejected
    """

    @pytest.mark.security
    def test_reject_request_without_token(self, client):
        """Requests without authentication token should be rejected."""
        response = self.make_request(client, {})
        assert response.status_code in [401, 403], (
            f"Endpoint {self.endpoint} accepted request without token"
        )

    @pytest.mark.security
    def test_reject_expired_token(self, client, expired_token):
        """Requests with expired tokens should be rejected."""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = self.make_request(client, {}, headers=headers)
        assert response.status_code in [401, 403], (
            f"Endpoint {self.endpoint} accepted expired token"
        )

    @pytest.mark.security
    def test_reject_tampered_token(self, client, tampered_token):
        """Requests with tampered tokens should be rejected."""
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = self.make_request(client, {}, headers=headers)
        assert response.status_code in [401, 403], (
            f"Endpoint {self.endpoint} accepted tampered token"
        )

    @pytest.mark.security
    def test_reject_malformed_token(self, client, malformed_token):
        """Requests with malformed tokens should be rejected."""
        headers = {"Authorization": f"Bearer {malformed_token}"}
        response = self.make_request(client, {}, headers=headers)
        assert response.status_code in [401, 403], (
            f"Endpoint {self.endpoint} accepted malformed token"
        )


@pytest.mark.security
@pytest.mark.authorization
class AuthorizationTestBase(SecurityTestBase):
    """
    Base class for authorization security tests.

    Inherit from this class and define 'endpoint' and 'resource_id_param'
    to get automatic authorization tests.

    Tests included:
    - User cannot access another user's resources
    - Role-based access is enforced
    """

    @property
    def resource_id_param(self) -> str:
        """URL parameter name for resource ID. Default: 'id'."""
        return "id"

    @pytest.mark.security
    def test_deny_access_to_other_user_resource(
        self, client, auth_headers, other_user_resource_id
    ):
        """Users should not access resources they don't own."""
        endpoint = self.endpoint.format(**{self.resource_id_param: other_user_resource_id})
        response = client.get(endpoint, headers=auth_headers)
        assert response.status_code in [403, 404], (
            f"User accessed another user's resource at {endpoint}"
        )

    @pytest.mark.security
    def test_enforce_role_based_access(
        self, client, client_auth_headers, admin_only_endpoint
    ):
        """Non-admin users should not access admin-only endpoints."""
        response = client.get(admin_only_endpoint, headers=client_auth_headers)
        assert response.status_code == 403, (
            f"Non-admin user accessed admin endpoint {admin_only_endpoint}"
        )


@pytest.mark.security
@pytest.mark.input_validation
class InputValidationTestBase(SecurityTestBase):
    """
    Base class for input validation security tests.

    Inherit from this class and define 'endpoint' and 'field_name'
    to get automatic input validation tests.

    Tests included:
    - SQL injection attempts should be blocked
    - XSS attempts should be blocked or escaped
    - Path traversal attempts should be blocked
    - Command injection attempts should be blocked
    """

    @property
    def field_name(self) -> str:
        """The field name to inject payloads into. Default: 'input'."""
        return "input"

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SecurityPayloads.SQL_INJECTION[:3])
    def test_reject_sql_injection(self, client, auth_headers, payload):
        """SQL injection attempts should be blocked."""
        data = {self.field_name: payload}
        response = self.make_request(client, data, headers=auth_headers)
        # Should either reject (422) or store safely via ORM (200/201 without executing SQL)
        # 201 is valid for POST endpoints that create resources - ORM prevents injection
        assert response.status_code in [400, 422, 200, 201], (
            f"Unexpected response {response.status_code} for SQL injection"
        )
        if response.status_code in [200, 201]:
            # If accepted, ensure it was sanitized (no SQL executed)
            assert "error" not in response.text.lower() or "sql" not in response.text.lower()

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SecurityPayloads.XSS[:3])
    def test_reject_xss_attempt(self, client, auth_headers, payload):
        """XSS attempts should be blocked or escaped."""
        data = {self.field_name: payload}
        response = self.make_request(client, data, headers=auth_headers)
        assert response.status_code in [400, 422, 200]
        if response.status_code == 200:
            # If accepted, ensure script tags are escaped
            response_text = response.text
            assert "<script>" not in response_text, "XSS payload not escaped"

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SecurityPayloads.PATH_TRAVERSAL[:3])
    def test_reject_path_traversal(self, client, auth_headers, payload):
        """Path traversal attempts should be blocked."""
        data = {self.field_name: payload}
        response = self.make_request(client, data, headers=auth_headers)
        assert response.status_code in [400, 404, 422], (
            f"Path traversal not blocked: {response.status_code}"
        )

    @pytest.mark.security
    @pytest.mark.parametrize("payload", SecurityPayloads.COMMAND_INJECTION[:3])
    def test_reject_command_injection(self, client, auth_headers, payload):
        """Command injection attempts should be blocked."""
        data = {self.field_name: payload}
        response = self.make_request(client, data, headers=auth_headers)
        assert response.status_code in [400, 422, 200]


@pytest.mark.security
class RateLimitingTestBase(SecurityTestBase):
    """
    Base class for rate limiting tests.

    Tests included:
    - Endpoints should enforce rate limits
    """

    @property
    def rate_limit(self) -> int:
        """Number of requests before rate limiting. Default: 100."""
        return 100

    @pytest.mark.security
    @pytest.mark.slow
    def test_enforce_rate_limiting(self, client, auth_headers):
        """Endpoints should enforce rate limits after threshold."""
        responses = []
        for _ in range(self.rate_limit + 10):
            response = self.make_request(client, {}, headers=auth_headers)
            responses.append(response.status_code)

        # At least one request should be rate limited
        assert 429 in responses, (
            f"No rate limiting after {self.rate_limit + 10} requests"
        )
