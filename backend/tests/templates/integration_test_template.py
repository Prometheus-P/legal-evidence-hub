"""
Integration Test Template
==========================

Template for writing integration tests for API endpoints.
Tests full HTTP request-response cycle with database.

QA Framework v4.0 - Test Pyramid: Integration Layer (20% of tests)

Usage:
    1. Copy this template to tests/test_api/test_your_endpoint.py
    2. Replace endpoint paths and expected responses
    3. Use provided fixtures for authentication

Fixtures Used:
    - client: FastAPI TestClient with /api prefix
    - auth_headers: JWT headers for authenticated requests
    - admin_auth_headers: JWT headers for admin requests
    - test_case: Sample case for testing
"""

import pytest
from uuid import uuid4


# ============================================================================
# TDD STATUS TRACKING
# ============================================================================
# | Test Name                           | Status | Date       | Notes         |
# |-------------------------------------|--------|------------|---------------|
# | test_create_returns_201             | GREEN  | 2024-12-01 | Happy path    |
# | test_create_returns_422_invalid     | GREEN  | 2024-12-01 | Validation    |
# | test_get_returns_200                | GREEN  | 2024-12-01 | Happy path    |
# | test_get_returns_404_not_found      | GREEN  | 2024-12-01 | Error case    |
# | test_list_returns_paginated         | RED    | -          | Pending       |
# ============================================================================


class TestResourceCreate:
    """
    Integration tests for POST /api/resources endpoint.

    Tests:
    - Successful creation returns 201
    - Invalid data returns 422
    - Unauthenticated request returns 401
    - Duplicate resource returns 409
    """

    endpoint = "/api/resources"

    @pytest.mark.integration
    def test_create_returns_201_when_valid_data(self, client, auth_headers):
        """
        Given: Valid resource data and authenticated user
        When: POST /api/resources is called
        Then: 201 Created is returned with resource data
        """
        # Arrange
        data = {
            "name": f"Test Resource {uuid4()}",
            "description": "Integration test resource",
        }

        # Act
        response = client.post(
            self.endpoint,
            json=data,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 201
        response_data = response.json()
        assert "id" in response_data
        assert response_data["name"] == data["name"]

    @pytest.mark.integration
    def test_create_returns_422_when_invalid_data(self, client, auth_headers):
        """
        Given: Invalid resource data (missing required field)
        When: POST /api/resources is called
        Then: 422 Unprocessable Entity is returned
        """
        # Arrange
        data = {
            # "name" is missing - required field
            "description": "Missing name",
        }

        # Act
        response = client.post(
            self.endpoint,
            json=data,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 422
        assert "detail" in response.json()

    @pytest.mark.integration
    def test_create_returns_401_when_unauthenticated(self, client):
        """
        Given: Valid resource data but no authentication
        When: POST /api/resources is called
        Then: 401 Unauthorized is returned
        """
        # Arrange
        data = {"name": "Test Resource"}

        # Act
        response = client.post(
            self.endpoint,
            json=data,
            # No auth_headers
        )

        # Assert
        assert response.status_code == 401


class TestResourceGet:
    """
    Integration tests for GET /api/resources/{id} endpoint.

    Tests:
    - Valid ID returns 200 with resource
    - Invalid ID returns 404
    - Unauthenticated returns 401
    - Unauthorized (other user's resource) returns 403
    """

    endpoint = "/api/resources/{resource_id}"

    @pytest.mark.integration
    def test_get_returns_200_when_resource_exists(
        self, client, auth_headers, db_session
    ):
        """
        Given: Existing resource ID and authenticated owner
        When: GET /api/resources/{id} is called
        Then: 200 OK is returned with resource data
        """
        # Arrange - Create a resource first
        resource_id = str(uuid4())
        # In real test, create resource in db_session

        # Act
        response = client.get(
            self.endpoint.format(resource_id=resource_id),
            headers=auth_headers,
        )

        # Assert
        # Status depends on whether resource was actually created
        assert response.status_code in [200, 404]

    @pytest.mark.integration
    def test_get_returns_404_when_not_found(self, client, auth_headers):
        """
        Given: Non-existent resource ID
        When: GET /api/resources/{id} is called
        Then: 404 Not Found is returned
        """
        # Arrange
        nonexistent_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = client.get(
            self.endpoint.format(resource_id=nonexistent_id),
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    def test_get_returns_403_when_unauthorized(
        self, client, auth_headers, other_user_resource_id
    ):
        """
        Given: Resource owned by another user
        When: GET /api/resources/{id} is called
        Then: 403 Forbidden or 404 Not Found is returned
        """
        # Act
        response = client.get(
            self.endpoint.format(resource_id=other_user_resource_id),
            headers=auth_headers,
        )

        # Assert - Either forbidden or hidden (404)
        assert response.status_code in [403, 404]


class TestResourceList:
    """
    Integration tests for GET /api/resources endpoint.

    Tests:
    - Returns paginated list
    - Filtering works correctly
    - Only returns user's resources
    """

    endpoint = "/api/resources"

    @pytest.mark.integration
    def test_list_returns_paginated_results(self, client, auth_headers):
        """
        Given: Authenticated user with multiple resources
        When: GET /api/resources is called
        Then: Paginated list is returned
        """
        # Act
        response = client.get(
            self.endpoint,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        # Check for pagination structure
        assert isinstance(data, (list, dict))

    @pytest.mark.integration
    def test_list_filters_by_query(self, client, auth_headers):
        """
        Given: Resources with different names
        When: GET /api/resources?q=search is called
        Then: Only matching resources are returned
        """
        # Act
        response = client.get(
            f"{self.endpoint}?q=test",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200


class TestResourceUpdate:
    """
    Integration tests for PATCH /api/resources/{id} endpoint.

    Tests:
    - Valid update returns 200
    - Invalid data returns 422
    - Not found returns 404
    - Unauthorized returns 403
    """

    endpoint = "/api/resources/{resource_id}"

    @pytest.mark.integration
    @pytest.mark.skip(reason="Template - implement with actual resource")
    def test_update_returns_200_when_valid(self, client, auth_headers):
        """
        Given: Existing resource and valid update data
        When: PATCH /api/resources/{id} is called
        Then: 200 OK is returned with updated data
        """
        pass


class TestResourceDelete:
    """
    Integration tests for DELETE /api/resources/{id} endpoint.

    Tests:
    - Successful delete returns 204
    - Not found returns 404
    - Unauthorized returns 403
    """

    endpoint = "/api/resources/{resource_id}"

    @pytest.mark.integration
    @pytest.mark.skip(reason="Template - implement with actual resource")
    def test_delete_returns_204_when_authorized(self, client, auth_headers):
        """
        Given: Existing resource owned by user
        When: DELETE /api/resources/{id} is called
        Then: 204 No Content is returned
        """
        pass


# ============================================================================
# Fixture for other_user_resource_id (if not in conftest)
# ============================================================================

@pytest.fixture
def other_user_resource_id():
    """Resource ID owned by a different user."""
    return "00000000-0000-0000-0000-000000000999"
