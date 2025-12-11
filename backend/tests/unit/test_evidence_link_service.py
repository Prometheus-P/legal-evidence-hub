"""
Unit tests for Evidence Link Service
007-lawyer-portal-v1: US4 (Evidence-Party Linking)
TDD - Tests for evidence_link_service.py
"""

import pytest
import uuid

from app.services.evidence_link_service import EvidenceLinkService
from app.db.models import (
    PartyNode, PartyRelationship, EvidencePartyLink,
    PartyType, RelationshipType, LinkType,
    Case, User
)
from app.db.schemas import EvidenceLinkCreate
from app.middleware import NotFoundError, ValidationError
from app.core.security import hash_password


class TestEvidenceLinkServiceCreate:
    """Unit tests for evidence link creation"""

    def test_create_link_to_party_success(self, test_env):
        """
        Given: Existing party and evidence
        When: create_link is called with party_id
        Then: Link is created
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Setup
        user = User(
            email=f"link_party_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Link Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Link Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_link_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()
        db.refresh(party)

        # When
        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_{unique_id}",
            party_id=party.id,
            link_type=LinkType.PROVES
        )
        result = service.create_link(case.id, link_data, user.id)

        # Then
        assert result.evidence_id == f"ev_{unique_id}"
        assert result.party_id == party.id
        assert result.link_type == LinkType.PROVES
        assert result.case_id == case.id
        assert result.relationship_id is None

        # Cleanup
        db.query(EvidencePartyLink).filter(EvidencePartyLink.id == result.id).delete()
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_link_to_relationship_success(self, test_env):
        """
        Given: Existing relationship and evidence
        When: create_link is called with relationship_id
        Then: Link is created
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"link_rel_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Link Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Link Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_linkrel1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="당사자1",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_linkrel2_{unique_id}",
            case_id=case.id,
            type=PartyType.THIRD_PARTY,
            name="당사자2",
            position_x=0, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        rel = PartyRelationship(
            id=f"rel_link_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.AFFAIR
        )
        db.add(rel)
        db.commit()
        db.refresh(rel)

        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_rel_{unique_id}",
            relationship_id=rel.id,
            link_type=LinkType.PROVES
        )
        result = service.create_link(case.id, link_data, user.id)

        assert result.relationship_id == rel.id
        assert result.party_id is None
        assert result.link_type == LinkType.PROVES

        # Cleanup
        db.query(EvidencePartyLink).filter(EvidencePartyLink.id == result.id).delete()
        db.delete(rel)
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_link_no_target_raises_error(self, test_env):
        """
        Given: Neither party_id nor relationship_id provided
        When: create_link is called
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"link_no_target_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="No Target User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="No Target Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_no_target_{unique_id}",
            link_type=LinkType.MENTIONS
            # No party_id or relationship_id
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_link(case.id, link_data, user.id)

        assert "party_id 또는 relationship_id" in str(exc_info.value)

        # Cleanup
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_link_party_not_found_raises_error(self, test_env):
        """
        Given: Non-existent party_id
        When: create_link is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"link_party_nf_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Party NF User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Party NF Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_party_nf_{unique_id}",
            party_id="non_existent_party",
            link_type=LinkType.MENTIONS
        )

        with pytest.raises(NotFoundError) as exc_info:
            service.create_link(case.id, link_data, user.id)

        assert "당사자를 찾을 수 없습니다" in str(exc_info.value)

        # Cleanup
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_link_party_wrong_case_raises_error(self, test_env):
        """
        Given: Party from different case
        When: create_link is called
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"link_wrong_case_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Wrong Case User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case1 = Case(title="Case 1", status="active", created_by=user.id)
        case2 = Case(title="Case 2", status="active", created_by=user.id)
        db.add(case1)
        db.add(case2)
        db.commit()
        db.refresh(case1)
        db.refresh(case2)

        party = PartyNode(
            id=f"party_wrong_{unique_id}",
            case_id=case2.id,  # Different case!
            type=PartyType.PLAINTIFF,
            name="다른케이스",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_wrong_{unique_id}",
            party_id=party.id,
            link_type=LinkType.MENTIONS
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_link(case1.id, link_data, user.id)

        assert "케이스에 속하지 않습니다" in str(exc_info.value)

        # Cleanup
        db.delete(party)
        db.query(Case).filter(Case.id == case1.id).delete()
        db.query(Case).filter(Case.id == case2.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_link_duplicate_raises_error(self, test_env):
        """
        Given: Existing link with same evidence and party
        When: create_link is called with same link_type
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"link_dup_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Dup Link User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Dup Link Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_dup_link_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        # Create existing link
        existing = EvidencePartyLink(
            id=f"link_existing_{unique_id}",
            case_id=case.id,
            evidence_id=f"ev_dup_{unique_id}",
            party_id=party.id,
            link_type=LinkType.MENTIONS
        )
        db.add(existing)
        db.commit()

        service = EvidenceLinkService(db)
        link_data = EvidenceLinkCreate(
            evidence_id=f"ev_dup_{unique_id}",
            party_id=party.id,
            link_type=LinkType.MENTIONS  # Same type
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_link(case.id, link_data, user.id)

        assert "이미 존재합니다" in str(exc_info.value)

        # Cleanup
        db.delete(existing)
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestEvidenceLinkServiceGet:
    """Unit tests for evidence link retrieval"""

    def test_get_link_success(self, test_env):
        """
        Given: Existing link
        When: get_link is called
        Then: Link is returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"get_link_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Get Link User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Get Link Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_get_link_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="피고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        link = EvidencePartyLink(
            id=f"link_get_{unique_id}",
            case_id=case.id,
            evidence_id=f"ev_get_{unique_id}",
            party_id=party.id,
            link_type=LinkType.CONTRADICTS
        )
        db.add(link)
        db.commit()
        db.refresh(link)

        service = EvidenceLinkService(db)
        result = service.get_link(link.id)

        assert result.id == link.id
        assert result.link_type == LinkType.CONTRADICTS

        # Cleanup
        db.delete(link)
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_link_not_found_raises_error(self, test_env):
        """
        Given: Non-existent link_id
        When: get_link is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = EvidenceLinkService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_link("non_existent_link")

        assert "링크를 찾을 수 없습니다" in str(exc_info.value)
        db.close()

    def test_get_links_for_case_returns_all(self, test_env):
        """
        Given: Case with multiple links
        When: get_links_for_case is called
        Then: All links are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"list_link_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="List Link User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="List Link Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_list_link_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        links = []
        for i in range(3):
            link = EvidencePartyLink(
                id=f"link_list_{unique_id}_{i}",
                case_id=case.id,
                evidence_id=f"ev_list_{unique_id}_{i}",
                party_id=party.id,
                link_type=LinkType.MENTIONS
            )
            db.add(link)
            links.append(link)
        db.commit()

        service = EvidenceLinkService(db)
        result = service.get_links_for_case(case.id)

        assert result.total == 3
        assert len(result.links) == 3

        # Cleanup
        for link in links:
            db.delete(link)
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_links_for_evidence_filters_correctly(self, test_env):
        """
        Given: Multiple links for different evidence
        When: get_links_for_evidence is called
        Then: Only links for that evidence are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"filter_ev_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Filter Ev User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Filter Ev Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_filter_ev_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        # Link to target evidence
        target_link = EvidencePartyLink(
            id=f"link_target_{unique_id}",
            case_id=case.id,
            evidence_id=f"target_ev_{unique_id}",
            party_id=party.id,
            link_type=LinkType.PROVES
        )
        # Link to other evidence
        other_link = EvidencePartyLink(
            id=f"link_other_{unique_id}",
            case_id=case.id,
            evidence_id=f"other_ev_{unique_id}",
            party_id=party.id,
            link_type=LinkType.MENTIONS
        )
        db.add(target_link)
        db.add(other_link)
        db.commit()

        service = EvidenceLinkService(db)
        result = service.get_links_for_evidence(case.id, f"target_ev_{unique_id}")

        assert result.total == 1
        assert result.links[0].evidence_id == f"target_ev_{unique_id}"

        # Cleanup
        db.delete(target_link)
        db.delete(other_link)
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestEvidenceLinkServiceDelete:
    """Unit tests for evidence link deletion"""

    def test_delete_link_success(self, test_env):
        """
        Given: Existing link
        When: delete_link is called
        Then: Link is deleted
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"del_link_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Del Link User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Del Link Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_del_link_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()

        link = EvidencePartyLink(
            id=f"link_del_{unique_id}",
            case_id=case.id,
            evidence_id=f"ev_del_{unique_id}",
            party_id=party.id,
            link_type=LinkType.INVOLVES
        )
        db.add(link)
        db.commit()
        link_id = link.id

        service = EvidenceLinkService(db)
        result = service.delete_link(link_id, user.id)

        assert result is True

        # Verify deletion
        deleted = db.query(EvidencePartyLink).filter(EvidencePartyLink.id == link_id).first()
        assert deleted is None

        # Cleanup
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_delete_link_not_found_raises_error(self, test_env):
        """
        Given: Non-existent link_id
        When: delete_link is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = EvidenceLinkService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.delete_link("non_existent_link", "user_id")

        assert "링크를 찾을 수 없습니다" in str(exc_info.value)
        db.close()
