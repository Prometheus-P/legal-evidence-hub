"""
Pydantic schemas (DTOs) for request/response validation
Separated from SQLAlchemy models per BACKEND_SERVICE_REPOSITORY_GUIDE.md

This module re-exports all schemas from domain-specific modules for backward compatibility.
Import from this module or directly from submodules:
    from app.db.schemas import LoginRequest  # Legacy
    from app.db.schemas.auth import LoginRequest  # Preferred
"""

# Auth & User Management
from app.db.schemas.auth import (
    LoginRequest,
    SignupRequest,
    UserOut,
    TokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    UserInviteRequest,
    InviteResponse,
    UserListResponse,
    ResourcePermission,
    RolePermissions,
    RolePermissionsResponse,
    UpdateRolePermissionsRequest,
)

# Case
from app.db.schemas.case import (
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

# Evidence
from app.db.schemas.evidence import (
    Article840Category,
    Article840Tags,
    PresignedUrlRequest,
    PresignedUrlResponse,
    ExifMetadataInput,
    UploadCompleteRequest,
    UploadCompleteResponse,
    EvidenceSummary,
    EvidenceListResponse,
    EvidenceReviewRequest,
    EvidenceReviewResponse,
    EvidenceDetail,
    # Speaker Mapping (015-evidence-speaker-mapping)
    SpeakerMappingItem,
    SpeakerMappingUpdateRequest,
    SpeakerMappingResponse,
)

# Draft
from app.db.schemas.draft import (
    DraftPreviewRequest,
    DraftCitation,
    PrecedentCitation,
    DraftPreviewResponse,
    DraftExportFormat,
    LineBasedDraftRequest,
    LineFormatInfo,
    DraftLine,
    LineBasedDraftResponse,
    DraftDocumentType,
    DraftDocumentStatus,
    DraftContentSection,
    DraftContent,
    DraftCreate,
    DraftUpdate,
    DraftResponse,
    DraftListItem,
    DraftListResponse,
    # Async Draft Preview
    DraftJobStatus,
    DraftJobCreateResponse,
    DraftJobStatusResponse,
)

# Audit
from app.db.schemas.audit import (
    AuditAction,
    AuditLogOut,
    AuditLogListRequest,
    AuditLogListResponse,
)

# Messaging & Notifications
from app.db.schemas.messaging import (
    MessageCreateLegacy,
    MessageOut,
    MessageListResponseLegacy,
    MarkMessageReadRequest,
    MessageCreate,
    MessageResponse,
    MessageListResponse,
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationReadAllResponse,
)

# Calendar
from app.db.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventOut,
    CalendarEventListResponse,
)

# Detective
from app.db.schemas.detective import (
    InvestigationRecordCreate,
    InvestigationRecordOut,
    InvestigationRecordListResponse,
    InvestigationReportSubmit,
    DetectiveContactCreate,
    DetectiveContactUpdate,
    DetectiveContactResponse,
    DetectiveContactListResponse,
)

# Billing
from app.db.schemas.billing import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceOut,
    InvoiceListResponse,
    InvoicePaymentRequest,
)

# Dashboard
from app.db.schemas.dashboard import (
    LawyerDashboardStats,
    ClientDashboardStats,
    DetectiveDashboardStats,
    PortalAccess,
    ROLE_PORTAL_CONFIG,
)

# Property Division
from app.db.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyOut,
    PropertyListResponse,
    PropertySummary,
    EvidenceImpact,
    SimilarCase,
    DivisionPredictionOut,
    DivisionPredictionRequest,
)

# Job Queue
from app.db.schemas.job import (
    JobCreate,
    JobOut,
    JobDetail,
    JobListResponse,
    JobStatusUpdate,
    JobProgressUpdate,
)

# User Settings
from app.db.schemas.settings import (
    ProfileSettingsUpdate,
    NotificationSettingsUpdate,
    PrivacySettingsUpdate,
    SecuritySettingsUpdate,
    ProfileSettingsOut,
    NotificationSettingsOut,
    SecuritySettingsOut,
    UserSettingsResponse,
    SettingsUpdateRequest,
)

# Party Graph
from app.db.schemas.party import (
    Position,
    PartyNodeCreate,
    PartyNodeUpdate,
    PartyNodeResponse,
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    PartyGraphResponse,
    AutoExtractedPartyRequest,
    AutoExtractedPartyResponse,
    AutoExtractedRelationshipRequest,
    AutoExtractedRelationshipResponse,
    EvidenceLinkCreate,
    EvidenceLinkResponse,
    EvidenceLinksResponse,
)

