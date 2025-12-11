"""
Contract tests for Evidence Links API
007-lawyer-portal-v1: US4 (Evidence-Party Linking)
TDD - API contract tests for evidence_links.py
"""

from fastapi import status
import uuid


class TestEvidenceLinksAPI:
    """Contract tests for Evidence Links CRUD endpoints"""

    def test_create_evidence_link_to_party_returns_201(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Existing party and evidence_id
        When: POST /cases/{case_id}/evidence-links
        Then: 201 Created with link data
        """
        # Create party
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고"},
            headers=auth_headers
        ).json()

        evidence_id = f"ev_{uuid.uuid4().hex[:8]}"

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "proves"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["evidence_id"] == evidence_id
        assert data["party_id"] == party["id"]
        assert data["link_type"] == "proves"
        assert data["relationship_id"] is None

    def test_create_evidence_link_to_relationship_returns_201(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Existing relationship and evidence_id
        When: POST /cases/{case_id}/evidence-links with relationship_id
        Then: 201 Created with link data
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
        rel = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": party1["id"],
                "target_party_id": party2["id"],
                "type": "affair"
            },
            headers=auth_headers
        ).json()

        evidence_id = f"ev_rel_{uuid.uuid4().hex[:8]}"

        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "relationship_id": rel["id"],
                "link_type": "proves"
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["relationship_id"] == rel["id"]
        assert data["party_id"] is None

    def test_create_evidence_link_no_target_returns_400(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: No party_id or relationship_id
        When: POST /cases/{case_id}/evidence-links
        Then: 400 Bad Request
        """
        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": "ev_no_target",
                "link_type": "mentions"
                # No party_id or relationship_id
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_evidence_link_without_auth_returns_401(self, client, test_case):
        """
        Given: No authentication
        When: POST /cases/{case_id}/evidence-links
        Then: 401 Unauthorized
        """
        response = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": "ev_test",
                "party_id": "party_test",
                "link_type": "mentions"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_evidence_links_returns_list(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Case with evidence links
        When: GET /cases/{case_id}/evidence-links
        Then: 200 OK with link list
        """
        # Create party and link
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "피고"},
            headers=auth_headers
        ).json()

        evidence_id = f"ev_list_{uuid.uuid4().hex[:8]}"
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "mentions"
            },
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
        assert data["total"] >= 1

    def test_get_evidence_links_filtered_by_evidence_id(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Multiple evidence links
        When: GET /cases/{case_id}/evidence-links?evidence_id={id}
        Then: Only links for that evidence returned
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고"},
            headers=auth_headers
        ).json()

        target_ev = f"target_ev_{uuid.uuid4().hex[:8]}"
        other_ev = f"other_ev_{uuid.uuid4().hex[:8]}"

        # Create links
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": target_ev, "party_id": party["id"], "link_type": "proves"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": other_ev, "party_id": party["id"], "link_type": "mentions"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/evidence-links?evidence_id={target_ev}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for link in data["links"]:
            assert link["evidence_id"] == target_ev

    def test_get_evidence_links_filtered_by_party_id(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Links to different parties
        When: GET /cases/{case_id}/evidence-links?party_id={id}
        Then: Only links to that party returned
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

        ev1 = f"ev1_{uuid.uuid4().hex[:8]}"
        ev2 = f"ev2_{uuid.uuid4().hex[:8]}"

        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": ev1, "party_id": party1["id"], "link_type": "proves"},
            headers=auth_headers
        )
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": ev2, "party_id": party2["id"], "link_type": "mentions"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/evidence-links?party_id={party1['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for link in data["links"]:
            assert link["party_id"] == party1["id"]

    def test_get_evidence_link_by_id(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Existing link
        When: GET /cases/{case_id}/evidence-links/{link_id}
        Then: 200 OK with link data
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "child", "name": "자녀"},
            headers=auth_headers
        ).json()

        evidence_id = f"ev_get_{uuid.uuid4().hex[:8]}"
        link = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "involves"
            },
            headers=auth_headers
        ).json()

        response = client.get(
            f"/cases/{test_case.id}/evidence-links/{link['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == link["id"]
        assert response.json()["link_type"] == "involves"

    def test_delete_evidence_link_returns_204(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Existing link
        When: DELETE /cases/{case_id}/evidence-links/{link_id}
        Then: 204 No Content
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "family", "name": "가족"},
            headers=auth_headers
        ).json()

        evidence_id = f"ev_del_{uuid.uuid4().hex[:8]}"
        link = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "contradicts"
            },
            headers=auth_headers
        ).json()

        response = client.delete(
            f"/cases/{test_case.id}/evidence-links/{link['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_resp = client.get(
            f"/cases/{test_case.id}/evidence-links/{link['id']}",
            headers=auth_headers
        )
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND


class TestEvidenceLinksConvenienceEndpoints:
    """Contract tests for convenience endpoints"""

    def test_get_links_by_evidence_returns_filtered(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Links for specific evidence
        When: GET /cases/{case_id}/evidence-links/by-evidence/{evidence_id}
        Then: 200 OK with filtered links
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "원고"},
            headers=auth_headers
        ).json()

        target_ev = f"by_ev_{uuid.uuid4().hex[:8]}"
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": target_ev, "party_id": party["id"], "link_type": "proves"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/evidence-links/by-evidence/{target_ev}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(link["evidence_id"] == target_ev for link in data["links"])

    def test_get_links_by_party_returns_filtered(
        self, client, test_user, auth_headers, test_case
    ):
        """
        Given: Links for specific party
        When: GET /cases/{case_id}/evidence-links/by-party/{party_id}
        Then: 200 OK with filtered links
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "defendant", "name": "피고"},
            headers=auth_headers
        ).json()

        ev = f"by_party_ev_{uuid.uuid4().hex[:8]}"
        client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={"evidence_id": ev, "party_id": party["id"], "link_type": "mentions"},
            headers=auth_headers
        )

        response = client.get(
            f"/cases/{test_case.id}/evidence-links/by-party/{party['id']}",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(link["party_id"] == party["id"] for link in data["links"])
