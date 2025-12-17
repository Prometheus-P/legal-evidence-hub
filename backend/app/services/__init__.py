"""
Service layer package.

Provides business logic services for the application.
Import services as needed to avoid circular dependencies.
"""

# Core services
from app.services.audit_service import AuditService, AuditLogService
from app.services.auth_service import AuthService
from app.services.case_service import CaseService
from app.services.evidence_service import EvidenceService

# List services
from app.services.case_list_service import CaseListService
from app.services.client_list_service import ClientListService
from app.services.investigator_list_service import InvestigatorListService

# Feature services
from app.services.asset_service import AssetService
from app.services.billing_service import BillingService
from app.services.calendar_service import CalendarService
from app.services.dashboard_service import DashboardService
from app.services.draft_service import DraftService
from app.services.evidence_link_service import EvidenceLinkService
from app.services.job_service import JobService
from app.services.message_service import MessageService
from app.services.notification_service import NotificationService
from app.services.party_service import PartyService
from app.services.precedent_service import PrecedentService
from app.services.procedure_service import ProcedureService
from app.services.property_service import PropertyService
from app.services.relationship_service import RelationshipService
from app.services.search_service import SearchService
from app.services.settings_service import SettingsService

# Portal services
from app.services.client_portal_service import ClientPortalService
from app.services.detective_portal_service import DetectivePortalService
from app.services.lawyer_dashboard_service import LawyerDashboardService

# Admin services
from app.services.role_management_service import RoleManagementService
from app.services.user_management_service import UserManagementService

__all__ = [
    # Core
    "AuditService",
    "AuditLogService",
    "AuthService",
    "CaseService",
    "EvidenceService",
    # List
    "CaseListService",
    "ClientListService",
    "InvestigatorListService",
    # Feature
    "AssetService",
    "BillingService",
    "CalendarService",
    "DashboardService",
    "DraftService",
    "EvidenceLinkService",
    "JobService",
    "MessageService",
    "NotificationService",
    "PartyService",
    "PrecedentService",
    "ProcedureService",
    "PropertyService",
    "RelationshipService",
    "SearchService",
    "SettingsService",
    # Portal
    "ClientPortalService",
    "DetectivePortalService",
    "LawyerDashboardService",
    # Admin
    "RoleManagementService",
    "UserManagementService",
]