# Asset (US2)
from app.db.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    DivisionCalculateRequest,
    AssetCategorySummary,
    DivisionSummaryResponse,
    AssetSheetSummary,
)

# Client Contact
from app.db.schemas.client import (
    ClientContactCreate,
    ClientContactUpdate,
    ClientContactResponse,
    ClientContactListResponse,
)

# Re-export all for backward compatibility
__all__ = [
    # Auth
    "LoginRequest",
    "SignupRequest",
    "UserOut",
    "TokenResponse",
    "ForgotPasswordRequest",
    "ForgotPasswordResponse",
    "ResetPasswordRequest",
    "ResetPasswordResponse",
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
    "ExifMetadataInput",
    "UploadCompleteRequest",
    "UploadCompleteResponse",
    "EvidenceSummary",
    "EvidenceListResponse",
    "EvidenceReviewRequest",
    "EvidenceReviewResponse",
    "EvidenceDetail",
    # Speaker Mapping
    "SpeakerMappingItem",
    "SpeakerMappingUpdateRequest",
    "SpeakerMappingResponse",
    # Draft
    "DraftPreviewRequest",
    "DraftCitation",
    "PrecedentCitation",
    "DraftPreviewResponse",
    "DraftExportFormat",
    "LineBasedDraftRequest",
    "LineFormatInfo",
    "DraftLine",
    "LineBasedDraftResponse",
    "DraftDocumentType",
    "DraftDocumentStatus",
    "DraftContentSection",
    "DraftContent",
    "DraftCreate",
    "DraftUpdate",
    "DraftResponse",
    "DraftListItem",
    "DraftListResponse",
    # Async Draft Preview
    "DraftJobStatus",
    "DraftJobCreateResponse",
    "DraftJobStatusResponse",
    # Audit
    "AuditAction",
    "AuditLogOut",
    "AuditLogListRequest",
    "AuditLogListResponse",
    # Messaging
    "MessageCreateLegacy",
    "MessageOut",
    "MessageListResponseLegacy",
    "MarkMessageReadRequest",
    "MessageCreate",
    "MessageResponse",
    "MessageListResponse",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationReadAllResponse",
    # Calendar
    "CalendarEventCreate",
    "CalendarEventUpdate",
    "CalendarEventOut",
    "CalendarEventListResponse",
    # Detective
    "InvestigationRecordCreate",
    "InvestigationRecordOut",
    "InvestigationRecordListResponse",
    "InvestigationReportSubmit",
    "DetectiveContactCreate",
    "DetectiveContactUpdate",
    "DetectiveContactResponse",
    "DetectiveContactListResponse",
    # Billing
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceOut",
    "InvoiceListResponse",
    "InvoicePaymentRequest",
    # Dashboard
    "LawyerDashboardStats",
    "ClientDashboardStats",
    "DetectiveDashboardStats",
    "PortalAccess",
    "ROLE_PORTAL_CONFIG",
    # Property
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyOut",
    "PropertyListResponse",
    "PropertySummary",
    "EvidenceImpact",
    "SimilarCase",
    "DivisionPredictionOut",
    "DivisionPredictionRequest",
    # Job
    "JobCreate",
    "JobOut",
    "JobDetail",
    "JobListResponse",
    "JobStatusUpdate",
    "JobProgressUpdate",
    # Settings
    "ProfileSettingsUpdate",
    "NotificationSettingsUpdate",
    "PrivacySettingsUpdate",
    "SecuritySettingsUpdate",
    "ProfileSettingsOut",
    "NotificationSettingsOut",
    "SecuritySettingsOut",
    "UserSettingsResponse",
    "SettingsUpdateRequest",
    # Party
    "Position",
    "PartyNodeCreate",
    "PartyNodeUpdate",
    "PartyNodeResponse",
    "RelationshipCreate",
    "RelationshipUpdate",
    "RelationshipResponse",
    "PartyGraphResponse",
    "AutoExtractedPartyRequest",
    "AutoExtractedPartyResponse",
    "AutoExtractedRelationshipRequest",
    "AutoExtractedRelationshipResponse",
    "EvidenceLinkCreate",
    "EvidenceLinkResponse",
    "EvidenceLinksResponse",
    # Asset
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetListResponse",
    "DivisionCalculateRequest",
    "AssetCategorySummary",
    "DivisionSummaryResponse",
    "AssetSheetSummary",
    # Client
    "ClientContactCreate",
    "ClientContactUpdate",
    "ClientContactResponse",
    "ClientContactListResponse",
]
