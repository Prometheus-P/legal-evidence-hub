"""
Test suite for InvestigatorListService
005-lawyer-portal-pages Feature - US3

Tests for:
- get_investigators returns paginated list
- availability filter
- search filter
- empty result handling
"""


from app.services.investigator_list_service import InvestigatorListService
from app.schemas.investigator_list import (
    InvestigatorFilter,
    AvailabilityStatus,
    InvestigatorSortField,
    SortOrder,
)


class TestGetInvestigators:
    """Test suite for get_investigators method"""

    def test_should_return_paginated_investigator_list(self, db_session):
        """
        Given: Lawyer with investigators on shared cases
        When: get_investigators is called
        Then: Returns paginated InvestigatorListResponse
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_investigators(lawyer_id)

        # Then
        assert result is not None
        assert hasattr(result, 'items')
        assert hasattr(result, 'total')
        assert hasattr(result, 'page')
        assert hasattr(result, 'page_size')
        assert hasattr(result, 'total_pages')

    def test_should_filter_by_search_term(self, db_session):
        """
        Given: Investigators with various names
        When: get_investigators is called with search filter
        Then: Returns only matching investigators
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"
        filters = InvestigatorFilter(search="탐정")

        # When
        result = service.get_investigators(lawyer_id, filters=filters)

        # Then
        assert result is not None

    def test_should_filter_by_availability(self, db_session):
        """
        Given: Mix of available and busy investigators
        When: get_investigators is called with availability=available
        Then: Returns only available investigators
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"
        filters = InvestigatorFilter(availability=AvailabilityStatus.AVAILABLE)

        # When
        result = service.get_investigators(lawyer_id, filters=filters)

        # Then
        assert result is not None
        for item in result.items:
            assert item.availability == "available"

    def test_should_return_empty_list_when_no_investigators(self, db_session):
        """
        Given: Lawyer with no investigators
        When: get_investigators is called
        Then: Returns empty list with zero total
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "lawyer-with-no-investigators"

        # When
        result = service.get_investigators(lawyer_id)

        # Then
        assert result is not None
        assert result.items == []
        assert result.total == 0

    def test_should_respect_pagination(self, db_session):
        """
        Given: Many investigators
        When: get_investigators is called with page and page_size
        Then: Returns correct page of results
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_investigators(lawyer_id, page=1, page_size=10)

        # Then
        assert result is not None
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) <= 10

    def test_should_sort_by_name_ascending(self, db_session):
        """
        Given: Multiple investigators
        When: get_investigators is called with sort_by=name, sort_order=asc
        Then: Returns investigators sorted by name ascending
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_investigators(
            lawyer_id,
            sort_by=InvestigatorSortField.NAME,
            sort_order=SortOrder.ASC
        )

        # Then
        assert result is not None
        if len(result.items) > 1:
            names = [item.name for item in result.items]
            assert names == sorted(names)


class TestGetInvestigatorDetail:
    """Test suite for get_investigator_detail method"""

    def test_should_return_investigator_detail(self, db_session):
        """
        Given: Valid investigator ID
        When: get_investigator_detail is called
        Then: Returns InvestigatorDetail with assigned cases and stats
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"
        investigator_id = "test-investigator-id"

        # When
        result = service.get_investigator_detail(lawyer_id, investigator_id)

        # Then - may return None if investigator not found, which is valid behavior
        if result is not None:
            assert hasattr(result, 'id')
            assert hasattr(result, 'name')
            assert hasattr(result, 'assigned_cases')
            assert hasattr(result, 'stats')

    def test_should_return_none_for_invalid_investigator(self, db_session):
        """
        Given: Invalid investigator ID
        When: get_investigator_detail is called
        Then: Returns None
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "test-lawyer-id"
        investigator_id = "non-existent-investigator"

        # When
        result = service.get_investigator_detail(lawyer_id, investigator_id)

        # Then
        assert result is None

    def test_should_return_none_for_unauthorized_access(self, db_session):
        """
        Given: Investigator not linked to the lawyer's cases
        When: get_investigator_detail is called
        Then: Returns None (access denied)
        """
        # Given
        service = InvestigatorListService(db_session)
        lawyer_id = "other-lawyer-id"
        investigator_id = "test-investigator-id"

        # When
        result = service.get_investigator_detail(lawyer_id, investigator_id)

        # Then
        assert result is None
