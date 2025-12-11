"""
Unit tests for Detective Portal Service
TDD - Improving test coverage for detective_portal_service.py
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.detective_portal_service import DetectivePortalService
from app.schemas.detective_portal import RecordType


class TestGetCases:
    """Unit tests for get_cases method"""

    def test_get_cases_empty(self):
        """Returns empty list when no cases"""
        mock_db = MagicMock()

        # Mock query chain for empty result
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service.get_cases("detective-123")

            assert result.items == []
            assert result.total == 0


class TestGetCaseDetail:
    """Unit tests for get_case_detail method"""

    def test_get_case_detail_case_not_found(self):
        """Raises KeyError when case not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            with pytest.raises(KeyError, match="Case not found"):
                service.get_case_detail("detective-123", "case-123")

    def test_get_case_detail_not_member(self):
        """Raises PermissionError when detective not case member"""
        mock_db = MagicMock()

        # First query returns case, second returns None for member
        mock_case = MagicMock()
        mock_case.id = "case-123"

        call_count = [0]
        def mock_filter(*args):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:  # First call for case lookup
                result.first.return_value = mock_case
            else:  # Second call for member lookup
                result.first.return_value = None
            return result

        mock_db.query.return_value.filter = mock_filter

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            with pytest.raises(PermissionError, match="Not authorized"):
                service.get_case_detail("detective-123", "case-123")


class TestAcceptCase:
    """Unit tests for accept_case method"""

    def test_accept_case_not_member(self):
        """Raises KeyError when detective not case member"""
        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=None)

            with pytest.raises(KeyError, match="Case not found or not assigned"):
                service.accept_case("detective-123", "case-123")


class TestRejectCase:
    """Unit tests for reject_case method"""

    def test_reject_case_not_member(self):
        """Raises KeyError when detective not case member"""
        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=None)

            with pytest.raises(KeyError, match="Case not found or not assigned"):
                service.reject_case("detective-123", "case-123", "reason")


class TestCreateFieldRecord:
    """Unit tests for create_field_record method"""

    def test_create_field_record_not_member(self):
        """Raises KeyError when detective not case member"""
        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=None)

            with pytest.raises(KeyError, match="Case not found or not assigned"):
                service.create_field_record(
                    detective_id="detective-123",
                    case_id="case-123",
                    record_type=RecordType.NOTE,
                    content="Test content"
                )


class TestSubmitReport:
    """Unit tests for submit_report method"""

    def test_submit_report_not_member(self):
        """Raises KeyError when detective not case member"""
        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=None)

            with pytest.raises(KeyError, match="Case not found or not assigned"):
                service.submit_report(
                    detective_id="detective-123",
                    case_id="case-123",
                    summary="summary",
                    findings="findings",
                    conclusion="conclusion"
                )


class TestGetEarnings:
    """Unit tests for get_earnings method"""

    def test_get_earnings_returns_data_from_repository(self):
        """Returns earnings data from repository"""
        from decimal import Decimal

        mock_db = MagicMock()

        # Mock repository
        mock_repo = MagicMock()
        mock_repo.get_earnings_summary.return_value = {
            "total": Decimal("15000000"),
            "pending": Decimal("500000")
        }
        mock_repo.get_by_detective_id.return_value = []

        # Mock this month query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            with patch('app.repositories.detective_earnings_repository.DetectiveEarningsRepository', return_value=mock_repo):
                service = DetectivePortalService(mock_db)
                service.db = mock_db

                result = service.get_earnings("detective-123")

                assert result.summary.total_earned == 15000000.0
                assert result.summary.pending_payment == 500000.0
                assert len(result.transactions) == 0


class TestGetDashboard:
    """Unit tests for get_dashboard method"""

    def test_get_dashboard_detective_not_found(self):
        """Raises ValueError when detective not found"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            with pytest.raises(ValueError, match="Detective not found"):
                service.get_dashboard("detective-123")


class TestAcceptCaseSuccess:
    """Unit tests for accept_case success path"""

    def test_accept_case_success(self):
        """Accept case successfully"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_case = MagicMock()
        mock_case.id = "case-123"

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)
            mock_db.query.return_value.filter.return_value.first.return_value = mock_case

            result = service.accept_case("detective-123", "case-123")

            assert result.success is True
            assert result.case_id == "case-123"
            mock_db.commit.assert_called_once()


