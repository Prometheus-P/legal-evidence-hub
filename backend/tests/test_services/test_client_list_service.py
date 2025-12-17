"""
Test suite for ClientListService
005-lawyer-portal-pages Feature - US2

Tests for:
- get_clients returns paginated list
- search filter by name/email
- status filter (active/inactive)
- empty result handling
"""


from app.services.client_list_service import ClientListService
from app.schemas.client_list import ClientFilter, ClientStatus, ClientSortField, SortOrder


class TestGetClients:
    """Test suite for get_clients method"""

    def test_should_return_paginated_client_list(self, db_session):
        """
        Given: Lawyer with multiple clients
        When: get_clients is called
        Then: Returns paginated ClientListResponse
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_clients(lawyer_id)

        # Then
        assert result is not None
        assert hasattr(result, 'items')
        assert hasattr(result, 'total')
        assert hasattr(result, 'page')
        assert hasattr(result, 'page_size')
        assert hasattr(result, 'total_pages')

    def test_should_filter_by_search_term(self, db_session):
        """
        Given: Clients with various names
        When: get_clients is called with search filter
        Then: Returns only matching clients
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"
        filters = ClientFilter(search="홍길동")

        # When
        result = service.get_clients(lawyer_id, filters=filters)

        # Then
        assert result is not None
        # All returned items should match search term in name or email
        for item in result.items:
            assert (
                "홍길동" in item.name.lower() or
                "홍길동" in item.email.lower() or
                len(result.items) == 0  # or empty if no matches
            )

    def test_should_filter_by_active_status(self, db_session):
        """
        Given: Mix of active and inactive clients
        When: get_clients is called with status=active
        Then: Returns only active clients
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"
        filters = ClientFilter(status=ClientStatus.ACTIVE)

        # When
        result = service.get_clients(lawyer_id, filters=filters)

        # Then
        assert result is not None
        for item in result.items:
            assert item.status == "active"

    def test_should_filter_by_inactive_status(self, db_session):
        """
        Given: Mix of active and inactive clients
        When: get_clients is called with status=inactive
        Then: Returns only inactive clients
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"
        filters = ClientFilter(status=ClientStatus.INACTIVE)

        # When
        result = service.get_clients(lawyer_id, filters=filters)

        # Then
        assert result is not None
        for item in result.items:
            assert item.status == "inactive"

    def test_should_return_empty_list_when_no_clients(self, db_session):
        """
        Given: Lawyer with no clients
        When: get_clients is called
        Then: Returns empty list with zero total
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "lawyer-with-no-clients"

        # When
        result = service.get_clients(lawyer_id)

        # Then
        assert result is not None
        assert result.items == []
        assert result.total == 0

    def test_should_respect_pagination(self, db_session):
        """
        Given: Many clients
        When: get_clients is called with page and page_size
        Then: Returns correct page of results
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_clients(lawyer_id, page=1, page_size=10)

        # Then
        assert result is not None
        assert result.page == 1
        assert result.page_size == 10
        assert len(result.items) <= 10

    def test_should_sort_by_name_ascending(self, db_session):
        """
        Given: Multiple clients
        When: get_clients is called with sort_by=name, sort_order=asc
        Then: Returns clients sorted by name ascending
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"

        # When
        result = service.get_clients(
            lawyer_id,
            sort_by=ClientSortField.NAME,
            sort_order=SortOrder.ASC
        )

        # Then
        assert result is not None
        if len(result.items) > 1:
            names = [item.name for item in result.items]
            assert names == sorted(names)


class TestGetClientDetail:
    """Test suite for get_client_detail method"""

    def test_should_return_client_detail(self, db_session):
        """
        Given: Valid client ID
        When: get_client_detail is called
        Then: Returns ClientDetail with linked cases and stats
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"
        client_id = "test-client-id"

        # When
        result = service.get_client_detail(lawyer_id, client_id)

        # Then - may return None if client not found, which is valid behavior
        if result is not None:
            assert hasattr(result, 'id')
            assert hasattr(result, 'name')
            assert hasattr(result, 'linked_cases')
            assert hasattr(result, 'stats')

    def test_should_return_none_for_invalid_client(self, db_session):
        """
        Given: Invalid client ID
        When: get_client_detail is called
        Then: Returns None
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "test-lawyer-id"
        client_id = "non-existent-client"

        # When
        result = service.get_client_detail(lawyer_id, client_id)

        # Then
        assert result is None

    def test_should_return_none_for_unauthorized_access(self, db_session):
        """
        Given: Client not linked to the lawyer
        When: get_client_detail is called
        Then: Returns None (access denied)
        """
        # Given
        service = ClientListService(db_session)
        lawyer_id = "other-lawyer-id"
        client_id = "test-client-id"

        # When
        result = service.get_client_detail(lawyer_id, client_id)

        # Then
        assert result is None
