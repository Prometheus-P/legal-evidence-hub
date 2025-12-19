"""
Security Test Module for LEH Backend
=====================================

This module provides base classes and fixtures for OWASP-compliant security testing.

Test Categories:
- Authentication: Token validation, expiry, tampering
- Authorization: Access control, role-based permissions
- Input Validation: SQL injection, XSS, path traversal

Usage:
    from tests.security.base import SecurityTestBase, AuthenticationTestBase

    class TestUserAuthentication(AuthenticationTestBase):
        endpoint = "/api/auth/login"
        # Tests are inherited automatically
"""
