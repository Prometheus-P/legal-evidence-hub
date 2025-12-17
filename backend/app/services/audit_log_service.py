"""
Audit Log Service - Business logic for audit log management
Handles audit log retrieval, CSV export, and access denied logging
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.schemas import (
    AuditAction,
    AuditLogOut,
    AuditLogListRequest,
    AuditLogListResponse
)
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
import math
import logging

logger = logging.getLogger(__name__)


class AuditLogService:
    """
    Service for audit log management business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditLogRepository(db)
        self.user_repo = UserRepository(db)

    def get_audit_logs(
        self,
        request: AuditLogListRequest
    ) -> AuditLogListResponse:
        """
        Get audit logs with filtering and pagination

        Args:
            request: Audit log list request with filters

        Returns:
            Paginated audit log response
        """
        # Get logs from repository
        logs, total = self.audit_repo.get_logs_with_pagination(
            start_date=request.start_date,
            end_date=request.end_date,
            user_id=request.user_id,
            actions=request.actions,
            page=request.page,
            page_size=request.page_size
        )

        # Convert to output schema with user info
        log_outs = []
        for log in logs:
            user = self.user_repo.get_by_id(log.user_id)

            log_outs.append(AuditLogOut(
                id=log.id,
                user_id=log.user_id,
                user_email=user.email if user else None,
                user_name=user.name if user else None,
                action=log.action,
                object_id=log.object_id,
                timestamp=log.timestamp
            ))

        # Calculate total pages
        total_pages = math.ceil(total / request.page_size) if total > 0 else 0

        return AuditLogListResponse(
            logs=log_outs,
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages
        )

    def export_audit_logs_csv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        actions: Optional[List[AuditAction]] = None
    ) -> str:
        """
        Export audit logs to CSV format

        Args:
            start_date: Filter logs after this date (optional)
            end_date: Filter logs before this date (optional)
            user_id: Filter logs by user ID (optional)
            actions: Filter logs by action types (optional)

        Returns:
            CSV string content
        """
        # Get all logs for export (no pagination)
        logs = self.audit_repo.get_logs_for_export(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            actions=actions
        )

        # Build CSV content
        csv_lines = []

        # Header
        csv_lines.append("ID,User ID,User Email,User Name,Action,Object ID,Timestamp")

        # Data rows
        for log in logs:
            user = self.user_repo.get_by_id(log.user_id)

            csv_lines.append(",".join([
                log.id,
                log.user_id,
                user.email if user else "",
                f'"{user.name}"' if user else "",  # Quote name for CSV safety
                log.action,
                log.object_id or "",
                log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ]))

        return "\n".join(csv_lines)

    def log_access_denied(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str
    ) -> None:
        """
        Log an ACCESS_DENIED event to the audit log

        Args:
            user_id: ID of user who was denied access
            resource_type: Type of resource (e.g., "case", "evidence", "draft")
            resource_id: ID of the resource that was denied access to

        Returns:
            None (fails silently to not interrupt the 403 response)
        """
        try:
            # Format: resource_type:resource_id (e.g., "case:case_123abc")
            object_id = f"{resource_type}:{resource_id}"

            self.audit_repo.create(
                user_id=user_id,
                action=AuditAction.ACCESS_DENIED.value,
                object_id=object_id
            )
            self.db.commit()

            logger.info(
                f"ACCESS_DENIED logged: user={user_id}, "
                f"resource_type={resource_type}, resource_id={resource_id}"
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            logger.error(f"Failed to log ACCESS_DENIED: {e}")
            self.db.rollback()
