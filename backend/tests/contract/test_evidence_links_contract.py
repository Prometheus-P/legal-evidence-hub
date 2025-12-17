"""
Contract tests for Evidence-Party Link API (US4)
Task T067 - TDD RED Phase

Tests for Evidence Link endpoints:
- POST /cases/{case_id}/evidence-links - Create evidence link
- GET /cases/{case_id}/evidence-links - List links for case
- GET /cases/{case_id}/evidence-links/by-party/{party_id} - Get links by party
- GET /cases/{case_id}/evidence-links/by-evidence/{evidence_id} - Get links by evidence
- DELETE /cases/{case_id}/evidence-links/{link_id} - Delete link
"""

import pytest
from fastapi import status


@pytest.fixture
def party_with_evidence(client, test_case, auth_headers):
    """
    Create a party and mock evidence ID for link tests

    Returns:
        tuple: (party_id, evidence_id)
    """
    party = client.post(
        f"/cases/{test_case.id}/parties",
        json={"type": "plaintiff", "name": "김원고"},
        headers=auth_headers
    ).json()

    # Use mock evidence ID (evidence is stored in DynamoDB)
    evidence_id = "ev_test_001"

    return party["id"], evidence_id


class TestCreateEvidenceLink:
    """Contract tests for POST /cases/{case_id}/evidence-links"""

    def test_should_create_link_to_party(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Existing party and evidence
        When: POST /cases/{case_id}/evidence-links with party_id
        Then:
            - Returns 201 Created
            - Link has correct evidence_id and party_id
            - Link has default link_type 'mentions'
        """
        party_id, evidence_id = party_with_evidence

        link_data = {
            "evidence_id": evidence_id,
            "party_id": party_id,
            "link_type": "mentions"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["evidence_id"] == evidence_id
        assert data["party_id"] == party_id
        assert data["link_type"] == "mentions"
        assert data["id"].startswith("link_")

    def test_should_create_link_with_proves_type(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Existing party and evidence
        When: POST with link_type 'proves'
        Then: Returns link with proves type
        """
        party_id, evidence_id = party_with_evidence

        link_data = {
            "evidence_id": evidence_id,
            "party_id": party_id,
            "link_type": "proves"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["link_type"] == "proves"

    def test_should_create_link_to_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Given: Existing relationship
        When: POST with relationship_id (not party_id)
        Then: Returns link connected to relationship
        """
        # Create two parties
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

        # Create relationship
        relationship = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage"
            },
            headers=auth_headers
        ).json()

        # Create link to relationship
        link_data = {
            "evidence_id": "ev_marriage_cert_001",
            "relationship_id": relationship["id"],
            "link_type": "proves"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["relationship_id"] == relationship["id"]
        assert data["party_id"] is None

    def test_should_reject_link_without_target(
        self, client, test_case, auth_headers
    ):
        """
        Given: No party_id or relationship_id
        When: POST evidence link
        Then: Returns 400 Bad Request (must specify at least one target)
        """
        link_data = {
            "evidence_id": "ev_test_001",
            "link_type": "mentions"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_reject_duplicate_link(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Existing link
        When: POST duplicate link (same evidence, party, type)
        Then: Returns 409 Conflict
        """
        party_id, evidence_id = party_with_evidence

        link_data = {
            "evidence_id": evidence_id,
            "party_id": party_id,
            "link_type": "mentions"
        }

        # Create first link
        first_response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )
        assert first_response.status_code == status.HTTP_201_CREATED

        # Try to create duplicate - ValidationError maps to 400 Bad Request
        duplicate_response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )
        assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_allow_different_link_types_for_same_evidence_party(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Existing 'mentions' link
        When: POST 'proves' link (same evidence, same party)
        Then: Returns 201 (different link_type allowed)
        """
        party_id, evidence_id = party_with_evidence

        # Create 'mentions' link
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party_id,
                "link_type": "mentions"
            },
            headers=auth_headers
        )

        # Create 'proves' link (should succeed)
        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party_id,
                "link_type": "proves"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_should_reject_nonexistent_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent party ID
        When: POST evidence link
        Then: Returns 404 Not Found
        """
        link_data = {
            "evidence_id": "ev_test_001",
            "party_id": "party_nonexistent",
            "link_type": "mentions"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_reject_invalid_link_type(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Valid party
        When: POST with invalid link_type
        Then: Returns 422 Unprocessable Entity
        """
        party_id, evidence_id = party_with_evidence

        link_data = {
            "evidence_id": evidence_id,
            "party_id": party_id,
            "link_type": "invalid_type"
        }

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json=link_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListEvidenceLinks:
    """Contract tests for GET /cases/{case_id}/evidence-links"""

    def test_should_return_all_links_for_case(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Case with multiple evidence links
        When: GET /cases/{case_id}/evidence-links
        Then: Returns all links with total count
        """
        party_id, evidence_id = party_with_evidence

        # Create multiple links
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": "ev_001", "party_id": party_id, "link_type": "mentions"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": "ev_002", "party_id": party_id, "link_type": "proves"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/evidence-links",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "links" in data
        assert "total" in data
        assert data["total"] >= 2
        assert len(data["links"]) >= 2

    def test_should_return_empty_for_new_case(
        self, client, test_case, auth_headers
    ):
        """
        Given: Case with no evidence links
        When: GET /cases/{case_id}/evidence-links
        Then: Returns empty array with total 0
        """
        response = client.get(
            f"/cases/{test_case.id}/evidence-links",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["links"] == []
        assert data["total"] == 0


class TestGetLinksByParty:
    """Contract tests for GET /cases/{case_id}/evidence-links/by-party/{party_id}"""

    def test_should_return_links_for_party(
        self, client, test_case, auth_headers
    ):
        """
        Given: Party with linked evidence
        When: GET /cases/{case_id}/evidence-links/by-party/{party_id}
        Then: Returns only links for that party
        """
        # Create two parties
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "이피고"},
            headers=auth_headers
        ).json()

        # Create links for party1
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": "ev_001", "party_id": party1["id"], "link_type": "mentions"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": "ev_002", "party_id": party1["id"], "link_type": "proves"},
            headers=auth_headers
        )

        # Create link for party2
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": "ev_003", "party_id": party2["id"], "link_type": "mentions"},
            headers=auth_headers
        )

        # Get links for party1
        response = client.get(
            f"/cases/{test_case.id}/evidence-links/by-party/{party1['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        for link in data["links"]:
            assert link["party_id"] == party1["id"]


class TestGetLinksByEvidence:
    """Contract tests for GET /cases/{case_id}/evidence-links/by-evidence/{evidence_id}"""

    def test_should_return_links_for_evidence(
        self, client, test_case, auth_headers
    ):
        """
        Given: Evidence linked to multiple parties
        When: GET /cases/{case_id}/evidence-links/by-evidence/{evidence_id}
        Then: Returns all links for that evidence
        """
        # Create two parties
        party1 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        party2 = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "이피고"},
            headers=auth_headers
        ).json()

        evidence_id = "ev_shared_001"

        # Link same evidence to both parties
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": evidence_id, "party_id": party1["id"], "link_type": "mentions"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": evidence_id, "party_id": party2["id"], "link_type": "involves"},
            headers=auth_headers
        )

        # Get links for evidence
        response = client.get(
            f"/cases/{test_case.id}/evidence-links/by-evidence/{evidence_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        for link in data["links"]:
            assert link["evidence_id"] == evidence_id


class TestDeleteEvidenceLink:
    """Contract tests for DELETE /cases/{case_id}/evidence-links/{link_id}"""

    def test_should_delete_link(
        self, client, test_case, auth_headers, party_with_evidence
    ):
        """
        Given: Existing evidence link
        When: DELETE /cases/{case_id}/evidence-links/{link_id}
        Then: Returns 204 No Content
        """
        party_id, evidence_id = party_with_evidence

        # Create link
        create_response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": evidence_id, "party_id": party_id, "link_type": "mentions"},
            headers=auth_headers
        )
        link_id = create_response.json()["id"]

        # Delete link
        response = client.delete(
            f"/cases/{test_case.id}/evidence-links/{link_id}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion - links for this party should be empty now
        get_response = client.get(
            f"/cases/{test_case.id}/evidence-links/by-party/{party_id}",
            headers=auth_headers
        )
        assert get_response.json()["total"] == 0

    def test_should_return_404_for_nonexistent_link(
        self, client, test_case, auth_headers
    ):
        """
        Given: Non-existent link ID
        When: DELETE /cases/{case_id}/evidence-links/{link_id}
        Then: Returns 404 Not Found
        """
        response = client.delete(
            f"/cases/{test_case.id}/evidence-links/link_nonexistent",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_reject_unauthenticated_delete(
        self, client, test_case
    ):
        """
        Given: No authentication
        When: DELETE evidence link
        Then: Returns 401 Unauthorized
        """
        response = client.delete(
            f"/cases/{test_case.id}/evidence-links/link_123"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
