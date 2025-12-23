"""
SQLAlchemy ORM Models for LEH Backend
Database tables: users, cases, case_members, audit_logs, etc.

This module re-exports all models and enums from domain-specific modules for backward compatibility.
Import from this module or directly from submodules:
    from app.db.models import User  # Legacy
    from app.db.models.auth import User  # Preferred
"""

# Base and utilities
from app.db.models.base import Base, StrEnumColumn

# ============================================
# Enums
# ============================================
from app.db.models.enums import (
    # User & Auth
    UserRole,
    UserStatus,
    AgreementType,
    # Case
    CaseStatus,
    CaseMemberRole,
    # Draft & Document
    DocumentType,
    DraftStatus,
    ExportFormat,
    ExportJobStatus,
    # Calendar
    CalendarEventType,
    # Investigation & Detective
    InvestigationRecordType,
    EarningsStatus,
    # Billing
    InvoiceStatus,
    # Property & Asset
    PropertyType,
    PropertyOwner,
    AssetCategory,
    AssetOwnership,
    AssetNature,
    ConfidenceLevel,
    # Job & Processing
    JobType,
    JobStatus,
    EvidenceStatus,
    # Settings
    NotificationFrequency,
    ProfileVisibility,
    # Party Graph
    PartyType,
    RelationshipType,
    LinkType,
    # Procedure Stage
    ProcedureStageType,
    StageStatus,
    # Notification
    NotificationType,
    # Consultation
    ConsultationType,
)

# ============================================
# Models
# ============================================
# Auth & User
from app.db.models.auth import (
    User,
    InviteToken,
    PasswordResetToken,
    UserAgreement,
)

# Case
from app.db.models.case import (
    Case,
    CaseMember,
    CaseChecklistStatus,
)

# Audit
from app.db.models.audit import AuditLog

# Draft & Document
from app.db.models.draft import (
    DraftDocument,
    ExportJob,
    DocumentTemplate,
)

# Messaging & Notification
from app.db.models.messaging import (
    Message,
    Notification,
)

# Calendar
from app.db.models.calendar import CalendarEvent

# Detective & Investigation
from app.db.models.detective import (
    InvestigationRecord,
    DetectiveEarnings,
    DetectiveContact,
)

# Billing
from app.db.models.billing import Invoice

# Property & Division
from app.db.models.property import (
    CaseProperty,
    DivisionPrediction,
)

# Asset (US2)
from app.db.models.asset import (
    Asset,
    AssetDivisionSummary,
)

# Evidence
from app.db.models.evidence import Evidence

# Job Queue
from app.db.models.job import Job

# Settings
from app.db.models.settings import UserSettings

# Party Graph
from app.db.models.party import (
    PartyNode,
    PartyRelationship,
    EvidencePartyLink,
)

# Procedure Stage (US3)
from app.db.models.procedure import ProcedureStageRecord

# Client Contact
from app.db.models.client import ClientContact

# Consultation
from app.db.models.consultation import (
    Consultation,
    ConsultationParticipant,
    ConsultationEvidence,
)


# Re-export all for backward compatibility
__all__ = [
    # Base
    "Base",
    "StrEnumColumn",
    # Enums - User & Auth
    "UserRole",
    "UserStatus",
    "AgreementType",
    # Enums - Case
    "CaseStatus",
    "CaseMemberRole",
    # Enums - Draft & Document
    "DocumentType",
    "DraftStatus",
    "ExportFormat",
    "ExportJobStatus",
    # Enums - Calendar
    "CalendarEventType",
    # Enums - Investigation
    "InvestigationRecordType",
    "EarningsStatus",
    # Enums - Billing
    "InvoiceStatus",
    # Enums - Property & Asset
    "PropertyType",
    "PropertyOwner",
    "AssetCategory",
    "AssetOwnership",
    "AssetNature",
    "ConfidenceLevel",
    # Enums - Job
    "JobType",
    "JobStatus",
    "EvidenceStatus",
    # Enums - Settings
    "NotificationFrequency",
    "ProfileVisibility",
    # Enums - Party Graph
    "PartyType",
    "RelationshipType",
    "LinkType",
    # Enums - Procedure Stage
    "ProcedureStageType",
    "StageStatus",
    # Enums - Notification
    "NotificationType",
    # Models - Auth
    "User",
    "InviteToken",
    "PasswordResetToken",
    "UserAgreement",
    # Models - Case
    "Case",
    "CaseMember",
    "CaseChecklistStatus",
    # Models - Audit
    "AuditLog",
    # Models - Draft
    "DraftDocument",
    "ExportJob",
    "DocumentTemplate",
    # Models - Messaging
    "Message",
    "Notification",
    # Models - Calendar
    "CalendarEvent",
    # Models - Detective
    "InvestigationRecord",
    "DetectiveEarnings",
    "DetectiveContact",
    # Models - Billing
    "Invoice",
    # Models - Property
    "CaseProperty",
    "DivisionPrediction",
    # Models - Asset
    "Asset",
    "AssetDivisionSummary",
    # Models - Evidence
    "Evidence",
    # Models - Job
    "Job",
    # Models - Settings
    "UserSettings",
    # Models - Party Graph
    "PartyNode",
    "PartyRelationship",
    "EvidencePartyLink",
    # Models - Procedure Stage
    "ProcedureStageRecord",
    # Models - Client
    "ClientContact",
    # Enums - Consultation
    "ConsultationType",
    # Models - Consultation
    "Consultation",
    "ConsultationParticipant",
    "ConsultationEvidence",
]