class TestRejectCaseSuccess:
    """Unit tests for reject_case success path"""

    def test_reject_case_success(self):
        """Reject case successfully"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)

            result = service.reject_case("detective-123", "case-123", "Not enough time")

            assert result.success is True
            assert result.case_id == "case-123"
            assert "Not enough time" in result.message
            mock_db.delete.assert_called_once_with(mock_member)
            mock_db.commit.assert_called_once()


class TestPrivateHelpers:
    """Unit tests for private helper methods"""

    def test_get_case_member(self):
        """Test _get_case_member returns member"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_member

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._get_case_member("detective-123", "case-123")

            assert result == mock_member

    def test_map_case_status_pending(self):
        """Test _map_case_status for pending"""
        from app.schemas.detective_portal import InvestigationStatus

        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._map_case_status("pending")
            assert result == InvestigationStatus.PENDING

    def test_map_case_status_active(self):
        """Test _map_case_status for active"""
        from app.schemas.detective_portal import InvestigationStatus

        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._map_case_status("active")
            assert result == InvestigationStatus.ACTIVE

    def test_map_case_status_unknown(self):
        """Test _map_case_status for unknown status"""
        from app.schemas.detective_portal import InvestigationStatus

        mock_db = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._map_case_status("unknown_status")
            assert result == InvestigationStatus.PENDING

    def test_get_case_lawyer_not_found(self):
        """Test _get_case_lawyer returns None when no lawyer"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._get_case_lawyer("case-123")

            assert result is None

    def test_get_case_lawyer_found(self):
        """Test _get_case_lawyer returns user when found"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_member.user_id = "lawyer-123"
        mock_user = MagicMock()
        mock_user.name = "Test Lawyer"

        # First call returns member, second returns user
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_member, mock_user]

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._get_case_lawyer("case-123")

            assert result == mock_user


class TestAcceptCaseCaseNotFound:
    """Unit tests for accept_case when case not found after member check"""

    def test_accept_case_case_not_found(self):
        """Raises KeyError when case not found after member check"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)
            # Case not found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            with pytest.raises(KeyError, match="Case not found"):
                service.accept_case("detective-123", "case-123")


class TestGetCasesWithStatusFilter:
    """Unit tests for get_cases with status filter"""

    def test_get_cases_with_status_filter(self):
        """Returns cases filtered by status"""
        mock_db = MagicMock()

        # Mock query chain for filtered result
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service.get_cases("detective-123", status="active")

            assert result.items == []
            assert result.total == 0
            # Verify filter was called multiple times (join filter + status filter)
            assert mock_query.filter.call_count >= 1


class TestGetCaseRecordCount:
    """Unit tests for _get_case_record_count method"""

    def test_get_case_record_count(self):
        """Returns record count for detective in case"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.count.return_value = 5

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._get_case_record_count("case-123", "detective-123")

            assert result == 5


