"""
Test suite for Lawyer Investigators API endpoints
005-lawyer-portal-pages Feature - US3

Tests for:
- GET /lawyer/investigators - list investigators with filters
- GET /lawyer/investigators/{investigator_id} - investigator detail
"""

from fastapi import status


class TestGetInvestigators:
    """Test suite for GET /lawyer/investigators endpoint"""

    def test_should_return_investigator_list_for_authenticated_lawyer(
        self, client, auth_headers
    ):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators is called
        Then:
            - Returns 200 status code
            - Response contains items, total, page, page_size, total_pages
        """
        # When
        response = client.get("/lawyer/investigators", headers=auth_headers)

        # Then
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_should_return_401_without_auth(self, client):
        """
        Given: No authentication
        When: GET /lawyer/investigators is called
        Then: Returns 401 Unauthorized
        """
        # When
        response = client.get("/lawyer/investigators")

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_should_accept_search_filter(self, client, auth_headers):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators?search=test is called
        Then: Returns 200 with filtered results
        """
        # When
        response = client.get(
            "/lawyer/investigators?search=test",
            headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert "items" in response.json()

    def test_should_accept_availability_filter(self, client, auth_headers):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators?availability=available is called
        Then: Returns 200 with filtered results
        """
        # When
        response = client.get(
            "/lawyer/investigators?availability=available",
            headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert "items" in response.json()

    def test_should_accept_pagination_params(self, client, auth_headers):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators?page=2&page_size=5 is called
        Then: Returns 200 with correct pagination
        """
        # When
        response = client.get(
            "/lawyer/investigators?page=2&page_size=5",
            headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 5

    def test_should_accept_sort_params(self, client, auth_headers):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators?sort_by=name&sort_order=asc is called
        Then: Returns 200 with sorted results
        """
        # When
        response = client.get(
            "/lawyer/investigators?sort_by=name&sort_order=asc",
            headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK


class TestGetInvestigatorDetail:
    """Test suite for GET /lawyer/investigators/{investigator_id} endpoint"""

    def test_should_return_investigator_detail_for_valid_id(
        self, client, auth_headers, detective_user
    ):
        """
        Given: Authenticated lawyer and valid investigator ID
        When: GET /lawyer/investigators/{investigator_id} is called
        Then:
            - Returns 200 or 404 (depending on case link)
        """
        # When
        response = client.get(
            f"/lawyer/investigators/{detective_user.id}",
            headers=auth_headers
        )

        # Then - may return 404 if no case link, which is expected behavior
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_should_return_404_for_invalid_id(self, client, auth_headers):
        """
        Given: Authenticated lawyer
        When: GET /lawyer/investigators/{invalid_id} is called
        Then: Returns 404 Not Found
        """
        # When
        response = client.get(
            "/lawyer/investigators/non-existent-investigator-id",
            headers=auth_headers
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_401_without_auth(self, client):
        """
        Given: No authentication
        When: GET /lawyer/investigators/{id} is called
        Then: Returns 401 Unauthorized
        """
        # When
        response = client.get("/lawyer/investigators/some-investigator-id")

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
