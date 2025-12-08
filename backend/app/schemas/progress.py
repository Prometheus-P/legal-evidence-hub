"""Schemas for paralegal progress dashboard."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.db.models import CaseStatus


class EvidenceCounts(BaseModel):
    """Aggregated evidence counts by processing state."""

    pending: int = 0
    uploaded: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0


class FeedbackChecklistItem(BaseModel):
    """Represents a single feedback action item."""

    item_id: str
    title: str
    status: str = "pending"
    description: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class AssigneeInfo(BaseModel):
    """Minimal user info displayed on dashboard."""

    id: str
    name: str
    email: Optional[str] = None


class ProgressFilter(BaseModel):
    """Query parameters for filtering progress data."""

    blocked_only: bool = False
    assignee_id: Optional[str] = None


class CaseProgressSummary(BaseModel):
    """Aggregated progress signal for a single case."""

    case_id: str
    title: str
    client_name: Optional[str] = None
    status: CaseStatus
    assignee: AssigneeInfo
    updated_at: datetime
    evidence_counts: EvidenceCounts
    ai_status: str
    ai_last_updated: Optional[datetime] = None
    outstanding_feedback_count: int = 0
    feedback_items: List[FeedbackChecklistItem]
    is_blocked: bool = False
    blocked_reason: Optional[str] = None


class FeedbackChecklistUpdate(BaseModel):
    """Payload for updating checklist status."""

    status: str
    notes: Optional[str] = None
