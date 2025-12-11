"""
Investigator List Schemas
005-lawyer-portal-pages Feature - US3

Pydantic schemas for lawyer's investigator management APIs.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InvestigatorSortField(str, Enum):
    """Sortable fields for investigator list"""
    NAME = "name"
    ACTIVE_ASSIGNMENTS = "active_assignments"
    COMPLETED_ASSIGNMENTS = "completed_assignments"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


class AvailabilityStatus(str, Enum):
    """Investigator availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"
    ALL = "all"


class InvestigatorFilter(BaseModel):
    """Filter parameters for investigator list"""
    search: Optional[str] = None  # Search by name or email
    availability: Optional[AvailabilityStatus] = AvailabilityStatus.ALL


class InvestigatorItem(BaseModel):
    """Single investigator item in list view"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    active_assignments: int = 0
    completed_assignments: int = 0
    availability: str = "available"
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True


class InvestigatorListResponse(BaseModel):
    """Paginated investigator list response"""
    items: List[InvestigatorItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssignedCase(BaseModel):
    """Case assigned to an investigator"""
    id: str
    title: str
    status: str
    role: str
    client_name: Optional[str] = None
    assigned_at: datetime
    last_updated: datetime


class InvestigatorStats(BaseModel):
    """Statistics for an investigator"""
    total_assignments: int = 0
    active_assignments: int = 0
    completed_assignments: int = 0
    total_evidence_collected: int = 0
    average_response_time_hours: Optional[float] = None


class InvestigatorDetail(BaseModel):
    """Detailed investigator response"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    availability: str = "available"
    created_at: datetime
    assigned_cases: List[AssignedCase] = []
    stats: InvestigatorStats = InvestigatorStats()

    class Config:
        from_attributes = True
