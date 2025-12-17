"""
Integration tests for Party Graph API (US1)
Task T033 - Integration test for party CRUD

End-to-end tests for complete party graph workflows:
- Full CRUD cycle for parties
- Full CRUD cycle for relationships
- Graph retrieval with parties and relationships
"""

from fastapi import status


class TestPartyGraphIntegration:
    """
    Integration tests for complete party graph workflows

    Tests the scenario from spec:
    Create case → Add plaintiff/defendant nodes → Connect with marriage edge
    → Save → Reload page → Verify graph persists
    """

    def test_complete_party_crud_cycle(
        self, client, test_case, auth_headers
    ):
        """
        Test complete CRUD cycle for a party:
        Create → Read → Update → Delete
        """
        # CREATE
        create_response = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "plaintiff",
                "name": "김원고",
                "alias": "원고",
                "birth_year": 1985,
                "occupation": "회사원",
                "position": {"x": 100, "y": 100}
            },
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        party = create_response.json()
        party_id = party["id"]

        # READ
        read_response = client.get(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.json()["name"] == "김원고"

        # UPDATE
        update_response = client.patch(
            f"/cases/{test_case.id}/parties/{party_id}",
            json={"name": "김개명", "occupation": "자영업"},
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["name"] == "김개명"
        assert update_response.json()["occupation"] == "자영업"
        assert update_response.json()["birth_year"] == 1985  # Unchanged

        # DELETE
        delete_response = client.delete(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # VERIFY DELETION
        verify_response = client.get(
            f"/cases/{test_case.id}/parties/{party_id}",
            headers=auth_headers
        )
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_divorce_case_graph(
        self, client, test_case, auth_headers
    ):
        """
        Test creating a typical divorce case graph:
        - Plaintiff (원고)
        - Defendant (피고)
        - Third party (상간자)
        - Child (자녀)
        - Marriage relationship (원고-피고)
        - Affair relationship (피고-상간자)
        - Parent-child relationships
        """
        # Step 1: Create all parties
        plaintiff = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "plaintiff",
                "name": "김원고",
                "birth_year": 1985,
                "position": {"x": 100, "y": 200}
            },
            headers=auth_headers
        ).json()

        defendant = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "defendant",
                "name": "이피고",
                "birth_year": 1987,
                "position": {"x": 400, "y": 200}
            },
            headers=auth_headers
        ).json()

        third_party = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "third_party",
                "name": "박상간",
                "alias": "상간자",
                "position": {"x": 600, "y": 200}
            },
            headers=auth_headers
        ).json()

        child = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "child",
                "name": "김자녀",
                "birth_year": 2015,
                "position": {"x": 250, "y": 400}
            },
            headers=auth_headers
        ).json()

        # Verify 4 parties created
        parties_response = client.get(
            f"/cases/{test_case.id}/parties",
            headers=auth_headers
        )
        assert parties_response.json()["total"] == 4

        # Step 2: Create relationships
        # Marriage (plaintiff-defendant)
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage",
                "start_date": "2010-05-20",
                "notes": "혼인신고일"
            },
            headers=auth_headers
        )

        # Affair (defendant-third_party)
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": defendant["id"],
                "target_party_id": third_party["id"],
                "type": "affair",
                "start_date": "2022-01-15",
                "notes": "불륜관계 시작"
            },
            headers=auth_headers
        )

        # Parent-child (plaintiff-child)
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": child["id"],
                "type": "parent_child"
            },
            headers=auth_headers
        )

        # Parent-child (defendant-child)
        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": defendant["id"],
                "target_party_id": child["id"],
                "type": "parent_child"
            },
            headers=auth_headers
        )

        # Verify 4 relationships created
        relationships_response = client.get(
            f"/cases/{test_case.id}/relationships",
            headers=auth_headers
        )
        assert relationships_response.json()["total"] == 4

        # Step 3: Verify full graph
        graph_response = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        )
        assert graph_response.status_code == status.HTTP_200_OK
        graph = graph_response.json()

        assert len(graph["nodes"]) == 4
        assert len(graph["relationships"]) == 4

        # Verify party types
        party_types = {p["type"] for p in graph["nodes"]}
        assert party_types == {"plaintiff", "defendant", "third_party", "child"}

        # Verify relationship types
        rel_types = {r["type"] for r in graph["relationships"]}
        assert rel_types == {"marriage", "affair", "parent_child"}

    def test_graph_persistence_simulation(
        self, client, test_case, auth_headers
    ):
        """
        Simulate page reload - verify graph data persists:
        1. Create parties and relationships
        2. "Reload" (re-fetch graph)
        3. Verify all data persists
        """
        # Create minimal graph
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

        client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage"
            },
            headers=auth_headers
        )

        # "Reload" - fetch graph fresh
        graph = client.get(
            f"/cases/{test_case.id}/graph",
            headers=auth_headers
        ).json()

        # Verify persistence
        assert len(graph["nodes"]) == 2
        assert len(graph["relationships"]) == 1

        # Verify party details persisted
        party_names = {p["name"] for p in graph["nodes"]}
        assert party_names == {"김원고", "이피고"}

        # Verify relationship details persisted
        rel = graph["relationships"][0]
        assert rel["type"] == "marriage"
        assert rel["source_party_id"] == plaintiff["id"]
        assert rel["target_party_id"] == defendant["id"]

    def test_position_update_auto_save(
        self, client, test_case, auth_headers
    ):
        """
        Test position updates (simulating drag-and-drop in React Flow)
        """
        # Create party at initial position
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={
                "type": "plaintiff",
                "name": "김원고",
                "position": {"x": 100, "y": 100}
            },
            headers=auth_headers
        ).json()

        # Simulate drag-and-drop: update position
        updated = client.patch(
            f"/cases/{test_case.id}/parties/{party['id']}",
            json={"position": {"x": 350, "y": 250}},
            headers=auth_headers
        ).json()

        assert updated["position"]["x"] == 350
        assert updated["position"]["y"] == 250

        # Verify persistence after "reload"
        fetched = client.get(
            f"/cases/{test_case.id}/parties/{party['id']}",
            headers=auth_headers
        ).json()

        assert fetched["position"]["x"] == 350
        assert fetched["position"]["y"] == 250

    def test_cascade_delete_party_with_relationships(
        self, client, test_case, auth_headers
    ):
        """
        Test that deleting a party also deletes related relationships
        (or prevents deletion if relationships exist - depends on design)
        """
        # Create two parties with relationship
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

        rel = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage"
            },
            headers=auth_headers
        ).json()

        # Delete plaintiff
        delete_response = client.delete(
            f"/cases/{test_case.id}/parties/{plaintiff['id']}",
            headers=auth_headers
        )

        # Expected: Either 204 (cascade delete) or 409 (blocked by FK)
        # Based on our implementation with cascade delete:
        assert delete_response.status_code in [
            status.HTTP_204_NO_CONTENT,  # Cascade delete
            status.HTTP_409_CONFLICT  # FK constraint
        ]

        # If cascade deleted, verify relationship is also gone
        if delete_response.status_code == status.HTTP_204_NO_CONTENT:
            rel_response = client.get(
                f"/cases/{test_case.id}/relationships/{rel['id']}",
                headers=auth_headers
            )
            assert rel_response.status_code == status.HTTP_404_NOT_FOUND


