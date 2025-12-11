"""
Contract tests for Detective Cases API
Task T078 - US5 Tests

Tests for detective case endpoints:
- GET /detective/cases
- GET /detective/cases/{id}
"""

import pytest
from fastapi import status


# ============== T078: GET /detective/cases Contract Tests ==============


class TestGetDetectiveCases:
    """
    Contract tests for GET /detective/cases
    """

    def test_should_return_case_list_for_detective(
        self, client, detective_user, detective_auth_headers
    ):
        """
        Given: Authenticated detective user
        When: GET /detective/cases
        Then:
            - Returns 200 status code
            - Response contains items array
            - Response contains total count
        """
        # When: GET /detective/cases
        response = client.get("/detective/cases", headers=detective_auth_headers)

        # Then: Success with case list
        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        # Verify items array
        assert "items" in data
        assert isinstance(data["items"], list)

        # Verify total count
        assert "total" in data
        assert isinstance(data["total"], int)
        assert data["total"] >= 0

    def test_should_filter_by_status(
        self, client, detective_user, detective_auth_headers
    ):
        """
        Given: Authenticated detective
        When: GET /detective/cases?status=active
        Then: Returns filtered results
        """
        response = client.get(
            "/detective/cases?status=active", headers=detective_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "items" in data

        # If items exist, they should have status=active
        for item in data["items"]:
            assert item["status"] == "active"

    def test_should_reject_unauthenticated_request(self, client):
        """
        Given: No authentication token
        When: GET /detective/cases
        Then: Returns 401 Unauthorized
        """
        response = client.get("/detective/cases")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_should_reject_client_role(self, client, client_user, client_auth_headers):
        """
        Given: User with CLIENT role
        When: GET /detective/cases
        Then: Returns 403 Forbidden
        """
        response = client.get("/detective/cases", headers=client_auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_reject_lawyer_role(self, client, auth_headers):
        """
        Given: User with LAWYER role
        When: GET /detective/cases
        Then: Returns 403 Forbidden
        """
        response = client.get("/detective/cases", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetDetectiveCaseDetail:
    """
    Contract tests for GET /detective/cases/{id}
    """

    def test_should_reject_unauthenticated_request(self, client):
        """
        Given: No authentication token
        When: GET /detective/cases/{id}
        Then: Returns 401 Unauthorized
        """
        response = client.get("/detective/cases/some-case-id")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_should_reject_client_role(self, client, client_user, client_auth_headers):
        """
        Given: User with CLIENT role
        When: GET /detective/cases/{id}
        Then: Returns 403 Forbidden
        """
        response = client.get(
            "/detective/cases/some-case-id", headers=client_auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_404_for_nonexistent_case(
        self, client, detective_user, detective_auth_headers
    ):
        """
        Given: Authenticated detective
        When: GET /detective/cases/{nonexistent_id}
        Then: Returns 404 Not Found
        """
        response = client.get(
            "/detective/cases/nonexistent-case-id", headers=detective_auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDetectiveCaseListItems:
    """
    Contract tests for case list item structure
    """

    def test_case_items_should_have_required_fields(
        self, client, detective_user, detective_auth_headers
    ):
        """
        Given: Authenticated detective
        When: GET /detective/cases
        Then: Each case item has id, title, status, lawyer_name
        """
        response = client.get("/detective/cases", headers=detective_auth_headers)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        for item in data["items"]:
            assert "id" in item
            assert "title" in item
            assert "status" in item
            assert item["status"] in ["pending", "active", "review", "completed"]


class TestDetectiveNonAssignedCaseAccess:
    """
    Contract tests for SC-016: 탐정은 미관련 케이스 접근 시 100% 403 반환
    Task #261 - Verify 403 for detective non-assigned cases
    """

    def test_detective_a_cannot_access_detective_b_case_detail(self, client, test_env):
        """
        Given: Detective A is assigned to Case A, Detective B is assigned to Case B
        When: Detective A tries to access Case B (GET /detective/cases/{case_b_id})
        Then: Returns 403 Forbidden
        """
        from app.db.session import get_db
        from app.db.models import User, Case, CaseMember, CaseMemberRole, UserRole
        from app.core.security import hash_password, create_access_token
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create lawyer (case owner)
        lawyer = User(
            email=f"lawyer_261_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Test Lawyer 261",
            role=UserRole.LAWYER
        )
        db.add(lawyer)
        db.commit()
        db.refresh(lawyer)

        # Create Detective A
        detective_a = User(
            email=f"detective_a_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Detective A",
            role=UserRole.DETECTIVE
        )
        db.add(detective_a)
        db.commit()
        db.refresh(detective_a)

        # Create Detective B
        detective_b = User(
            email=f"detective_b_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Detective B",
            role=UserRole.DETECTIVE
        )
        db.add(detective_b)
        db.commit()
        db.refresh(detective_b)

        # Create Case A (assigned to Detective A)
        case_a = Case(
            title="Case A - Detective A's Case",
            description="Case for Detective A",
            status="active",
            created_by=lawyer.id
        )
        db.add(case_a)
        db.commit()
        db.refresh(case_a)

        # Create Case B (assigned to Detective B)
        case_b = Case(
            title="Case B - Detective B's Case",
            description="Case for Detective B",
            status="active",
            created_by=lawyer.id
        )
        db.add(case_b)
        db.commit()
        db.refresh(case_b)

        # Assign lawyer as owner for both cases
        lawyer_membership_a = CaseMember(
            case_id=case_a.id,
            user_id=lawyer.id,
            role=CaseMemberRole.OWNER
        )
        lawyer_membership_b = CaseMember(
            case_id=case_b.id,
            user_id=lawyer.id,
            role=CaseMemberRole.OWNER
        )
        db.add(lawyer_membership_a)
        db.add(lawyer_membership_b)

        # Assign Detective A to Case A
        membership_a = CaseMember(
            case_id=case_a.id,
            user_id=detective_a.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(membership_a)

        # Assign Detective B to Case B
        membership_b = CaseMember(
            case_id=case_b.id,
            user_id=detective_b.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(membership_b)
        db.commit()

        # Create token for Detective A
        token_a = create_access_token({
            "sub": detective_a.id,
            "role": detective_a.role.value,
            "email": detective_a.email
        })

        # When: Detective A tries to access Case B (not assigned)
        response = client.get(
            f"/detective/cases/{case_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Then: Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Cleanup
        db.delete(membership_a)
        db.delete(membership_b)
        db.delete(lawyer_membership_a)
        db.delete(lawyer_membership_b)
        db.delete(case_a)
        db.delete(case_b)
        db.delete(detective_a)
        db.delete(detective_b)
        db.delete(lawyer)
        db.commit()
        db.close()

    def test_detective_a_cannot_create_record_for_detective_b_case(self, client, test_env):
        """
        Given: Detective A is assigned to Case A, Detective B is assigned to Case B
        When: Detective A tries to create record in Case B (POST /detective/cases/{case_b_id}/records)
        Then: Returns 403 Forbidden or 404 Not Found
        """
        from app.db.session import get_db
        from app.db.models import User, Case, CaseMember, CaseMemberRole, UserRole
        from app.core.security import hash_password, create_access_token
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create lawyer
        lawyer = User(
            email=f"lawyer_261b_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Test Lawyer 261b",
            role=UserRole.LAWYER
        )
        db.add(lawyer)
        db.commit()
        db.refresh(lawyer)

        # Create Detective A
        detective_a = User(
            email=f"detective_a_rec_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Detective A Record",
            role=UserRole.DETECTIVE
        )
        db.add(detective_a)
        db.commit()
        db.refresh(detective_a)

        # Create Detective B
        detective_b = User(
            email=f"detective_b_rec_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Detective B Record",
            role=UserRole.DETECTIVE
        )
        db.add(detective_b)
        db.commit()
        db.refresh(detective_b)

        # Create Case A and Case B
        case_a = Case(
            title="Case A - Record Test",
            description="Case A",
            status="active",
            created_by=lawyer.id
        )
        case_b = Case(
            title="Case B - Record Test",
            description="Case B",
            status="active",
            created_by=lawyer.id
        )
        db.add(case_a)
        db.add(case_b)
        db.commit()
        db.refresh(case_a)
        db.refresh(case_b)

        # Assign memberships
        lawyer_membership_a = CaseMember(
            case_id=case_a.id,
            user_id=lawyer.id,
            role=CaseMemberRole.OWNER
        )
        lawyer_membership_b = CaseMember(
            case_id=case_b.id,
            user_id=lawyer.id,
            role=CaseMemberRole.OWNER
        )
        membership_a = CaseMember(
            case_id=case_a.id,
            user_id=detective_a.id,
            role=CaseMemberRole.MEMBER
        )
        membership_b = CaseMember(
            case_id=case_b.id,
            user_id=detective_b.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(lawyer_membership_a)
        db.add(lawyer_membership_b)
        db.add(membership_a)
        db.add(membership_b)
        db.commit()

        # Create token for Detective A
        token_a = create_access_token({
            "sub": detective_a.id,
            "role": detective_a.role.value,
            "email": detective_a.email
        })

        # When: Detective A tries to create record in Case B
        response = client.post(
            f"/detective/cases/{case_b.id}/records",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "record_type": "observation",
                "content": "Test observation"
            }
        )

        # Then: Should return 403 Forbidden or 404 Not Found (case not assigned)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

        # Cleanup
        db.delete(membership_a)
        db.delete(membership_b)
        db.delete(lawyer_membership_a)
        db.delete(lawyer_membership_b)
        db.delete(case_a)
        db.delete(case_b)
        db.delete(detective_a)
        db.delete(detective_b)
        db.delete(lawyer)
        db.commit()
        db.close()

    def test_detective_a_can_access_own_case(self, client, test_env):
        """
        Given: Detective A is assigned to Case A
        When: Detective A accesses Case A (GET /detective/cases/{case_a_id})
        Then: Returns 200 OK
        """
        from app.db.session import get_db
        from app.db.models import User, Case, CaseMember, CaseMemberRole, UserRole
        from app.core.security import hash_password, create_access_token
        import uuid

        db = next(get_db())
        unique_id = uuid.uuid4().hex[:8]

        # Create lawyer
        lawyer = User(
            email=f"lawyer_261c_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Test Lawyer 261c",
            role=UserRole.LAWYER
        )
        db.add(lawyer)
        db.commit()
        db.refresh(lawyer)

        # Create Detective A
        detective_a = User(
            email=f"detective_a_own_{unique_id}@test.com",
            hashed_password=hash_password("password123"),
            name="Detective A Own",
            role=UserRole.DETECTIVE
        )
        db.add(detective_a)
        db.commit()
        db.refresh(detective_a)

        # Create Case A
        case_a = Case(
            title="Case A - Own Case Test",
            description="Detective A's own case",
            status="active",
            created_by=lawyer.id
        )
        db.add(case_a)
        db.commit()
        db.refresh(case_a)

        # Assign memberships
        lawyer_membership = CaseMember(
            case_id=case_a.id,
            user_id=lawyer.id,
            role=CaseMemberRole.OWNER
        )
        membership_a = CaseMember(
            case_id=case_a.id,
            user_id=detective_a.id,
            role=CaseMemberRole.MEMBER
        )
        db.add(lawyer_membership)
        db.add(membership_a)
        db.commit()

        # Create token for Detective A
        token_a = create_access_token({
            "sub": detective_a.id,
            "role": detective_a.role.value,
            "email": detective_a.email
        })

        # When: Detective A accesses their own Case A
        response = client.get(
            f"/detective/cases/{case_a.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Then: Should return 200 OK
        assert response.status_code == status.HTTP_200_OK

        # Verify response contains case details
        data = response.json()
        assert data["id"] == str(case_a.id)
        assert data["title"] == "Case A - Own Case Test"

        # Cleanup
        db.delete(membership_a)
        db.delete(lawyer_membership)
        db.delete(case_a)
        db.delete(detective_a)
        db.delete(lawyer)
        db.commit()
        db.close()
