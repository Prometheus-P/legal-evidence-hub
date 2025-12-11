"""
Asset Service - Business logic for Asset Division
Implements Service layer per BACKEND_SERVICE_REPOSITORY_GUIDE.md

US2 - 재산분할표 (Asset Division Sheet)
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from app.db.models import Asset, AssetDivisionSummary, AssetCategory, AssetOwnership
from app.db.schemas import AssetCreate, AssetUpdate
from app.repositories.asset_repository import AssetRepository, AssetDivisionSummaryRepository
from app.services.division_calculator import DivisionCalculator
from app.services.case_service import CaseService


class AssetService:
    """
    Service for Asset business logic
    """

    def __init__(self, db: Session):
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.summary_repo = AssetDivisionSummaryRepository(db)
        self.calculator = DivisionCalculator()
        self.case_service = CaseService(db)

    def _verify_case_access(self, case_id: str, user_id: str) -> None:
        """Verify user has access to the case"""
        # This will raise 404 or 403 if no access
        self.case_service.get_case_by_id(case_id, user_id)

    def create_asset(
        self,
        case_id: str,
        asset_data: AssetCreate,
        user_id: str
    ) -> Asset:
        """
        Create a new asset for a case

        Args:
            case_id: Case ID
            asset_data: Asset creation data
            user_id: User ID creating the asset

        Returns:
            Created Asset instance

        Raises:
            HTTPException: If case not found or user has no access
        """
        self._verify_case_access(case_id, user_id)

        asset = self.asset_repo.create(
            case_id=case_id,
            category=asset_data.category,
            ownership=asset_data.ownership,
            name=asset_data.name,
            current_value=asset_data.current_value,
            created_by=user_id,
            nature=asset_data.nature,
            description=asset_data.description,
            acquisition_date=asset_data.acquisition_date,
            acquisition_value=asset_data.acquisition_value,
            valuation_date=asset_data.valuation_date,
            valuation_source=asset_data.valuation_source,
            division_ratio_plaintiff=asset_data.division_ratio_plaintiff,
            division_ratio_defendant=asset_data.division_ratio_defendant,
            proposed_allocation=asset_data.proposed_allocation,
            evidence_id=asset_data.evidence_id,
            notes=asset_data.notes,
        )

        self.db.commit()
        return asset

    def get_asset(
        self,
        case_id: str,
        asset_id: str,
        user_id: str
    ) -> Asset:
        """
        Get a specific asset by ID

        Args:
            case_id: Case ID
            asset_id: Asset ID
            user_id: User ID requesting the asset

        Returns:
            Asset instance

        Raises:
            HTTPException: If asset not found or user has no access
        """
        self._verify_case_access(case_id, user_id)

        asset = self.asset_repo.get_by_id(asset_id)
        if not asset or asset.case_id != case_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )

        return asset

    def list_assets(
        self,
        case_id: str,
        user_id: str,
        category: Optional[AssetCategory] = None
    ) -> List[Asset]:
        """
        List all assets for a case

        Args:
            case_id: Case ID
            user_id: User ID requesting the list
            category: Optional category filter

        Returns:
            List of Asset instances
        """
        self._verify_case_access(case_id, user_id)

        if category:
            return self.asset_repo.get_by_case_and_category(case_id, category)
        return self.asset_repo.get_by_case_id(case_id)

    def update_asset(
        self,
        case_id: str,
        asset_id: str,
        update_data: AssetUpdate,
        user_id: str
    ) -> Asset:
        """
        Update an asset

        Args:
            case_id: Case ID
            asset_id: Asset ID
            update_data: Fields to update
            user_id: User ID making the update

        Returns:
            Updated Asset instance

        Raises:
            HTTPException: If asset not found or user has no access
        """
        asset = self.get_asset(case_id, asset_id, user_id)

        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.model_dump(exclude_unset=True)

        asset = self.asset_repo.update(asset, **update_dict)
        self.db.commit()

        return asset

    def delete_asset(
        self,
        case_id: str,
        asset_id: str,
        user_id: str
    ) -> None:
        """
        Delete an asset

        Args:
            case_id: Case ID
            asset_id: Asset ID
            user_id: User ID deleting the asset

        Raises:
            HTTPException: If asset not found or user has no access
        """
        asset = self.get_asset(case_id, asset_id, user_id)
        self.asset_repo.delete(asset)
        self.db.commit()

    def calculate_division(
        self,
        case_id: str,
        user_id: str,
        plaintiff_ratio: int = 50,
        defendant_ratio: int = 50,
        include_separate: bool = False,
        notes: Optional[str] = None
    ) -> AssetDivisionSummary:
        """
        Calculate property division for a case

        Args:
            case_id: Case ID
            user_id: User ID performing calculation
            plaintiff_ratio: Plaintiff's division ratio (0-100)
            defendant_ratio: Defendant's division ratio (0-100)
            include_separate: Include separate property in calculation
            notes: Optional notes for this calculation

        Returns:
            AssetDivisionSummary with calculation results
        """
        self._verify_case_access(case_id, user_id)

        # Get all assets for the case
        assets = self.asset_repo.get_by_case_id(case_id)

        # Perform calculation
        result = self.calculator.calculate(
            assets=assets,
            plaintiff_ratio=plaintiff_ratio,
            defendant_ratio=defendant_ratio,
            include_separate=include_separate
        )

        # Save calculation result
        summary = self.summary_repo.create(
            case_id=case_id,
            calculation_result=result,
            plaintiff_ratio=plaintiff_ratio,
            defendant_ratio=defendant_ratio,
            calculated_by=user_id,
            notes=notes
        )

        self.db.commit()
        return summary

    def get_latest_summary(
        self,
        case_id: str,
        user_id: str
    ) -> Optional[AssetDivisionSummary]:
        """
        Get the most recent division summary for a case

        Args:
            case_id: Case ID
            user_id: User ID requesting the summary

        Returns:
            Latest AssetDivisionSummary or None
        """
        self._verify_case_access(case_id, user_id)
        return self.summary_repo.get_latest_by_case(case_id)

    def get_category_summaries(
        self,
        case_id: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get asset summaries grouped by category

        Args:
            case_id: Case ID
            user_id: User ID requesting summaries

        Returns:
            List of category summary dictionaries
        """
        self._verify_case_access(case_id, user_id)

        assets = self.asset_repo.get_by_case_id(case_id)
        category_data: Dict[AssetCategory, Dict[str, int]] = {}

        for asset in assets:
            if asset.category not in category_data:
                category_data[asset.category] = {
                    "total_value": 0,
                    "count": 0,
                    "plaintiff_value": 0,
                    "defendant_value": 0,
                    "joint_value": 0,
                }

            data = category_data[asset.category]
            data["total_value"] += asset.current_value
            data["count"] += 1

            if asset.ownership == AssetOwnership.PLAINTIFF:
                data["plaintiff_value"] += asset.current_value
            elif asset.ownership == AssetOwnership.DEFENDANT:
                data["defendant_value"] += asset.current_value
            else:  # Joint or third_party
                data["joint_value"] += asset.current_value

        return [
            {
                "category": category,
                "total_value": data["total_value"],
                "count": data["count"],
                "plaintiff_value": data["plaintiff_value"],
                "defendant_value": data["defendant_value"],
                "joint_value": data["joint_value"],
            }
            for category, data in category_data.items()
        ]

    def get_asset_sheet_summary(
        self,
        case_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get complete asset sheet summary including latest division calculation

        Args:
            case_id: Case ID
            user_id: User ID requesting summary

        Returns:
            Dictionary with division_summary, category_summaries, and total_assets
        """
        self._verify_case_access(case_id, user_id)

        assets = self.list_assets(case_id, user_id)
        latest_summary = self.get_latest_summary(case_id, user_id)
        category_summaries = self.get_category_summaries(case_id, user_id)

        return {
            "division_summary": latest_summary,
            "category_summaries": category_summaries,
            "total_assets": len(assets),
        }
