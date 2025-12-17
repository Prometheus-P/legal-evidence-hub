"""
Unit tests for Party Service
007-lawyer-portal-v1: US1 (Party Relationship Graph)
TDD - Tests for party_service.py
"""

import pytest
import uuid

from app.services.party_service import PartyService
from app.db.models import PartyNode, PartyType, Case, User
from app.db.schemas import PartyNodeCreate, PartyNodeUpdate, Position
from app.middleware import NotFoundError
from app.core.security import hash_password


class TestPartyServiceCreate:
    """Unit tests for party creation"""

    def test_create_party_success(self, test_env):
        """
        Given: Valid party data and existing case
        When: create_party is called
        Then: Party is created with correct attributes
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Setup: Create user and case
        user = User(
            email=f"party_create_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Party Create User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Party Test Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # When
        service = PartyService(db)
        party_data = PartyNodeCreate(
            type=PartyType.PLAINTIFF,
            name="김철수",
            alias="김○○",
            birth_year=1980,
            occupation="회사원",
            position=Position(x=100, y=200)
        )
        result = service.create_party(case.id, party_data, user.id)

        # Then
        assert result.name == "김철수"
        assert result.type == PartyType.PLAINTIFF
        assert result.alias == "김○○"
        assert result.birth_year == 1980
        assert result.occupation == "회사원"
        assert result.position.x == 100
        assert result.position.y == 200
        assert result.case_id == case.id

        # Cleanup
        db.query(PartyNode).filter(PartyNode.id == result.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_create_party_case_not_found_raises_error(self, test_env):
        """
        Given: Non-existent case_id
        When: create_party is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = PartyService(db)
        party_data = PartyNodeCreate(
            type=PartyType.PLAINTIFF,
            name="테스트"
        )

        with pytest.raises(NotFoundError) as exc_info:
            service.create_party("non_existent_case_id", party_data, "user_id")

        assert "케이스를 찾을 수 없습니다" in str(exc_info.value)
        db.close()

    def test_create_party_with_default_position(self, test_env):
        """
        Given: Party data without position
        When: create_party is called
        Then: Party is created with default position (0, 0)
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_default_pos_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Default Position User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Default Position Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        service = PartyService(db)
        party_data = PartyNodeCreate(
            type=PartyType.DEFENDANT,
            name="박영희"
        )
        result = service.create_party(case.id, party_data, user.id)

        # Default position should be (0, 0)
        assert result.position.x == 0
        assert result.position.y == 0

        # Cleanup
        db.query(PartyNode).filter(PartyNode.id == result.id).delete()
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestPartyServiceGet:
    """Unit tests for party retrieval"""

    def test_get_party_success(self, test_env):
        """
        Given: Existing party
        When: get_party is called with valid id
        Then: Party is returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_get_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Get Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Get Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="조회테스트",
            position_x=50,
            position_y=75
        )
        db.add(party)
        db.commit()
        db.refresh(party)

        service = PartyService(db)
        result = service.get_party(party.id)

        assert result.id == party.id
        assert result.name == "조회테스트"
        assert result.position.x == 50
        assert result.position.y == 75

        # Cleanup
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_party_not_found_raises_error(self, test_env):
        """
        Given: Non-existent party_id
        When: get_party is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = PartyService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.get_party("non_existent_party_id")

        assert "당사자를 찾을 수 없습니다" in str(exc_info.value)
        db.close()

    def test_get_parties_for_case_returns_all_parties(self, test_env):
        """
        Given: Case with multiple parties
        When: get_parties_for_case is called
        Then: All parties for the case are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_list_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="List Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="List Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        # Create 3 parties
        parties = []
        for i, ptype in enumerate([PartyType.PLAINTIFF, PartyType.DEFENDANT, PartyType.CHILD]):
            party = PartyNode(
                id=f"party_{unique_id}_{i}",
                case_id=case.id,
                type=ptype,
                name=f"당사자{i+1}",
                position_x=i * 100,
                position_y=i * 50
            )
            db.add(party)
            parties.append(party)
        db.commit()

        service = PartyService(db)
        result = service.get_parties_for_case(case.id)

        assert len(result) == 3
        names = [p.name for p in result]
        assert "당사자1" in names
        assert "당사자2" in names
        assert "당사자3" in names

        # Cleanup
        for party in parties:
            db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_get_parties_for_case_filtered_by_type(self, test_env):
        """
        Given: Case with parties of different types
        When: get_parties_for_case is called with type filter
        Then: Only parties of that type are returned
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_filter_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Filter Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Filter Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party1 = PartyNode(
            id=f"party_filter_{unique_id}_1",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원고",
            position_x=0,
            position_y=0
        )
        party2 = PartyNode(
            id=f"party_filter_{unique_id}_2",
            case_id=case.id,
            type=PartyType.DEFENDANT,
            name="피고",
            position_x=0,
            position_y=0
        )
        db.add(party1)
        db.add(party2)
        db.commit()

        service = PartyService(db)
        result = service.get_parties_for_case(case.id, PartyType.PLAINTIFF)

        assert len(result) == 1
        assert result[0].name == "원고"
        assert result[0].type == PartyType.PLAINTIFF

        # Cleanup
        db.delete(party1)
        db.delete(party2)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()


class TestPartyServiceUpdate:
    """Unit tests for party update"""

    def test_update_party_success(self, test_env):
        """
        Given: Existing party
        When: update_party is called with valid data
        Then: Party is updated
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_update_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Update Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Update Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_update_{unique_id}",
            case_id=case.id,
            type=PartyType.PLAINTIFF,
            name="원래이름",
            alias="원○○",
            position_x=0,
            position_y=0
        )
        db.add(party)
        db.commit()
        db.refresh(party)

        service = PartyService(db)
        update_data = PartyNodeUpdate(
            name="수정이름",
            alias="수○○",
            position=Position(x=300, y=400)
        )
        result = service.update_party(party.id, update_data, user.id)

        assert result.name == "수정이름"
        assert result.alias == "수○○"
        assert result.position.x == 300
        assert result.position.y == 400

        # Cleanup
        db.delete(party)
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_update_party_not_found_raises_error(self, test_env):
        """
        Given: Non-existent party_id
        When: update_party is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = PartyService(db)
        update_data = PartyNodeUpdate(name="새이름")

        with pytest.raises(NotFoundError) as exc_info:
            service.update_party("non_existent_id", update_data, "user_id")

        assert "당사자를 찾을 수 없습니다" in str(exc_info.value)
        db.close()


class TestPartyServiceDelete:
    """Unit tests for party deletion"""

    def test_delete_party_success(self, test_env):
        """
        Given: Existing party
        When: delete_party is called
        Then: Party is deleted
        """
        from app.db.session import get_db

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        user = User(
            email=f"party_delete_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Delete Party User",
            role="lawyer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        case = Case(
            title="Delete Party Case",
            status="active",
            created_by=user.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        party = PartyNode(
            id=f"party_delete_{unique_id}",
            case_id=case.id,
            type=PartyType.THIRD_PARTY,
            name="삭제대상",
            position_x=0,
            position_y=0
        )
        db.add(party)
        db.commit()
        party_id = party.id

        service = PartyService(db)
        result = service.delete_party(party_id, user.id)

        assert result is True

        # Verify deletion
        deleted = db.query(PartyNode).filter(PartyNode.id == party_id).first()
        assert deleted is None

        # Cleanup
        db.query(Case).filter(Case.id == case.id).delete()
        db.delete(user)
        db.commit()
        db.close()

    def test_delete_party_not_found_raises_error(self, test_env):
        """
        Given: Non-existent party_id
        When: delete_party is called
        Then: NotFoundError is raised
        """
        from app.db.session import get_db

        db = next(get_db())

        service = PartyService(db)

        with pytest.raises(NotFoundError) as exc_info:
            service.delete_party("non_existent_id", "user_id")

        assert "당사자를 찾을 수 없습니다" in str(exc_info.value)
        db.close()
