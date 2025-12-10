"""
Legal Evidence Hub (LEH) - Middleware Package
"""

from .error_handler import (
    LEHException,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ConflictError,
    ValidationError,
    register_exception_handlers
)
from .security import SecurityHeadersMiddleware, HTTPSRedirectMiddleware
from .audit_log import AuditLogMiddleware
from .case_permission import (
    CasePermissionChecker,
    get_permission_checker,
    require_case_access,
    require_case_write_access,
    require_case_owner,
    require_case_access_or_admin,
    require_case_write_or_admin,
    require_case_owner_or_admin
)

__all__ = [
    "LEHException",
    "AuthenticationError",
    "PermissionError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "register_exception_handlers",
    "SecurityHeadersMiddleware",
    "HTTPSRedirectMiddleware",
    "AuditLogMiddleware",
    # Case permission utilities
    "CasePermissionChecker",
    "get_permission_checker",
    "require_case_access",
    "require_case_write_access",
    "require_case_owner",
    "require_case_access_or_admin",
    "require_case_write_or_admin",
    "require_case_owner_or_admin"
]
