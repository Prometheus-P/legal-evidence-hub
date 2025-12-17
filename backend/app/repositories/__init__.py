"""
Repository layer package.

Provides data access objects for database operations.
Import repositories as needed to avoid circular dependencies.
"""

# Core repositories
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.repositories.user_repository import UserRepository

# Feature repositories
from app.repositories.asset_repository import AssetRepository
from app.repositories.case_checklist_repository import CaseChecklistRepository
from app.repositories.evidence_link_repository import EvidenceLinkRepository
from app.repositories.job_repository import JobRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.party_repository import PartyRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.procedure_repository import ProcedureRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.relationship_repository import RelationshipRepository

# Contact repositories
from app.repositories.client_contact_repository import ClientContactRepository
from app.repositories.detective_contact_repository import DetectiveContactRepository
from app.repositories.detective_earnings_repository import DetectiveEarningsRepository

# Admin repositories
from app.repositories.invite_token_repository import InviteTokenRepository

__all__ = [
    # Core
    "AuditLogRepository",
    "CaseRepository",
    "CaseMemberRepository",
    "UserRepository",
    # Feature
    "AssetRepository",
    "CaseChecklistRepository",
    "EvidenceLinkRepository",
    "JobRepository",
    "MessageRepository",
    "NotificationRepository",
    "PartyRepository",
    "PredictionRepository",
    "ProcedureRepository",
    "PropertyRepository",
    "RelationshipRepository",
    # Contact
    "ClientContactRepository",
    "DetectiveContactRepository",
    "DetectiveEarningsRepository",
    # Admin
    "InviteTokenRepository",
]
