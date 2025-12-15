"""
Unit tests for PropertyService
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from app.services.property_service import PropertyService
from app.db.schemas import PropertyCreate, PropertyUpdate
from app.middleware import NotFoundError, PermissionError


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_property_repo():
    """Create a mock property repository."""
    return MagicMock()


@pytest.fixture
def mock_case_repo():
    """Create a mock case repository."""
    return MagicMock()


@pytest.fixture
def mock_member_repo():
    """Create a mock case member repository."""
    return MagicMock()


@pytest.fixture
def property_service(mock_db, mock_property_repo, mock_case_repo, mock_member_repo):
    """Create PropertyService with mocked repositories."""
    with patch('app.services.property_service.PropertyRepository', return_value=mock_property_repo), \
         patch('app.services.property_service.CaseRepository', return_value=mock_case_repo), \
         patch('app.services.property_service.CaseMemberRepository', return_value=mock_member_repo):
        service = PropertyService(mock_db)
        service.property_repo = mock_property_repo
        service.case_repo = mock_case_repo
        service.member_repo = mock_member_repo
        return service


class TestPropertyServiceInit:
    """Tests for PropertyService initialization."""

    def test_init_creates_repositories(self, mock_db):
        """Test that __init__ creates all repositories."""
        with patch('app.services.property_service.PropertyRepository') as mock_prop, \
             patch('app.services.property_service.CaseRepository') as mock_case, \
             patch('app.services.property_service.CaseMemberRepository') as mock_member:

            _service = PropertyService(mock_db)  # noqa: F841

            mock_prop.assert_called_once_with(mock_db)
            mock_case.assert_called_once_with(mock_db)
            mock_member.assert_called_once_with(mock_db)


class TestCheckCaseAccess:
    """Tests for _check_case_access method."""

    def test_check_access_case_not_found(self, property_service, mock_case_repo, mock_member_repo):
        """Raises NotFoundError when case doesn't exist."""
        mock_case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            property_service._check_case_access("case-1", "user-1")

        mock_case_repo.get_by_id.assert_called_once_with("case-1")

    def test_check_access_no_permission(self, property_service, mock_case_repo, mock_member_repo):
        """Raises PermissionError when user doesn't have access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = False

        with pytest.raises(PermissionError):
            property_service._check_case_access("case-1", "user-1")

    def test_check_access_success(self, property_service, mock_case_repo, mock_member_repo):
        """No exception when case exists and user has access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        # Should not raise
        property_service._check_case_access("case-1", "user-1")


