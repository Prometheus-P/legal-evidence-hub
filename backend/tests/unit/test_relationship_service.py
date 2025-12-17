"""
Unit tests for Relationship Service
007-lawyer-portal-v1: US1 (Party Relationship Graph)
TDD - Tests for relationship_service.py
"""

import pytest
import uuid

from app.services.relationship_service import RelationshipService
from app.db.models import (
    PartyNode, PartyRelationship, PartyType, RelationshipType,
    Case, User
)
from app.db.schemas import RelationshipCreate, RelationshipUpdate
from app.middleware import NotFoundError, ValidationError
from app.core.security import hash_password


class TestRelationshipServiceCreate:
    """Unit tests for relationship creation"""

    def test_create_relationship_success(self, test_env):
        """
        Given: Two existing parties in a case
        When: create_relationship is called
        Then: Relationship is created between them
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Setup
        user = User(
            email=f"rel_create_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Rel Create User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Relationship Test Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_rel1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="김철수",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_rel2_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="박영희",
            position_x=200, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()
        db.refresh(party1)
        db.refresh(party2)

        # When
        service = RelationshipService(db)
        rel_data = RelationshipCreate(
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.MARRIAGE,
            notes="2010년 결혼"
        )
        result = service.create_relationship(case.id, rel_data, user.id)

        # Then
        assert result.source_party_id == party1.id
        assert result.target_party_id == party2.id
        assert result.type == RelationshipType.MARRIAGE
        assert result.notes == "2010년 결혼"
        assert result.case_id == case.id

        # Cleanup
        db.query(PartyRelationship).filter(PartyRelationship.id == result.id).delete()
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_relationship_self_reference_raises_error(self, test_env):
        """
        Given: Same party as source and target
        When: create_relationship is called
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_self_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Self Ref User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Self Ref Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_self_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="자기참조",
            position_x=0, position_y=0
        )
        db.add(party)
        db.commit()
        db.refresh(party)

        service = RelationshipService(db)
        rel_data = RelationshipCreate(
            source_party_id=party.id,
            target_party_id=party.id,  # Same as source
            type=RelationshipType.MARRIAGE
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_relationship(case.id, rel_data, user.id)

        assert "동일할 수 없습니다" in str(exc_info.value)

        # Cleanup
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_relationship_duplicate_raises_error(self, test_env):
        """
        Given: Existing relationship between two parties
        When: create_relationship is called with same type
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_dup_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Dup Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Dup Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_dup1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="당사자1",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_dup2_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="당사자2",
            position_x=200, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        # Create existing relationship
        existing_rel = PartyRelationship(
            id=f"rel_existing_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.MARRIAGE
        )
        db.add(existing_rel)
        db.commit()

        service = RelationshipService(db)
        rel_data = RelationshipCreate(
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.MARRIAGE  # Same type
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_relationship(case.id, rel_data, user.id)

        assert "이미 존재합니다" in str(exc_info.value)

        # Cleanup
        db.delete(existing_rel)
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_relationship_party_not_in_case_raises_error(self, test_env):
        """
        Given: Party from different case
        When: create_relationship is called
        Then: ValidationError is raised
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_diff_case_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Diff Case User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case1 = Case(
            title="Case 1",
            status="active",
            created_by=user.id
        )
        case2 = Case(
            title="Case 2",
            status="active",
            created_by=user.id
        )
        db.add(case1)
        db.add(case2)
        db.commit()
        db.refresh(case1)
        db.refresh(case2)

        party1 = PartyNode(
            id=f"party_case1_{unique_id}",
            case_id=case1.id,
            type=PartyType.PLAINTIFF,
            name="Case1 Party",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_case2_{unique_id}",
            case_id=case2.id,  # Different case!
            type=PartyType.DEFENDANT,
            name="Case2 Party",
            position_x=0, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        service = RelationshipService(db)
        rel_data = RelationshipCreate(
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.MARRIAGE
        )

        with pytest.raises(ValidationError) as exc_info:
            service.create_relationship(case1.id, rel_data, user.id)

        assert "케이스에 속하지 않습니다" in str(exc_info.value)

        # Cleanup
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case1.id).delete()
        db.query(Case).filter(Case.id == case2.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestRelationshipServiceGet:
    """Unit tests for relationship retrieval"""

    def test_get_relationship_success(self, test_env):
        """
        Given: Existing relationship
        When: get_relationship is called
        Then: Relationship is returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_get_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Get Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Get Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_get1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="당사자1",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_get2_{unique_id}",
            case_id=case.id,
            type=PartyType.THIRD_PARTY,
            name="당사자2",
            position_x=0, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        rel = PartyRelationship(
            id=f"rel_get_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.AFFAIR,
            notes="불륜관계"
        )
        db.add(rel)
        db.commit()
        db.refresh(rel)

        service = RelationshipService(db)
        result = service.get_relationship(rel.id)

        assert result.id == rel.id
        assert result.type == RelationshipType.AFFAIR
        assert result.notes == "불륜관계"

        # Cleanup
        db.delete(rel)
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_relationship_not_found_raises_error(self, test_env):
        """
        Given: Non-existent relationship_id
        When: get_relationship is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = RelationshipService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_relationship("non_existent_rel_id")

        assert "관계를 찾을 수 없습니다" in str(exc_info.value)
        db.close()

    def test_get_relationships_for_case_returns_all(self, test_env):
        """
        Given: Case with multiple relationships
        When: get_relationships_for_case is called
        Then: All relationships are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_list_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="List Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="List Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        parties = []
        for i in range(3):
            party = PartyNode(
                id=f"party_list_{unique_id}_{i}",
                case_id=case.id,
                type=PartyType.FAMILY,
                name=f"가족{i+1}",
                position_x=i*100, position_y=0
            )
            db.add(party)
            parties.append(party)
        db.commit()

        rel1 = PartyRelationship(
            id=f"rel_list1_{unique_id}",
            case_id=case.id,
            source_party_id=parties[0].id,
            target_party_id=parties[1].id,
            type=RelationshipType.PARENT_CHILD
        )
        rel2 = PartyRelationship(
            id=f"rel_list2_{unique_id}",
            case_id=case.id,
            source_party_id=parties[1].id,
            target_party_id=parties[2].id,
            type=RelationshipType.SIBLING
        )
        db.add(rel1)
        db.add(rel2)
        db.commit()

        service = RelationshipService(db)
        result = service.get_relationships_for_case(case.id)

        assert len(result) == 2

        # Cleanup
        db.delete(rel1)
        db.delete(rel2)
        for p in parties:
            db.delete(p)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestRelationshipServiceUpdate:
    """Unit tests for relationship update"""

    def test_update_relationship_success(self, test_env):
        """
        Given: Existing relationship
        When: update_relationship is called
        Then: Relationship is updated
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_update_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Update Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Update Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_upd1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="당사자1",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_upd2_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="당사자2",
            position_x=0, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        rel = PartyRelationship(
            id=f"rel_upd_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.COHABIT,
            notes="원래메모"
        )
        db.add(rel)
        db.commit()
        db.refresh(rel)

        service = RelationshipService(db)
        update_data = RelationshipUpdate(
            type=RelationshipType.MARRIAGE,
            notes="수정된메모"
        )
        result = service.update_relationship(rel.id, update_data, user.id)

        assert result.type == RelationshipType.MARRIAGE
        assert result.notes == "수정된메모"

        # Cleanup
        db.delete(rel)
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestRelationshipServiceDelete:
    """Unit tests for relationship deletion"""

    def test_delete_relationship_success(self, test_env):
        """
        Given: Existing relationship
        When: delete_relationship is called
        Then: Relationship is deleted
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"rel_del_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Del Rel User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Del Rel Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_del1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="당사자1",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_del2_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="당사자2",
            position_x=0, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        rel = PartyRelationship(
            id=f"rel_del_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.IN_LAW
        )
        db.add(rel)
        db.commit()
        rel_id = rel.id

        service = RelationshipService(db)
        result = service.delete_relationship(rel_id, user.id)

        assert result is True

        # Verify deletion
        deleted = db.query(PartyRelationship).filter(PartyRelationship.id == rel_id).first()
        assert deleted is None

        # Cleanup
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestRelationshipServicePartyGraph:
    """Unit tests for party graph retrieval"""

    def test_get_party_graph_returns_nodes_and_relationships(self, test_env):
        """
        Given: Case with parties and relationships
        When: get_party_graph is called
        Then: Both nodes and relationships are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"graph_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Graph User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Graph Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_graph1_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0, position_y=0
        )
        party2 = PartyNode(
            id=f"party_graph2_{unique_id}",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="피고",
            position_x=200, position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        rel = PartyRelationship(
            id=f"rel_graph_{unique_id}",
            case_id=case.id,
            source_party_id=party1.id,
            target_party_id=party2.id,
            type=RelationshipType.MARRIAGE
        )
        db.add(rel)
        db.commit()

        service = RelationshipService(db)
        result = service.get_party_graph(case.id)

        assert len(result.nodes) == 2
        assert len(result.relationships) == 1
        
        node_names = [n.name for n in result.nodes]
        assert "원고" in node_names
        assert "피고" in node_names
        
        assert result.relationships[0].type == RelationshipType.MARRIAGE

        # Cleanup
        db.delete(rel)
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_party_graph_case_not_found_raises_error(self, test_env):
        """
        Given: Non-existent case_id
        When: get_party_graph is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = RelationshipService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_party_graph("non_existent_case")

        assert "케이스를 찾을 수 없습니다" in str(exc_info.value)
        db.close()