class TestEvidenceLinkIntegration:
    """
    Integration tests for evidence-party linking (US4)
    """

    def test_link_evidence_to_party_workflow(
        self, client, test_case, auth_headers
    ):
        """
        Test complete workflow:
        1. Create party
        2. Link evidence to party
        3. Query links by party
        4. Delete link
        """
        # Create party
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        # Mock evidence IDs (stored in DynamoDB)
        evidence_ids = ["ev_msg_001", "ev_photo_002", "ev_audio_003"]

        # Link multiple evidence to party
        created_links = []
        for ev_id in evidence_ids:
            link = client.post(
                f"/cases/{test_case.id}/evidence-links",
                json={
                    "evidence_id": ev_id,
                    "party_id": party["id"],
                    "link_type": "mentions"
                },
                headers=auth_headers
            ).json()
            created_links.append(link)

        assert len(created_links) == 3

        # Query links by party
        party_links = client.get(
            f"/cases/{test_case.id}/evidence-links/by-party/{party['id']}",
            headers=auth_headers
        ).json()

        assert party_links["total"] == 3

        # Delete one link
        client.delete(
            f"/cases/{test_case.id}/evidence-links/{created_links[0]['id']}",
            headers=auth_headers
        )

        # Verify link count decreased
        party_links_after = client.get(
            f"/cases/{test_case.id}/evidence-links/by-party/{party['id']}",
            headers=auth_headers
        ).json()

        assert party_links_after["total"] == 2

    def test_link_evidence_to_relationship(
        self, client, test_case, auth_headers
    ):
        """
        Test linking evidence to a relationship (e.g., marriage certificate)
        """
        # Create parties
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

        # Create marriage relationship
        marriage = client.post(
            f"/cases/{test_case.id}/relationships",
            json={
                "source_party_id": plaintiff["id"],
                "target_party_id": defendant["id"],
                "type": "marriage"
            },
            headers=auth_headers
        ).json()

        # Link marriage certificate to relationship
        link = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": "ev_marriage_cert",
                "relationship_id": marriage["id"],
                "link_type": "proves"
            },
            headers=auth_headers
        ).json()

        assert link["relationship_id"] == marriage["id"]
        assert link["link_type"] == "proves"

        # Verify link appears in case links
        case_links = client.get(
            f"/cases/{test_case.id}/evidence-links",
            headers=auth_headers
        ).json()

        rel_link = next(
            (link for link in case_links["links"] if link["relationship_id"] == marriage["id"]),
            None
        )
        assert rel_link is not None

    def test_multiple_link_types_for_same_evidence(
        self, client, test_case, auth_headers
    ):
        """
        Test that same evidence can have multiple link types to same party
        (e.g., evidence both 'mentions' and 'proves' something about a party)
        """
        party = client.post(
            f"/cases/{test_case.id}/parties",
            json={"type": "plaintiff", "name": "김원고"},
            headers=auth_headers
        ).json()

        evidence_id = "ev_comprehensive_001"

        # Create 'mentions' link
        mentions_link = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "mentions"
            },
            headers=auth_headers
        )
        assert mentions_link.status_code == status.HTTP_201_CREATED

        # Create 'proves' link (same evidence, same party, different type)
        proves_link = client.post(
            f"/cases/{test_case.id}/evidence-links",
            json={
                "evidence_id": evidence_id,
                "party_id": party["id"],
                "link_type": "proves"
            },
            headers=auth_headers
        )
        assert proves_link.status_code == status.HTTP_201_CREATED

        # Query by evidence - should return both links
        evidence_links = client.get(
            f"/cases/{test_case.id}/evidence-links/by-evidence/{evidence_id}",
            headers=auth_headers
        ).json()

        assert evidence_links["total"] == 2
        link_types = {link["link_type"] for link in evidence_links["links"]}
        assert link_types == {"mentions", "proves"}