class TestCreateProperty:
    """Tests for create_property method."""

    def test_create_property_success(
        self, property_service, mock_db,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Creates property successfully."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        # Mock created property
        mock_property = MagicMock()
        mock_property.id = "prop-1"
        mock_property.case_id = "case-1"
        mock_property.property_type = "real_estate"
        mock_property.estimated_value = 500000000
        mock_property.owner = "plaintiff"
        mock_property.description = "아파트"
        mock_property.is_premarital = False
        mock_property.acquisition_date = date(2020, 1, 15)
        mock_property.notes = "강남구 소재"
        mock_property.created_at = MagicMock()
        mock_property.updated_at = MagicMock()

        mock_property_repo.create.return_value = mock_property

        property_data = PropertyCreate(
            property_type="real_estate",
            estimated_value=500000000,
            owner="plaintiff",
            description="아파트",
            is_premarital=False,
            acquisition_date=date(2020, 1, 15),
            notes="강남구 소재"
        )

        result = property_service.create_property("case-1", property_data, "user-1")

        assert result is not None
        mock_property_repo.create.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_property_no_access(
        self, property_service,
        mock_case_repo, mock_member_repo
    ):
        """Raises PermissionError when user has no access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = False

        property_data = PropertyCreate(
            property_type="real_estate",
            estimated_value=500000000,
            owner="plaintiff"
        )

        with pytest.raises(PermissionError):
            property_service.create_property("case-1", property_data, "user-1")


class TestGetProperties:
    """Tests for get_properties method."""

    def test_get_properties_success(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Returns list of properties with summary."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        # Mock properties list
        mock_prop1 = MagicMock()
        mock_prop1.id = "prop-1"
        mock_prop1.case_id = "case-1"
        mock_prop1.property_type = "real_estate"
        mock_prop1.estimated_value = 500000000
        mock_prop1.owner = "plaintiff"
        mock_prop1.description = "아파트"
        mock_prop1.is_premarital = False
        mock_prop1.acquisition_date = None
        mock_prop1.notes = None
        mock_prop1.created_at = MagicMock()
        mock_prop1.updated_at = MagicMock()

        mock_property_repo.get_all_for_case.return_value = [mock_prop1]
        mock_property_repo.get_summary.return_value = {
            "total_assets": 500000000,
            "total_debts": 0,
            "net_value": 500000000
        }

        result = property_service.get_properties("case-1", "user-1")

        assert result.total == 1
        assert result.total_assets == 500000000
        assert result.net_value == 500000000

    def test_get_properties_empty(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Returns empty list when no properties."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property_repo.get_all_for_case.return_value = []
        mock_property_repo.get_summary.return_value = {
            "total_assets": 0,
            "total_debts": 0,
            "net_value": 0
        }

        result = property_service.get_properties("case-1", "user-1")

        assert result.total == 0
        assert result.properties == []


class TestGetProperty:
    """Tests for get_property method."""

    def test_get_property_success(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Returns property when found."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.id = "prop-1"
        mock_property.case_id = "case-1"
        mock_property.property_type = "real_estate"
        mock_property.estimated_value = 500000000
        mock_property.owner = "plaintiff"
        mock_property.description = "아파트"
        mock_property.is_premarital = False
        mock_property.acquisition_date = None
        mock_property.notes = None
        mock_property.created_at = MagicMock()
        mock_property.updated_at = MagicMock()

        mock_property_repo.get_by_id.return_value = mock_property

        result = property_service.get_property("case-1", "prop-1", "user-1")

        assert result is not None
        mock_property_repo.get_by_id.assert_called_once_with("prop-1")

    def test_get_property_not_found(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Raises NotFoundError when property not found."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_property_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            property_service.get_property("case-1", "prop-1", "user-1")

    def test_get_property_wrong_case(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Raises NotFoundError when property belongs to different case."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.case_id = "other-case"

        mock_property_repo.get_by_id.return_value = mock_property

        with pytest.raises(NotFoundError):
            property_service.get_property("case-1", "prop-1", "user-1")


class TestUpdateProperty:
    """Tests for update_property method."""

    def test_update_property_success(
        self, property_service, mock_db,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Updates property successfully."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.id = "prop-1"
        mock_property.case_id = "case-1"
        mock_property.property_type = "real_estate"
        mock_property.estimated_value = 500000000
        mock_property.owner = "plaintiff"
        mock_property.description = "아파트"
        mock_property.is_premarital = False
        mock_property.acquisition_date = None
        mock_property.notes = None
        mock_property.created_at = MagicMock()
        mock_property.updated_at = MagicMock()

        mock_property_repo.get_by_id.return_value = mock_property

        update_data = PropertyUpdate(
            estimated_value=600000000,
            description="리모델링 후 아파트"
        )

        result = property_service.update_property("case-1", "prop-1", update_data, "user-1")

        assert result is not None
        assert mock_property.estimated_value == 600000000
        assert mock_property.description == "리모델링 후 아파트"
        mock_property_repo.update.assert_called_once_with(mock_property)
        mock_db.commit.assert_called_once()

    def test_update_property_partial_fields(
        self, property_service, mock_db,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Updates partial property fields."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.id = "prop-1"
        mock_property.case_id = "case-1"
        mock_property.property_type = "real_estate"
        mock_property.estimated_value = 500000000
        mock_property.owner = "plaintiff"
        mock_property.description = "아파트"
        mock_property.is_premarital = False
        mock_property.acquisition_date = None
        mock_property.notes = None
        mock_property.created_at = MagicMock()
        mock_property.updated_at = MagicMock()

        mock_property_repo.get_by_id.return_value = mock_property

        # Update some fields
        update_data = PropertyUpdate(
            description="변경된 설명",
            notes="메모 추가"
        )

        property_service.update_property("case-1", "prop-1", update_data, "user-1")

        assert mock_property.description == "변경된 설명"
        assert mock_property.notes == "메모 추가"
        # Unchanged fields should remain
        mock_property_repo.update.assert_called_once_with(mock_property)

    def test_update_property_not_found(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Raises NotFoundError when property not found."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_property_repo.get_by_id.return_value = None

        update_data = PropertyUpdate(estimated_value=600000000)

        with pytest.raises(NotFoundError):
            property_service.update_property("case-1", "prop-1", update_data, "user-1")


class TestDeleteProperty:
    """Tests for delete_property method."""

    def test_delete_property_success(
        self, property_service, mock_db,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Deletes property successfully."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.id = "prop-1"
        mock_property.case_id = "case-1"

        mock_property_repo.get_by_id.return_value = mock_property

        property_service.delete_property("case-1", "prop-1", "user-1")

        mock_property_repo.delete.assert_called_once_with("prop-1")
        mock_db.commit.assert_called_once()

    def test_delete_property_not_found(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Raises NotFoundError when property not found."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True
        mock_property_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            property_service.delete_property("case-1", "prop-1", "user-1")

    def test_delete_property_wrong_case(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Raises NotFoundError when property belongs to different case."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property = MagicMock()
        mock_property.case_id = "other-case"

        mock_property_repo.get_by_id.return_value = mock_property

        with pytest.raises(NotFoundError):
            property_service.delete_property("case-1", "prop-1", "user-1")


class TestGetSummary:
    """Tests for get_summary method."""

    def test_get_summary_success(
        self, property_service,
        mock_case_repo, mock_member_repo, mock_property_repo
    ):
        """Returns property summary."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = True

        mock_property_repo.get_summary.return_value = {
            "total_assets": 500000000,
            "total_debts": 100000000,
            "net_value": 400000000,
            "by_type": {"real_estate": 500000000, "debt": -100000000},
            "by_owner": {"plaintiff": 300000000, "defendant": 100000000}
        }

        result = property_service.get_summary("case-1", "user-1")

        assert result.total_assets == 500000000
        assert result.total_debts == 100000000
        assert result.net_value == 400000000
        assert "real_estate" in result.by_type
        assert "plaintiff" in result.by_owner

    def test_get_summary_no_access(
        self, property_service,
        mock_case_repo, mock_member_repo
    ):
        """Raises PermissionError when user has no access."""
        mock_case_repo.get_by_id.return_value = MagicMock()
        mock_member_repo.has_access.return_value = False

        with pytest.raises(PermissionError):
            property_service.get_summary("case-1", "user-1")
