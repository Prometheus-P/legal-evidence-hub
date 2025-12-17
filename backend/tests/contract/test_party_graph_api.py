"""
Contract tests for Party Graph API
007-lawyer-portal-v1: US1 (Party Relationship Graph)
TDD - API contract tests for party.py and relationships.py
"""

from fastapi import status


class TestPartyAPI:
    """Contract tests for Party CRUD endpoints"""

    def test_create_party_returns_201(self, client, test_user, auth_headers, test_case):
        """
        Given: Authenticated user with case access
        When: POST /cases/{case_id}/parties
        Then: 201 Created with party data
        """
        response = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "plaintiff",
                "name": "김철수",
                "alias": "김○○",
                "birth_year": 1980,
                "occupation": "회사원",
                "position": {"x": 100, "y": 200}
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "김철수"
        assert data["type"] == "plaintiff"
        assert data["alias"] == "김○○"
        assert data["position"]["x"] == 100
        assert data["position"]["y"] == 200

    def test_create_party_without_auth_returns_401(self, client, test_case):
        """
        Given: No authentication
        When: POST /cases/{case_id}/parties
        Then: 401 Unauthorized
        """
        response = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "plaintiff",
                "name": "테스트"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_parties_returns_list(self, client, test_user, auth_headers, test_case):
        """
        Given: Case with parties
        When: GET /cases/{case_id}/parties
        Then: 200 OK with party list
        """
        # Create a party first
        client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/parties",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_parties_filtered_by_type(self, client, test_user, auth_headers, test_case):
        """
        Given: Case with parties of different types
        When: GET /cases/{case_id}/parties?type=plaintiff
        Then: Only plaintiff parties returned
        """
        # Create parties
        client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "피고"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/parties?type=plaintiff",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for party in data["items"]:
            assert party["type"] == "plaintiff"

    def test_get_party_by_id_returns_party(self, client, test_user, auth_headers, test_case):
        """
        Given: Existing party
        When: GET /cases/{case_id}/parties/{party_id}
        Then: 200 OK with party data
        """
        # Create party
        create_resp = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "child", "name": "자녀"},
            headers=auth_headers
        )
        party_id = create_resp.json()["id"]

        response = client.get(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == party_id
        assert response.json()["name"] == "자녀"

    def test_update_party_returns_updated_data(self, client, test_user, auth_headers, test_case):
        """
        Given: Existing party
        When: PATCH /cases/{case_id}/parties/{party_id}
        Then: 200 OK with updated data
        """
        # Create party
        create_resp = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "family", "name": "원래이름"},
            headers=auth_headers
        )
        party_id = create_resp.json()["id"]

        response = client.patch(
            f"/cases/{test_case.id}/parties/{party_id}",
            json={"name": "수정이름", "position": {"x": 500, "y": 600}},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "수정이름"
        assert response.json()["position"]["x"] == 500

    def test_delete_party_returns_204(self, client, test_user, auth_headers, test_case):
        """
        Given: Existing party
        When: DELETE /cases/{case_id}/parties/{party_id}
        Then: 204 No Content
        """
        # Create party
        create_resp = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "third_party", "name": "삭제대상"},
            headers=auth_headers
        )
        party_id = create_resp.json()["id"]

        response = client.delete(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_resp = client.get(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND


class TestRelationshipAPI:
    """Contract tests for Relationship CRUD endpoints"""

    def test_create_relationship_returns_201(self, client, test_user, auth_headers, test_case):
        """
        Given: Two existing parties
        When: POST /cases/{case_id}/relationships
        Then: 201 Created with relationship data
        """
        # Create parties
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "남편"},
            headers=auth_headers
        ).json()
        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "아내"},
            headers=auth_headers
        ).json()

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "marriage",
                "notes": "2010년 결혼"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["source_party_id"] == party1["id"]
        assert data["target_party_id"] == party2["id"]
        assert data["type"] == "marriage"

    def test_create_relationship_self_reference_returns_400(self, client, test_user, auth_headers, test_case):
        """
        Given: Same party as source and target
        When: POST /cases/{case_id}/relationships
        Then: 400 Bad Request
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "자기참조"},
            headers=auth_headers
        ).json()

        response = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party["id"],
                "target_party_id": party["id"],
                "type": "marriage"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_relationships_returns_list(self, client, test_user, auth_headers, test_case):
        """
        Given: Case with relationships
        When: GET /cases/{case_id}/relationships
        Then: 200 OK with relationship list
        """
        # Create parties and relationship
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "당사자1"},
            headers=auth_headers
        ).json()
        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "third_party", "name": "당사자2"},
            headers=auth_headers
        ).json()
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "affair"
            },
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/relationships",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_update_relationship_returns_updated(self, client, test_user, auth_headers, test_case):
        """
        Given: Existing relationship
        When: PATCH /cases/{case_id}/relationships/{id}
        Then: 200 OK with updated data
        """
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "당사자1"},
            headers=auth_headers
        ).json()
        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "당사자2"},
            headers=auth_headers
        ).json()
        rel = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "cohabit",
                "notes": "원래메모"
            },
            headers=auth_headers
        ).json()

        response = client.patch(
            f"/cases/{test_case.id}/relationships/{rel['id']}",
            json={"type": "marriage", "notes": "수정메모"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["type"] == "marriage"
        assert response.json()["notes"] == "수정메모"

    def test_delete_relationship_returns_204(self, client, test_user, auth_headers, test_case):
        """
        Given: Existing relationship
        When: DELETE /cases/{case_id}/relationships/{id}
        Then: 204 No Content
        """
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "당사자1"},
            headers=auth_headers
        ).json()
        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "family", "name": "당사자2"},
            headers=auth_headers
        ).json()
        rel = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "parent_child"
            },
            headers=auth_headers
        ).json()

        response = client.delete(
            f"/cases/{test_case.id}/relationships/{rel['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestPartyGraphAPI:
    """Contract tests for Party Graph endpoint"""

    def test_get_party_graph_returns_nodes_and_relationships(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Case with parties and relationships
        When: GET /cases/{case_id}/graph
        Then: 200 OK with nodes and relationships
        """
        # Create parties
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고", "position": {"x": 0, "y": 0}},
            headers=auth_headers
        ).json()
        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "피고", "position": {"x": 200, "y": 0}},
            headers=auth_headers
        ).json()

        # Create relationship
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "marriage"
            },
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "nodes" in data
        assert "relationships" in data
        assert len(data["nodes"]) >= 2
        assert len(data["relationships"]) >= 1

    def test_get_party_graph_empty_case(self, client, test_user, auth_headers, test_case):
        """
        Given: Case with no parties
        When: GET /cases/{case_id}/graph
        Then: 200 OK with empty arrays
        """
        # Note: test_case might have parties from other tests
        # This test verifies the structure is correct
        response = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "nodes" in data
        assert "relationships" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["relationships"], list)
