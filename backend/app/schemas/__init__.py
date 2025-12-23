"""
Pydantic Schemas Module

Request/Response validation schemas

Usage:
    from app.schemas import LoginRequest, UserOut, CaseCreate

모듈 구조:
- auth.py: Login, Signup, User, Token
- user.py: UserInvite, RBAC
- case.py: Case CRUD + Member
- evidence.py: Evidence + Article840
- draft.py: Draft generation
- audit.py: Audit Log
"""

# Auth schemas
from .auth import (
    LoginRequest,
    SignupRequest,
    UserOut,
    TokenResponse,
)

# User management schemas
from .user import (
    UserInviteRequest,
    InviteResponse,
    UserListResponse,
    ResourcePermission,
    RolePermissions,
    RolePermissionsResponse,
    UpdateRolePermissionsRequest,
)

# Case schemas
from .case import (
    CaseCreate,
    CaseUpdate,
    CaseOut,
    CaseSummary,
    CaseMemberPermission,
    CaseMemberAdd,
    CaseMemberOut,
    AddCaseMembersRequest,
    CaseMembersListResponse,
)

# Evidence schemas
from .evidence import (
    Article840Category,
    Article840Tags,
    PresignedUrlRequest,
    PresignedUrlResponse,
    UploadCompleteRequest,
    UploadCompleteResponse,
    EvidenceSummary,
    EvidenceDetail,
)

# Draft schemas
from .draft import (
    DraftPreviewRequest,
    DraftCitation,
    DraftPreviewResponse,
    DraftExportFormat,
)

# Audit schemas
from .audit import (
    AuditAction,
    AuditLogOut,
    AuditLogListRequest,
    AuditLogListResponse,
)

__all__ = [
    # Auth
    "LoginRequest",
    "SignupRequest",
    "UserOut",
    "TokenResponse",
    # User management
    "UserInviteRequest",
    "InviteResponse",
    "UserListResponse",
    "ResourcePermission",
    "RolePermissions",
    "RolePermissionsResponse",
    "UpdateRolePermissionsRequest",
    # Case
    "CaseCreate",
    "CaseUpdate",
    "CaseOut",
    "CaseSummary",
    "CaseMemberPermission",
    "CaseMemberAdd",
    "CaseMemberOut",
    "AddCaseMembersRequest",
    "CaseMembersListResponse",
    # Evidence
    "Article840Category",
    "Article840Tags",
    "PresignedUrlRequest",
    "PresignedUrlResponse",
    "UploadCompleteRequest",
    "UploadCompleteResponse",
    "EvidenceSummary",
    "EvidenceDetail",
    # Draft
    "DraftPreviewRequest",
    "DraftCitation",
    "DraftPreviewResponse",
    "DraftExportFormat",
    # Audit
    "AuditAction",
    "AuditLogOut",
    "AuditLogListRequest",
    "AuditLogListResponse",
]
