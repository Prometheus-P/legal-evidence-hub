"""
Audit Log Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# Audit Log Schemas
# ============================================
class AuditAction(str, Enum):
    """Audit action types"""
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    SIGNUP = "SIGNUP"

    # Case actions
    CREATE_CASE = "CREATE_CASE"
    VIEW_CASE = "VIEW_CASE"
    UPDATE_CASE = "UPDATE_CASE"
    DELETE_CASE = "DELETE_CASE"

    # Evidence actions
    UPLOAD_EVIDENCE = "UPLOAD_EVIDENCE"
    VIEW_EVIDENCE = "VIEW_EVIDENCE"
    DELETE_EVIDENCE = "DELETE_EVIDENCE"
    SPEAKER_MAPPING_UPDATE = "SPEAKER_MAPPING_UPDATE"

    # Admin actions
    INVITE_USER = "INVITE_USER"
    DELETE_USER = "DELETE_USER"
    UPDATE_PERMISSIONS = "UPDATE_PERMISSIONS"

    # Draft actions
    GENERATE_DRAFT = "GENERATE_DRAFT"
    EXPORT_DRAFT = "EXPORT_DRAFT"
    UPDATE_DRAFT = "UPDATE_DRAFT"

    # Security actions
    ACCESS_DENIED = "ACCESS_DENIED"


class AuditLogOut(BaseModel):
    """Audit log output schema"""
    id: str
    user_id: str
    user_email: Optional[str] = None  # Joined from User table
    user_name: Optional[str] = None  # Joined from User table
    action: str
    object_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogListRequest(BaseModel):
    """Audit log list request schema with filters"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    actions: Optional[List[AuditAction]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class AuditLogListResponse(BaseModel):
    """Audit log list response schema"""
    logs: List[AuditLogOut]
    total: int
    page: int
    page_size: int
    total_pages: int
