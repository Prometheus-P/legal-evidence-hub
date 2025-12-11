"""
Client List Schemas
005-lawyer-portal-pages Feature - US2

Pydantic schemas for lawyer's client management APIs.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ClientSortField(str, Enum):
    """Sortable fields for client list"""
    NAME = "name"
    CASE_COUNT = "case_count"
    LAST_ACTIVITY = "last_activity"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"


class ClientStatus(str, Enum):
    """Client status filter"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"


class ClientFilter(BaseModel):
    """Filter parameters for client list"""
    search: Optional[str] = None  # Search by name or email
    status: Optional[ClientStatus] = ClientStatus.ALL


class ClientItem(BaseModel):
    """Single client item in list view"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    case_count: int = 0
    active_cases: int = 0
    last_activity: Optional[datetime] = None
    status: str = "active"
    created_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Paginated client list response"""
    items: List[ClientItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class LinkedCase(BaseModel):
    """Case linked to a client"""
    id: str
    title: str
    status: str
    role: str  # client's role in the case
    created_at: datetime
    updated_at: datetime


class ActivityItem(BaseModel):
    """Activity item for client"""
    type: str
    case_id: str
    description: str
    timestamp: datetime


class ClientStats(BaseModel):
    """Statistics for a client"""
    total_cases: int = 0
    active_cases: int = 0
    completed_cases: int = 0
    total_evidence: int = 0
    total_messages: int = 0


class ClientDetail(BaseModel):
    """Detailed client response"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    linked_cases: List[LinkedCase] = []
    recent_activity: List[ActivityItem] = []
    stats: ClientStats = ClientStats()

    class Config:
        from_attributes = True
