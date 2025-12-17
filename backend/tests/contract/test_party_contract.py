"""
Contract tests for Party Graph API (US1)
Task T031 - TDD RED Phase

Tests for Party CRUD endpoints:
- GET /cases/{case_id}/parties - List party nodes
- POST /cases/{case_id}/parties - Create party node
- GET /cases/{case_id}/parties/{party_id} - Get party by ID
- PATCH /cases/{case_id}/parties/{party_id} - Update party
- DELETE /cases/{case_id}/parties/{party_id} - Delete party
- GET /cases/{case_id}/graph - Get full graph (parties + relationships)
"""

from fastapi import status


class TestListParties:
    """Contract tests for GET /cases/{case_id}/parties"""

    def test_should_return_empty_list_for_new_case(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer with access to case
        When: GET /cases/{case_id}/parties (no parties exist)
        Then:
            - Returns 200 status code
            - Response contains empty items array
            - Response contains total count of 0
        """
        response = client.get(
            f"/cases/{test_case.id}/parties",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 0
        assert "total" in data
        assert data["total"] == 0

    def test_should_reject_unauthenticated_request(self, client, test_case):
        """
        Given: No authentication
        When: GET /cases/{case_id}/parties
        Then: Returns 401 Unauthorized
        """
        response = client.get(f"/cases/{test_case.id}/parties")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateParty:
    """Contract tests for POST /cases/{case_id}/parties"""

    def test_should_create_plaintiff_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer with write access
        When: POST /cases/{case_id}/parties with plaintiff data
        Then:
            - Returns 201 Created
            - Response contains party with correct type and name
            - Party has generated ID starting with 'party_'
        """
        party_data = {
            "type": "plaintiff",
            "name": "김원고",
            "alias": "원고",
            "birth_year": 1985,
            "occupation": "회사원",
            "position": {"x": 100, "y": 100}
        }

        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"].startswith("party_")
        assert data["type"] == "plaintiff"
        assert data["name"] == "김원고"
        assert data["alias"] == "원고"
        assert data["birth_year"] == 1985
        assert data["case_id"] == test_case.id

    def test_should_create_defendant_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer with write access
        When: POST /cases/{case_id}/parties with defendant data
        Then: Returns 201 with defendant party
        """
        party_data = {
            "type": "defendant",
            "name": "이피고",
            "position": {"x": 300, "y": 100}
        }

        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "defendant"
        assert data["name"] == "이피고"

    def test_should_create_third_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer with write access
        When: POST /cases/{case_id}/parties with third_party type
        Then: Returns 201 with third party node
        """
        party_data = {
            "type": "third_party",
            "name": "박상간",
            "alias": "상간자"
        }

        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "third_party"

    def test_should_reject_invalid_party_type(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer
        When: POST with invalid party type
        Then: Returns 422 Unprocessable Entity
        """
        party_data = {
            "type": "invalid_type",
            "name": "테스트"
        }

        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_should_reject_missing_name(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated lawyer
        When: POST without required name field
        Then: Returns 422 Unprocessable Entity
        """
        party_data = {
            "type": "plaintiff"
        }

        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_should_reject_unauthenticated_create(self, client, test_case):
        """
        Given: No authentication
        When: POST /cases/{case_id}/parties
        Then: Returns 401 Unauthorized
        """
        party_data = {"type": "plaintiff", "name": "테스트"}
        response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetPartyById:
    """Contract tests for GET /cases/{case_id}/parties/{party_id}"""

    def test_should_get_party_by_id(
        self, client, test_case, auth_headers
    ):
        """
        Given: Existing party in case
        When: GET /cases/{case_id}/parties/{party_id}
        Then: Returns party details with all fields
        """
        # First create a party
        party_data = {"type": "plaintiff", "name": "김원고"}
        create_response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )
        created_party = create_response.json()

        # Then get it
        response = client.get(
            f"/cases/{test_case.id}/parties/{created_party['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_party["id"]
        assert data["name"] == "김원고"
        assert "created_at" in data
        assert "updated_at" in data

    def test_should_return_404_for_nonexistent_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent party ID
        When: GET /cases/{case_id}/parties/{party_id}
        Then: Returns 404 Not Found
        """
        response = client.get(
            f"/cases/{test_case.id}/parties/party_nonexistent123",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateParty:
    """Contract tests for PATCH /cases/{case_id}/parties/{party_id}"""

    def test_should_update_party_name(
        self, client, test_case, auth_headers
    ):
        """
        Given: Existing party
        When: PATCH with new name
        Then: Returns updated party with new name
        """
        # Create party
        party_data = {"type": "plaintiff", "name": "김원고"}
        create_response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )
        party_id = create_response.json()["id"]

        # Update name
        update_data = {"name": "김개명"}
        response = client.patch(
            f"/cases/{test_case.id}/parties/{party_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "김개명"
        assert data["type"] == "plaintiff"  # Type unchanged

    def test_should_update_party_position(
        self, client, test_case, auth_headers
    ):
        """
        Given: Existing party
        When: PATCH with new position
        Then: Returns updated party with new position
        """
        # Create party
        party_data = {"type": "plaintiff", "name": "김원고", "position": {"x": 0, "y": 0}}
        create_response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )
        party_id = create_response.json()["id"]

        # Update position
        update_data = {"position": {"x": 200, "y": 300}}
        response = client.patch(
            f"/cases/{test_case.id}/parties/{party_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["position"]["x"] == 200
        assert data["position"]["y"] == 300


class TestDeleteParty:
    """Contract tests for DELETE /cases/{case_id}/parties/{party_id}"""

    def test_should_delete_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Existing party
        When: DELETE /cases/{case_id}/parties/{party_id}
        Then: Returns 204 No Content
        """
        # Create party
        party_data = {"type": "plaintiff", "name": "삭제될당사자"}
        create_response = client.post(
            f"/cases/{test_case.id}/parties",
            json=party_data,
            headers=auth_headers
        )
        party_id = create_response.json()["id"]

        # Delete party
        response = client.delete(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_404_for_deleting_nonexistent_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent party ID
        When: DELETE /cases/{case_id}/parties/{party_id}
        Then: Returns 404 Not Found
        """
        response = client.delete(
            f"/cases/{test_case.id}/parties/party_nonexistent123",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetGraph:
    """Contract tests for GET /cases/{case_id}/graph"""

    def test_should_return_graph_with_parties_and_relationships(
        self, client, test_case, auth_headers
    ):
        """
        Given: Case with parties and relationships
        When: GET /cases/{case_id}/graph
        Then:
            - Returns 200
            - Response contains parties array
            - Response contains relationships array
        """
        # Create two parties
        client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "이피고"},
            headers=auth_headers
        )

        # Get graph
        response = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # API returns "nodes" for React Flow compatibility
        assert "nodes" in data
        assert "relationships" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["relationships"], list)
        assert len(data["nodes"]) == 2

    def test_should_return_empty_graph_for_new_case(
        self, client, test_case, auth_headers
    ):
        """
        Given: Case with no parties
        When: GET /cases/{case_id}/graph
        Then: Returns empty nodes and relationships arrays
        """
        response = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # API returns "nodes" for React Flow compatibility
        assert data["nodes"] == []
        assert data["relationships"] == []
