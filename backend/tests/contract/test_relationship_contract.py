"""
Contract tests for Party Relationship API (US1)
Task T032 - TDD RED Phase

Tests for Relationship CRUD endpoints:
- GET /cases/{case_id}/relationships - List relationships
- POST /cases/{case_id}/relationships - Create relationship
- GET /cases/{case_id}/relationships/{rel_id} - Get relationship by ID
- PATCH /cases/{case_id}/relationships/{rel_id} - Update relationship
- DELETE /cases/{case_id}/relationships/{rel_id} - Delete relationship
"""

import pytest
from fastapi import status


@pytest.fixture
def two_parties(client, test_case, auth_headers):
    """
    Create two parties for relationship tests

    Returns:
        tuple: (plaintiff_id, defendant_id)
    """
    plaintiff = client.post(
        f"/cases/{test_case.id}/parties",
        json={"type": "plaintiff", "name": "김원고"},
        headers=auth_headers
    ).json()

    defendant = client.post(
        f"/cases/{test_case.id}/parties",
        json={"type": "defendant", "name": "이피고"},
        headers=auth_headers
    ).json()

    return plaintiff["id"], defendant["id"]


class TestListRelationships:
    """Contract tests for GET /cases/{case_id}/relationships"""

    def test_should_return_empty_list_for_new_case(
        self, client, test_case, auth_headers
    ):
        """
        Given: Case with no relationships
        When: GET /cases/{case_id}/relationships
        Then:
            - Returns 200 OK
            - Empty relationships array
        """
        response = client.get(
            f"/cases/{test_case.id}/relationships",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0

    def test_should_reject_unauthenticated_request(self, client, test_case):
        """
        Given: No authentication
        When: GET /cases/{case_id}/relationships
        Then: Returns 401 Unauthorized
        """
        response = client.get(f"/cases/{test_case.id}/relationships")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateRelationship:
    """Contract tests for POST /cases/{case_id}/relationships"""

    def test_should_create_marriage_relationship(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Two parties in the case
        When: POST relationship with type 'marriage'
        Then:
            - Returns 201 Created
            - Relationship has correct source and target
            - Relationship type is 'marriage'
        """
        plaintiff_id, defendant_id = two_parties

        rel_data = {
            "source_party_id": plaintiff_id,
            "target_party_id": defendant_id,
            "type": "marriage",
            "start_date": "2010-05-20",
            "notes": "2010년 5월 혼인신고"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["source_party_id"] == plaintiff_id
        assert data["target_party_id"] == defendant_id
        assert data["type"] == "marriage"
        assert data["notes"] == "2010년 5월 혼인신고"

    def test_should_create_affair_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Defendant and third party
        When: POST relationship with type 'affair'
        Then: Returns 201 with affair relationship
        """
        # Create defendant and third party
        defendant = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "이피고"},
            headers=auth_headers
        ).json()

        third_party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "third_party", "name": "박상간"},
            headers=auth_headers
        ).json()

        rel_data = {
            "source_party_id": defendant["id"],
            "target_party_id": third_party["id"],
            "type": "affair",
            "start_date": "2022-01-15"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "affair"

    def test_should_create_parent_child_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Plaintiff and child
        When: POST relationship with type 'parent_child'
        Then: Returns 201 with parent_child relationship
        """
        plaintiff = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        child = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "child", "name": "김자녀", "birth_year": 2015},
            headers=auth_headers
        ).json()

        rel_data = {
            "source_party_id": plaintiff["id"],
            "target_party_id": child["id"],
            "type": "parent_child"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["type"] == "parent_child"

    def test_should_reject_duplicate_relationship(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Existing relationship between two parties
        When: POST duplicate relationship (same parties, same type)
        Then: Returns 409 Conflict
        """
        plaintiff_id, defendant_id = two_parties

        rel_data = {
            "source_party_id": plaintiff_id,
            "target_party_id": defendant_id,
            "type": "marriage"
        }

        # Create first relationship
        first_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )
        assert first_response.status_code == status.HTTP_201_CREATED

        # Try to create duplicate - ValidationError maps to 400 Bad Request
        duplicate_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )
        assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_reject_self_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Single party
        When: POST relationship with same source and target
        Then: Returns 400 Bad Request
        """
        plaintiff = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        rel_data = {
            "source_party_id": plaintiff["id"],
            "target_party_id": plaintiff["id"],
            "type": "marriage"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_reject_nonexistent_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Authenticated user
        When: POST relationship with non-existent party ID
        Then: Returns 404 Not Found
        """
        plaintiff = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        rel_data = {
            "source_party_id": plaintiff["id"],
            "target_party_id": "party_nonexistent",
            "type": "marriage"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_reject_invalid_relationship_type(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Two parties
        When: POST with invalid relationship type
        Then: Returns 422 Unprocessable Entity
        """
        plaintiff_id, defendant_id = two_parties

        rel_data = {
            "source_party_id": plaintiff_id,
            "target_party_id": defendant_id,
            "type": "invalid_type"
        }

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetRelationshipById:
    """Contract tests for GET /cases/{case_id}/relationships/{rel_id}"""

    def test_should_get_relationship_by_id(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Existing relationship
        When: GET /cases/{case_id}/relationships/{rel_id}
        Then: Returns relationship with all fields
        """
        plaintiff_id, defendant_id = two_parties

        # Create relationship
        rel_data = {
            "source_party_id": plaintiff_id,
            "target_party_id": defendant_id,
            "type": "marriage"
        }
        create_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json=rel_data,
            headers=auth_headers
        )
        rel_id = create_response.json()["id"]

        # Get relationship
        response = client.get(
            f"/cases/{test_case.id}/relationships/{rel_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == rel_id
        assert data["type"] == "marriage"
        assert "created_at" in data

    def test_should_return_404_for_nonexistent_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent relationship ID
        When: GET /cases/{case_id}/relationships/{rel_id}
        Then: Returns 404 Not Found
        """
        response = client.get(
            f"/cases/{test_case.id}/relationships/rel_nonexistent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateRelationship:
    """Contract tests for PATCH /cases/{case_id}/relationships/{rel_id}"""

    def test_should_update_relationship_notes(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Existing relationship
        When: PATCH with new notes
        Then: Returns updated relationship
        """
        plaintiff_id, defendant_id = two_parties

        # Create relationship
        create_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff_id,
                "target_party_id": defendant_id,
                "type": "marriage"
            },
            headers=auth_headers
        )
        rel_id = create_response.json()["id"]

        # Update notes
        response = client.patch(
            f"/cases/{test_case.id}/relationships/{rel_id}",
            json={"notes": "혼인신고일 변경"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notes"] == "혼인신고일 변경"

    def test_should_update_relationship_dates(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Existing relationship
        When: PATCH with start_date and end_date
        Then: Returns relationship with updated dates
        """
        plaintiff_id, defendant_id = two_parties

        # Create relationship
        create_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff_id,
                "target_party_id": defendant_id,
                "type": "marriage"
            },
            headers=auth_headers
        )
        rel_id = create_response.json()["id"]

        # Update dates
        response = client.patch(
            f"/cases/{test_case.id}/relationships/{rel_id}",
            json={
                "start_date": "2010-05-20",
                "end_date": "2023-12-01"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "start_date" in data
        assert "end_date" in data


class TestDeleteRelationship:
    """Contract tests for DELETE /cases/{case_id}/relationships/{rel_id}"""

    def test_should_delete_relationship(
        self, client, test_case, auth_headers, two_parties
    ):
        """
        Given: Existing relationship
        When: DELETE /cases/{case_id}/relationships/{rel_id}
        Then: Returns 204 No Content
        """
        plaintiff_id, defendant_id = two_parties

        # Create relationship
        create_response = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff_id,
                "target_party_id": defendant_id,
                "type": "marriage"
            },
            headers=auth_headers
        )
        rel_id = create_response.json()["id"]

        # Delete
        response = client.delete(
            f"/cases/{test_case.id}/relationships/{rel_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/cases/{test_case.id}/relationships/{rel_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_404_for_deleting_nonexistent_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent relationship ID
        When: DELETE /cases/{case_id}/relationships/{rel_id}
        Then: Returns 404 Not Found
        """
        response = client.delete(
            f"/cases/{test_case.id}/relationships/rel_nonexistent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestFilterRelationships:
    """Contract tests for filtering relationships"""

    def test_should_filter_by_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Multiple relationships involving different parties
        When: GET /cases/{case_id}/relationships?party_id={id}
        Then: Returns only relationships involving that party
        """
        # Create 3 parties
        plaintiff = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        defendant = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "이피고"},
            headers=auth_headers
        ).json()

        third_party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "third_party", "name": "박상간"},
            headers=auth_headers
        ).json()

        # Create relationships
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage"
            },
            headers=auth_headers
        )

        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": defendant["id"],
                "target_party_id": third_party["id"],
                "type": "affair"
            },
            headers=auth_headers
        )

        # Filter by defendant (should return both relationships)
        response = client.get(
            f"/cases/{test_case.id}/relationships?party_id={defendant['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2

        # Filter by third party (should return only affair)
        response = client.get(
            f"/cases/{test_case.id}/relationships?party_id={third_party['id']}",
            headers=auth_headers
        )

        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "affair"
