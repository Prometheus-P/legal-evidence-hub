"""
Contract tests for Assets API
TDD for US2 - 재산분할표 (Asset Division Sheet)

Tests API endpoints for asset CRUD and division calculation.
"""

import pytest
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.db.session import get_db
from app.db.models import User, Case, CaseMember, Asset, AssetCategory, AssetOwnership, AssetNature
from app.core.security import hash_password, create_access_token
from tests.conftest import APITestClient


@pytest.fixture
def test_client():
    """Create test client with /api prefix wrapper"""
    return APITestClient(TestClient(app))


@pytest.fixture
def test_user_and_case(test_env):
    """Create test user with a case for asset testing"""
    db = next(get_db())
    unique_id = uuid.uuid4().hex[:8]

    # Create user
    user = User(
        id=f"user_{unique_id}",
        email=f"asset_test_{unique_id}@test.com",
        hashed_password=hash_password("password123"),
        name="Asset Test User",
        role="lawyer"
    )
    db.add(user)
    db.flush()

    # Create case
    case = Case(
        id=f"case_{unique_id}",
        title="Asset Test Case",
        description="Test case for asset API",
        status="active",
        created_by=user.id
    )
    db.add(case)
    db.flush()

    # Add user as case member (owner)
    # CaseMember uses composite key (case_id, user_id)
    member = CaseMember(
        case_id=case.id,
        user_id=user.id,
        role="owner"
    )
    db.add(member)
    db.commit()

    # Generate access token
    token = create_access_token({"sub": user.id})

    yield {
        "user": user,
        "case": case,
        "token": token,
        "db": db
    }

    # Cleanup (optional - test DB is recreated each run)
    db.query(CaseMember).filter(CaseMember.case_id == case.id).delete()
    db.query(Asset).filter(Asset.case_id == case.id).delete()
    db.query(Case).filter(Case.id == case.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


class TestAssetsListEndpoint:
    """Tests for GET /cases/{case_id}/assets"""

    def test_list_assets_empty(self, test_client, test_user_and_case):
        """
        Given: A case with no assets
        When: GET /cases/{case_id}/assets
        Then: Returns empty list with total 0
        """
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]

        response = test_client.get(
            f"/cases/{case_id}/assets",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assets"] == []
        assert data["total"] == 0

    def test_list_assets_with_data(self, test_client, test_user_and_case):
        """
        Given: A case with assets
        When: GET /cases/{case_id}/assets
        Then: Returns list of assets
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create test assets
        asset1 = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            nature=AssetNature.MARITAL,
            name="Apartment",
            current_value=500_000_000,
            created_by=user_id
        )
        asset2 = Asset(
            case_id=case_id,
            category=AssetCategory.SAVINGS,
            ownership=AssetOwnership.DEFENDANT,
            nature=AssetNature.MARITAL,
            name="Bank Account",
            current_value=50_000_000,
            created_by=user_id
        )
        db.add_all([asset1, asset2])
        db.commit()

        response = test_client.get(
            f"/cases/{case_id}/assets",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["assets"]) == 2

    def test_list_assets_filter_by_category(self, test_client, test_user_and_case):
        """
        Given: Assets of different categories
        When: GET /cases/{case_id}/assets?category=real_estate
        Then: Returns only real estate assets
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create assets of different categories
        asset1 = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            name="House",
            current_value=500_000_000,
            created_by=user_id
        )
        asset2 = Asset(
            case_id=case_id,
            category=AssetCategory.VEHICLE,
            ownership=AssetOwnership.PLAINTIFF,
            name="Car",
            current_value=30_000_000,
            created_by=user_id
        )
        db.add_all([asset1, asset2])
        db.commit()

        response = test_client.get(
            f"/cases/{case_id}/assets?category=real_estate",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["assets"][0]["category"] == "real_estate"

    def test_list_assets_unauthorized(self, test_client, test_user_and_case):
        """
        Given: No authentication
        When: GET /cases/{case_id}/assets
        Then: Returns 401
        """
        case_id = test_user_and_case["case"].id

        response = test_client.get(f"/cases/{case_id}/assets")

        assert response.status_code == 401


class TestAssetCreateEndpoint:
    """Tests for POST /cases/{case_id}/assets"""

    def test_create_asset_success(self, test_client, test_user_and_case):
        """
        Given: Valid asset data
        When: POST /cases/{case_id}/assets
        Then: Asset is created and returned
        """
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]

        asset_data = {
            "category": "real_estate",
            "ownership": "plaintiff",
            "nature": "marital",
            "name": "Apartment in Gangnam",
            "current_value": 1_500_000_000,
            "description": "3-bedroom apartment",
            "division_ratio_plaintiff": 50,
            "division_ratio_defendant": 50
        }

        response = test_client.post(
            f"/cases/{case_id}/assets",
            json=asset_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Apartment in Gangnam"
        assert data["current_value"] == 1_500_000_000
        assert data["category"] == "real_estate"
        assert data["ownership"] == "plaintiff"
        assert "id" in data

    def test_create_asset_validation_error(self, test_client, test_user_and_case):
        """
        Given: Invalid asset data (missing required fields)
        When: POST /cases/{case_id}/assets
        Then: Returns 422 validation error
        """
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]

        # Missing required fields
        asset_data = {
            "category": "real_estate"
            # Missing: ownership, name, current_value
        }

        response = test_client.post(
            f"/cases/{case_id}/assets",
            json=asset_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 422


class TestAssetUpdateEndpoint:
    """Tests for PATCH /cases/{case_id}/assets/{asset_id}"""

    def test_update_asset_success(self, test_client, test_user_and_case):
        """
        Given: Existing asset
        When: PATCH /cases/{case_id}/assets/{asset_id}
        Then: Asset is updated
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create asset
        asset = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            name="Old Name",
            current_value=100_000_000,
            created_by=user_id
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        # Update
        update_data = {
            "name": "Updated Name",
            "current_value": 150_000_000
        }

        response = test_client.patch(
            f"/cases/{case_id}/assets/{asset.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["current_value"] == 150_000_000

    def test_update_asset_not_found(self, test_client, test_user_and_case):
        """
        Given: Non-existent asset ID
        When: PATCH /cases/{case_id}/assets/{asset_id}
        Then: Returns 404
        """
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]

        response = test_client.patch(
            f"/cases/{case_id}/assets/nonexistent_id",
            json={"name": "Updated"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestAssetDeleteEndpoint:
    """Tests for DELETE /cases/{case_id}/assets/{asset_id}"""

    def test_delete_asset_success(self, test_client, test_user_and_case):
        """
        Given: Existing asset
        When: DELETE /cases/{case_id}/assets/{asset_id}
        Then: Asset is deleted (204 No Content)
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create asset
        asset = Asset(
            case_id=case_id,
            category=AssetCategory.VEHICLE,
            ownership=AssetOwnership.DEFENDANT,
            name="Car",
            current_value=30_000_000,
            created_by=user_id
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        response = test_client.delete(
            f"/cases/{case_id}/assets/{asset.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # Verify deletion
        deleted = db.query(Asset).filter(Asset.id == asset.id).first()
        assert deleted is None


class TestDivisionCalculateEndpoint:
    """Tests for POST /cases/{case_id}/assets/calculate"""

    def test_calculate_division_success(self, test_client, test_user_and_case):
        """
        Given: Assets in a case
        When: POST /cases/{case_id}/assets/calculate
        Then: Division is calculated and summary returned
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create test assets
        assets = [
            Asset(
                case_id=case_id,
                category=AssetCategory.REAL_ESTATE,
                ownership=AssetOwnership.PLAINTIFF,
                nature=AssetNature.MARITAL,
                name="House",
                current_value=500_000_000,
                created_by=user_id
            ),
            Asset(
                case_id=case_id,
                category=AssetCategory.SAVINGS,
                ownership=AssetOwnership.DEFENDANT,
                nature=AssetNature.MARITAL,
                name="Savings",
                current_value=100_000_000,
                created_by=user_id
            )
        ]
        db.add_all(assets)
        db.commit()

        request_data = {
            "plaintiff_ratio": 50,
            "defendant_ratio": 50,
            "include_separate": False,
            "notes": "Initial calculation"
        }

        response = test_client.post(
            f"/cases/{case_id}/assets/calculate",
            json=request_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify calculation results
        assert data["total_marital_assets"] == 600_000_000
        assert data["net_marital_value"] == 600_000_000
        assert data["plaintiff_share"] == 300_000_000
        assert data["defendant_share"] == 300_000_000
        assert data["plaintiff_holdings"] == 500_000_000
        assert data["defendant_holdings"] == 100_000_000
        # Plaintiff holds 500M but entitled to 300M, pays 200M
        assert data["settlement_amount"] == 200_000_000

    def test_calculate_division_with_different_ratios(self, test_client, test_user_and_case):
        """
        Given: Assets and 60:40 ratio
        When: POST /cases/{case_id}/assets/calculate
        Then: Division calculated with specified ratios
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        asset = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            nature=AssetNature.MARITAL,
            name="Property",
            current_value=100_000_000,
            created_by=user_id
        )
        db.add(asset)
        db.commit()

        request_data = {
            "plaintiff_ratio": 60,
            "defendant_ratio": 40
        }

        response = test_client.post(
            f"/cases/{case_id}/assets/calculate",
            json=request_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["plaintiff_share"] == 60_000_000
        assert data["defendant_share"] == 40_000_000


class TestAssetExportEndpoint:
    """Tests for GET /cases/{case_id}/assets/export"""

    def test_export_assets_csv(self, test_client, test_user_and_case):
        """
        Given: Assets in a case
        When: GET /cases/{case_id}/assets/export
        Then: Returns CSV file
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create test asset
        asset = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            name="Test Property",
            current_value=100_000_000,
            created_by=user_id
        )
        db.add(asset)
        db.commit()

        response = test_client.get(
            f"/cases/{case_id}/assets/export",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert case_id in response.headers["content-disposition"]

        # Verify CSV content
        content = response.content.decode("utf-8-sig")
        assert "Test Property" in content
        assert "100000000" in content


class TestAssetSummaryEndpoint:
    """Tests for GET /cases/{case_id}/assets/summary"""

    def test_get_summary_with_calculation(self, test_client, test_user_and_case):
        """
        Given: Assets and a previous calculation
        When: GET /cases/{case_id}/assets/summary
        Then: Returns summary with latest division calculation
        """
        db = test_user_and_case["db"]
        case_id = test_user_and_case["case"].id
        token = test_user_and_case["token"]
        user_id = test_user_and_case["user"].id

        # Create asset
        asset = Asset(
            case_id=case_id,
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            nature=AssetNature.MARITAL,
            name="Property",
            current_value=100_000_000,
            created_by=user_id
        )
        db.add(asset)
        db.commit()

        # Calculate division first
        test_client.post(
            f"/cases/{case_id}/assets/calculate",
            json={"plaintiff_ratio": 50, "defendant_ratio": 50},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get summary
        response = test_client.get(
            f"/cases/{case_id}/assets/summary",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_assets"] == 1
        assert data["division_summary"] is not None
        assert data["division_summary"]["net_marital_value"] == 100_000_000