class TestGetInvestigationCount:
    """Unit tests for _get_investigation_count method"""

    def test_get_investigation_count(self):
        """Returns investigation count by status"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            result = service._get_investigation_count("detective-123", "active")

            assert result == 3


class TestGetCasesWithCases:
    """Unit tests for get_cases with actual cases"""

    def test_get_cases_with_items(self):
        """Returns case list items with lawyer and record count"""
        from app.db.models import CaseStatus

        mock_db = MagicMock()

        # Create mock cases
        mock_case = MagicMock()
        mock_case.id = "case-123"
        mock_case.title = "Test Case"
        mock_case.status = CaseStatus.OPEN
        mock_case.created_at = datetime.now(timezone.utc)
        mock_case.updated_at = datetime.now(timezone.utc)

        # Mock query chain
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_case]
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            # Mock helper methods
            mock_lawyer = MagicMock()
            mock_lawyer.name = "Test Lawyer"
            service._get_case_lawyer = MagicMock(return_value=mock_lawyer)
            service._get_case_record_count = MagicMock(return_value=5)

            result = service.get_cases("detective-123")

            assert result.total == 1
            assert len(result.items) == 1
            assert result.items[0].title == "Test Case"
            assert result.items[0].lawyer_name == "Test Lawyer"
            assert result.items[0].record_count == 5


class TestCreateFieldRecordSuccess:
    """Unit tests for create_field_record success path"""

    def test_create_field_record_observation(self):
        """Creates field record with observation type"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_record = MagicMock()
        mock_record.id = "record-123"

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)

            # Mock db.add to capture the record
            def capture_record(rec):
                mock_db._captured_record = rec

            mock_db.add.side_effect = capture_record
            mock_db.refresh = lambda rec: setattr(rec, 'id', 'record-123')

            result = service.create_field_record(
                detective_id="detective-123",
                case_id="case-123",
                record_type=RecordType.OBSERVATION,
                content="Observed target at location",
                gps_lat=37.5665,
                gps_lng=126.9780
            )

            assert result.success is True
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    def test_create_field_record_photo(self):
        """Creates field record with photo type"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)

            # Mock db.refresh to set record.id
            def mock_refresh(rec):
                rec.id = "record-photo-123"

            mock_db.refresh = mock_refresh

            result = service.create_field_record(
                detective_id="detective-123",
                case_id="case-123",
                record_type=RecordType.PHOTO,
                content="Photo evidence of meeting"
            )

            assert result.success is True
            assert result.record_id == "record-photo-123"

    def test_create_field_record_video(self):
        """Creates field record with video type"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)

            # Mock db.refresh to set record.id
            def mock_refresh(rec):
                rec.id = "record-video-123"

            mock_db.refresh = mock_refresh

            result = service.create_field_record(
                detective_id="detective-123",
                case_id="case-123",
                record_type=RecordType.VIDEO,
                content="Video evidence"
            )

            assert result.success is True
            assert result.record_id == "record-video-123"

    def test_create_field_record_audio(self):
        """Creates field record with audio type"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)

            # Mock db.refresh to set record.id
            def mock_refresh(rec):
                rec.id = "record-audio-123"

            mock_db.refresh = mock_refresh

            result = service.create_field_record(
                detective_id="detective-123",
                case_id="case-123",
                record_type=RecordType.AUDIO,
                content="Audio recording"
            )

            assert result.success is True
            assert result.record_id == "record-audio-123"


class TestSubmitReportSuccess:
    """Unit tests for submit_report success path"""

    def test_submit_report_success(self):
        """Submits report successfully"""
        mock_db = MagicMock()
        mock_member = MagicMock()
        mock_case = MagicMock()
        mock_case.id = "case-123"
        mock_case.status = "open"

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)
            mock_db.query.return_value.filter.return_value.first.return_value = mock_case

            # Mock db.refresh to set record.id
            def mock_refresh(rec):
                rec.id = "report-123"

            mock_db.refresh = mock_refresh

            result = service.submit_report(
                detective_id="detective-123",
                case_id="case-123",
                summary="Investigation summary",
                findings="Key findings from investigation",
                conclusion="Final conclusion"
            )

            assert result.success is True
            assert result.report_id == "report-123"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            # Verify case status was updated
            assert mock_case.status == "in_progress"

    def test_submit_report_case_not_found(self):
        """Raises KeyError when case not found after member check"""
        mock_db = MagicMock()
        mock_member = MagicMock()

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db
            service._get_case_member = MagicMock(return_value=mock_member)
            # Case not found
            mock_db.query.return_value.filter.return_value.first.return_value = None

            with pytest.raises(KeyError, match="Case not found"):
                service.submit_report(
                    detective_id="detective-123",
                    case_id="case-123",
                    summary="summary",
                    findings="findings",
                    conclusion="conclusion"
                )


class TestGetActiveInvestigations:
    """Unit tests for _get_active_investigations method"""

    def test_get_active_investigations_with_items(self):
        """Returns active investigations with lawyer name and record count"""
        from app.db.models import CaseStatus

        mock_db = MagicMock()

        # Create mock case
        mock_case = MagicMock()
        mock_case.id = "case-456"
        mock_case.title = "Active Case"
        mock_case.status = CaseStatus.OPEN

        # Mock query chain
        mock_query = MagicMock()
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_case]
        mock_db.query.return_value = mock_query

        with patch.object(DetectivePortalService, '__init__', lambda x, y: None):
            service = DetectivePortalService(mock_db)
            service.db = mock_db

            # Mock helper methods
            mock_lawyer = MagicMock()
            mock_lawyer.name = "Active Lawyer"
            service._get_case_lawyer = MagicMock(return_value=mock_lawyer)
            service._get_case_record_count = MagicMock(return_value=3)

            result = service._get_active_investigations("detective-123")

            assert len(result) == 1
            assert result[0].title == "Active Case"
            assert result[0].lawyer_name == "Active Lawyer"
            assert result[0].record_count == 3
