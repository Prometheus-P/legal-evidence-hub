"""
Unit tests for Audit Log Middleware
Tests ACCESS_DENIED (403) logging functionality
"""

import pytest
from unittest.mock import MagicMock, patch
from starlette.requests import Request

from app.middleware.audit_log import AuditLogMiddleware, extract_object_id


class TestExtractObjectId:
    """Unit tests for extract_object_id helper function"""

    def test_extracts_case_id_from_path(self):
        """Extracts ID from /cases/{id} pattern"""
        result = extract_object_id("/cases/case_123abc", r"^/cases/[^/]+$")
        assert result == "case_123abc"

    def test_extracts_first_id_from_nested_path(self):
        """Extracts first ID from /cases/{id}/draft-preview pattern"""
        result = extract_object_id(
            "/cases/case_123abc/draft-preview",
            r"^/cases/[^/]+/draft-preview$"
        )
        assert result == "case_123abc"

    def test_returns_none_for_no_id_pattern(self):
        """Returns None for patterns without ID placeholder"""
        result = extract_object_id("/auth/login", r"^/auth/login$")
        assert result is None

    def test_returns_none_for_non_matching_path(self):
        """Returns None for non-matching path"""
        result = extract_object_id("/users/user_123", r"^/cases/[^/]+$")
        assert result is None


class TestAuditLogMiddlewareExtractResourceInfo:
    """Unit tests for _extract_resource_info method"""

    def test_extracts_case_from_cases_path(self):
        """Extracts case resource from /cases/{id} path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/cases/case_123")
        assert resource_type == "case"
        assert resource_id == "case_123"

    def test_extracts_evidence_from_cases_evidence_path(self):
        """Extracts evidence resource from /cases/{id}/evidence path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/cases/case_123/evidence")
        assert resource_type == "evidence"
        assert resource_id == "case_123"

    def test_extracts_draft_from_draft_path(self):
        """Extracts draft resource from /cases/{id}/draft-preview path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/cases/case_123/draft-preview")
        assert resource_type == "draft"
        assert resource_id == "case_123"

    def test_extracts_members_from_members_path(self):
        """Extracts case_members resource from /cases/{id}/members path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/cases/case_123/members")
        assert resource_type == "case_members"
        assert resource_id == "case_123"

    def test_extracts_evidence_from_evidence_path(self):
        """Extracts evidence resource from /evidence/{id} path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/evidence/ev_123")
        assert resource_type == "evidence"
        assert resource_id == "ev_123"

    def test_extracts_search_from_semantic_path(self):
        """Extracts search resource from /search/semantic path"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/search/semantic")
        assert resource_type == "search"
        assert resource_id is None

    def test_extracts_unknown_for_unrecognized_path(self):
        """Falls back to path segment for unrecognized paths"""
        middleware = AuditLogMiddleware(app=MagicMock())
        resource_type, resource_id = middleware._extract_resource_info("/unknown/path")
        assert resource_type == "unknown"
        assert resource_id is None


class TestAuditLogMiddlewareLogAccessDenied:
    """Unit tests for _log_access_denied method"""

    @pytest.mark.asyncio
    async def test_logs_access_denied_for_403_response(self):
        """Logs ACCESS_DENIED when response is 403"""
        middleware = AuditLogMiddleware(app=MagicMock())

        # Mock request
        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = "user_123"
        mock_request.url.path = "/cases/case_456"
        mock_request.method = "GET"

        with patch('app.middleware.audit_log.SessionLocal') as mock_session_local, \
             patch('app.middleware.audit_log.AuditLogRepository') as mock_repo_class:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            await middleware._log_access_denied(mock_request)

            # Verify audit log created with correct parameters
            mock_repo.create.assert_called_once_with(
                user_id="user_123",
                action="ACCESS_DENIED",
                object_id="case:case_456"
            )
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_skips_logging_without_user_id(self):
        """Skips logging when user_id is not available"""
        middleware = AuditLogMiddleware(app=MagicMock())

        # Mock request without user_id
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock(spec=[])  # No user_id attribute
        mock_request.url.path = "/cases/case_456"

        with patch('app.middleware.audit_log.SessionLocal') as mock_session_local:
            await middleware._log_access_denied(mock_request)

            # SessionLocal should not be called
            mock_session_local.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_database_error_gracefully(self):
        """Handles database error without raising exception"""
        middleware = AuditLogMiddleware(app=MagicMock())

        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = "user_123"
        mock_request.url.path = "/cases/case_456"
        mock_request.method = "GET"

        with patch('app.middleware.audit_log.SessionLocal') as mock_session_local, \
             patch('app.middleware.audit_log.AuditLogRepository') as mock_repo_class:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_repo = MagicMock()
            mock_repo.create.side_effect = Exception("Database error")
            mock_repo_class.return_value = mock_repo

            # Should not raise exception
            await middleware._log_access_denied(mock_request)

            mock_db.rollback.assert_called_once()
            mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_formats_object_id_with_resource_id(self):
        """Formats object_id as resource_type:resource_id"""
        middleware = AuditLogMiddleware(app=MagicMock())

        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = "user_123"
        mock_request.url.path = "/evidence/ev_789"
        mock_request.method = "GET"

        with patch('app.middleware.audit_log.SessionLocal') as mock_session_local, \
             patch('app.middleware.audit_log.AuditLogRepository') as mock_repo_class:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            await middleware._log_access_denied(mock_request)

            call_args = mock_repo.create.call_args
            assert call_args.kwargs["object_id"] == "evidence:ev_789"

    @pytest.mark.asyncio
    async def test_formats_object_id_without_resource_id(self):
        """Formats object_id as just resource_type when no ID"""
        middleware = AuditLogMiddleware(app=MagicMock())

        mock_request = MagicMock(spec=Request)
        mock_request.state.user_id = "user_123"
        mock_request.url.path = "/search/semantic"
        mock_request.method = "GET"

        with patch('app.middleware.audit_log.SessionLocal') as mock_session_local, \
             patch('app.middleware.audit_log.AuditLogRepository') as mock_repo_class:
            mock_db = MagicMock()
            mock_session_local.return_value = mock_db
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo

            await middleware._log_access_denied(mock_request)

            call_args = mock_repo.create.call_args
            assert call_args.kwargs["object_id"] == "search"
