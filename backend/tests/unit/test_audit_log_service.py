"""
Unit tests for Audit Log Service
TDD - Improving test coverage for audit_log_service.py
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.audit_service import AuditLogService
from app.db.schemas import AuditLogListRequest, AuditAction


class TestGetAuditLogs:
    """Unit tests for get_audit_logs method"""

    def test_get_audit_logs_success(self):
        """Successfully get audit logs with pagination"""
        mock_db = MagicMock()

        # Mock log data
        mock_log = MagicMock()
        mock_log.id = "log-123"
        mock_log.user_id = "user-123"
        mock_log.action = "LOGIN"
        mock_log.object_id = None
        mock_log.timestamp = datetime.now(timezone.utc)

        # Mock user data
        mock_user = MagicMock()
        mock_user.email = "user@test.com"
        mock_user.name = "Test User"

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_with_pagination.return_value = ([mock_log], 1)
            service.user_repo.get_by_id.return_value = mock_user

            request = AuditLogListRequest(
                page=1,
                page_size=20
            )
            result = service.get_audit_logs(request)

            assert result.total == 1
            assert len(result.logs) == 1
            assert result.logs[0].user_email == "user@test.com"

    def test_get_audit_logs_with_filters(self):
        """Get audit logs with date and action filters"""
        mock_db = MagicMock()
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, tzinfo=timezone.utc)

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_with_pagination.return_value = ([], 0)

            request = AuditLogListRequest(
                page=1,
                page_size=20,
                start_date=start,
                end_date=end,
                actions=[AuditAction.LOGIN, AuditAction.LOGOUT]
            )
            result = service.get_audit_logs(request)

            service.audit_repo.get_logs_with_pagination.assert_called_once()
            assert result.total == 0

    def test_get_audit_logs_user_not_found(self):
        """Handles missing user gracefully"""
        mock_db = MagicMock()

        mock_log = MagicMock()
        mock_log.id = "log-123"
        mock_log.user_id = "deleted-user"
        mock_log.action = "LOGIN"
        mock_log.object_id = None
        mock_log.timestamp = datetime.now(timezone.utc)

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_with_pagination.return_value = ([mock_log], 1)
            service.user_repo.get_by_id.return_value = None

            request = AuditLogListRequest(page=1, page_size=20)
            result = service.get_audit_logs(request)

            assert result.logs[0].user_email is None
            assert result.logs[0].user_name is None

    def test_get_audit_logs_pagination(self):
        """Pagination calculates total pages correctly"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_with_pagination.return_value = ([], 45)

            request = AuditLogListRequest(page=1, page_size=10)
            result = service.get_audit_logs(request)

            assert result.total == 45
            assert result.total_pages == 5  # ceil(45/10)


class TestExportAuditLogsCsv:
    """Unit tests for export_audit_logs_csv method"""

    def test_export_csv_success(self):
        """Successfully export audit logs to CSV"""
        mock_db = MagicMock()

        mock_log = MagicMock()
        mock_log.id = "log-123"
        mock_log.user_id = "user-123"
        mock_log.action = "LOGIN"
        mock_log.object_id = "obj-123"
        mock_log.timestamp = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)

        mock_user = MagicMock()
        mock_user.email = "user@test.com"
        mock_user.name = "Test User"

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_for_export.return_value = [mock_log]
            service.user_repo.get_by_id.return_value = mock_user

            result = service.export_audit_logs_csv()

            assert "ID,User ID,User Email,User Name,Action,Object ID,Timestamp" in result
            assert "log-123" in result
            assert "user@test.com" in result
            assert "2024-06-15 10:30:00" in result

    def test_export_csv_with_filters(self):
        """Export with date and action filters"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_for_export.return_value = []

            start = datetime(2024, 1, 1, tzinfo=timezone.utc)
            end = datetime(2024, 12, 31, tzinfo=timezone.utc)

            service.export_audit_logs_csv(
                start_date=start,
                end_date=end,
                user_id="user-123",
                actions=[AuditAction.LOGIN]
            )

            service.audit_repo.get_logs_for_export.assert_called_once_with(
                start_date=start,
                end_date=end,
                user_id="user-123",
                actions=[AuditAction.LOGIN]
            )

    def test_export_csv_user_not_found(self):
        """Handles missing user in CSV export"""
        mock_db = MagicMock()

        mock_log = MagicMock()
        mock_log.id = "log-123"
        mock_log.user_id = "deleted-user"
        mock_log.action = "LOGIN"
        mock_log.object_id = None
        mock_log.timestamp = datetime(2024, 6, 15, tzinfo=timezone.utc)

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_for_export.return_value = [mock_log]
            service.user_repo.get_by_id.return_value = None

            result = service.export_audit_logs_csv()

            # Should contain empty strings for user email/name
            assert "deleted-user,," in result

    def test_export_csv_empty_logs(self):
        """Export returns header only when no logs"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.audit_repo.get_logs_for_export.return_value = []

            result = service.export_audit_logs_csv()

            # Should only have header
            assert result == "ID,User ID,User Email,User Name,Action,Object ID,Timestamp"


class TestLogAccessDenied:
    """Unit tests for log_access_denied method"""

    def test_log_access_denied_success(self):
        """Successfully log ACCESS_DENIED event"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.log_access_denied(
                user_id="user-123",
                resource_type="case",
                resource_id="case-456"
            )

            service.audit_repo.create.assert_called_once_with(
                user_id="user-123",
                action=AuditAction.ACCESS_DENIED.value,
                object_id="case:case-456"
            )
            mock_db.commit.assert_called_once()

    def test_log_access_denied_formats_object_id_correctly(self):
        """Object ID format is resource_type:resource_id"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.log_access_denied(
                user_id="user-123",
                resource_type="evidence",
                resource_id="ev-789"
            )

            call_args = service.audit_repo.create.call_args
            assert call_args.kwargs["object_id"] == "evidence:ev-789"

    def test_log_access_denied_handles_exception_gracefully(self):
        """Should not raise exception on database error"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            # Simulate database error
            service.audit_repo.create.side_effect = Exception("Database error")

            # Should not raise exception
            service.log_access_denied(
                user_id="user-123",
                resource_type="case",
                resource_id="case-456"
            )

            mock_db.rollback.assert_called_once()

    def test_log_access_denied_uses_correct_action(self):
        """Uses ACCESS_DENIED action"""
        mock_db = MagicMock()

        with patch.object(AuditLogService, '__init__', lambda x, y: None):
            service = AuditLogService(mock_db)
            service.db = mock_db
            service.audit_repo = MagicMock()
            service.user_repo = MagicMock()

            service.log_access_denied(
                user_id="user-123",
                resource_type="draft",
                resource_id="draft-001"
            )

            call_args = service.audit_repo.create.call_args
            assert call_args.kwargs["action"] == "ACCESS_DENIED"
