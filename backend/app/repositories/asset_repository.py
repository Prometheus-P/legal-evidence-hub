"""
Asset Repository - Data access layer for Asset model
Implements Repository pattern per BACKEND_SERVICE_REPOSITORY_GUIDE.md

US2 - 재산분할표 (Asset Division Sheet)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from app.db.models import Asset, AssetDivisionSummary, AssetCategory, AssetOwnership
from datetime import datetime, timezone


class AssetRepository:
    """
    Repository for Asset database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        case_id: str,
        category: AssetCategory,
        ownership: AssetOwnership,
        name: str,
        current_value: int,
        created_by: Optional[str] = None,
        **kwargs
    ) -> Asset:
        """
        Create a new asset in the database

        Args:
            case_id: Case ID this asset belongs to
            category: Asset category (real_estate, savings, etc.)
            ownership: Asset ownership (plaintiff, defendant, joint)
            name: Asset name/description
            current_value: Current value in KRW
            created_by: User ID who created the asset
            **kwargs: Additional optional fields

        Returns:
            Created Asset instance
        """
        asset = Asset(
            case_id=case_id,
            category=category,
            ownership=ownership,
            name=name,
            current_value=current_value,
            created_by=created_by,
            **kwargs
        )

        self.session.add(asset)
        self.session.flush()

        return asset

    def get_by_id(self, asset_id: str) -> Optional[Asset]:
        """
        Get asset by ID

        Args:
            asset_id: Asset ID

        Returns:
            Asset instance if found, None otherwise
        """
        return self.session.query(Asset).filter(Asset.id == asset_id).first()

    def get_by_case_id(self, case_id: str) -> List[Asset]:
        """
        Get all assets for a case

        Args:
            case_id: Case ID

        Returns:
            List of Asset instances
        """
        return (
            self.session.query(Asset)
            .filter(Asset.case_id == case_id)
            .order_by(Asset.category, Asset.created_at.desc())
            .all()
        )

    def get_by_case_and_category(
        self, case_id: str, category: AssetCategory
    ) -> List[Asset]:
        """
        Get assets for a case filtered by category

        Args:
            case_id: Case ID
            category: Asset category to filter by

        Returns:
            List of Asset instances
        """
        return (
            self.session.query(Asset)
            .filter(Asset.case_id == case_id, Asset.category == category)
            .order_by(Asset.created_at.desc())
            .all()
        )

    def update(self, asset: Asset, **kwargs) -> Asset:
        """
        Update an asset with provided fields

        Args:
            asset: Asset instance to update
            **kwargs: Fields to update

        Returns:
            Updated Asset instance
        """
        for key, value in kwargs.items():
            if hasattr(asset, key) and value is not None:
                setattr(asset, key, value)

        asset.updated_at = datetime.now(timezone.utc)
        self.session.flush()

        return asset

    def delete(self, asset: Asset) -> None:
        """
        Delete an asset (hard delete)

        Args:
            asset: Asset instance to delete
        """
        self.session.delete(asset)
        self.session.flush()

    def get_category_summary(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Get summary of assets by category for a case

        Args:
            case_id: Case ID

        Returns:
            List of dictionaries with category summaries
        """
        results = (
            self.session.query(
                Asset.category,
                func.count(Asset.id).label("count"),
                func.sum(Asset.current_value).label("total_value"),
            )
            .filter(Asset.case_id == case_id)
            .group_by(Asset.category)
            .all()
        )

        return [
            {
                "category": row.category,
                "count": row.count,
                "total_value": row.total_value or 0,
            }
            for row in results
        ]

    def get_ownership_summary(self, case_id: str) -> Dict[str, int]:
        """
        Get summary of asset values by ownership

        Args:
            case_id: Case ID

        Returns:
            Dictionary with ownership totals
        """
        results = (
            self.session.query(
                Asset.ownership,
                func.sum(Asset.current_value).label("total_value"),
            )
            .filter(Asset.case_id == case_id)
            .group_by(Asset.ownership)
            .all()
        )

        return {row.ownership.value: row.total_value or 0 for row in results}

    def bulk_update_ratios(
        self, case_id: str, plaintiff_ratio: int, defendant_ratio: int
    ) -> int:
        """
        Bulk update division ratios for all assets in a case

        Args:
            case_id: Case ID
            plaintiff_ratio: New plaintiff ratio (0-100)
            defendant_ratio: New defendant ratio (0-100)

        Returns:
            Number of assets updated
        """
        updated = (
            self.session.query(Asset)
            .filter(Asset.case_id == case_id)
            .update(
                {
                    Asset.division_ratio_plaintiff: plaintiff_ratio,
                    Asset.division_ratio_defendant: defendant_ratio,
                    Asset.updated_at: datetime.now(timezone.utc),
                },
                synchronize_session=False
            )
        )
        self.session.flush()
        return updated


class AssetDivisionSummaryRepository:
    """
    Repository for AssetDivisionSummary database operations
    """

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        case_id: str,
        calculation_result: Dict[str, Any],
        plaintiff_ratio: int,
        defendant_ratio: int,
        calculated_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> AssetDivisionSummary:
        """
        Create a new division summary record

        Args:
            case_id: Case ID
            calculation_result: Dictionary from DivisionCalculator.calculate()
            plaintiff_ratio: Ratio used for plaintiff
            defendant_ratio: Ratio used for defendant
            calculated_by: User ID who performed calculation
            notes: Optional notes

        Returns:
            Created AssetDivisionSummary instance
        """
        summary = AssetDivisionSummary(
            case_id=case_id,
            total_marital_assets=calculation_result["total_marital_assets"],
            total_separate_plaintiff=calculation_result["total_separate_plaintiff"],
            total_separate_defendant=calculation_result["total_separate_defendant"],
            total_debts=calculation_result["total_debts"],
            net_marital_value=calculation_result["net_marital_value"],
            plaintiff_share=calculation_result["plaintiff_share"],
            defendant_share=calculation_result["defendant_share"],
            settlement_amount=calculation_result["settlement_amount"],
            plaintiff_ratio=plaintiff_ratio,
            defendant_ratio=defendant_ratio,
            plaintiff_holdings=calculation_result["plaintiff_holdings"],
            defendant_holdings=calculation_result["defendant_holdings"],
            notes=notes,
            calculated_by=calculated_by,
        )

        self.session.add(summary)
        self.session.flush()

        return summary

    def get_latest_by_case(self, case_id: str) -> Optional[AssetDivisionSummary]:
        """
        Get the most recent division summary for a case

        Args:
            case_id: Case ID

        Returns:
            Most recent AssetDivisionSummary or None
        """
        return (
            self.session.query(AssetDivisionSummary)
            .filter(AssetDivisionSummary.case_id == case_id)
            .order_by(AssetDivisionSummary.calculated_at.desc())
            .first()
        )

    def get_all_by_case(self, case_id: str) -> List[AssetDivisionSummary]:
        """
        Get all division summaries for a case (history)

        Args:
            case_id: Case ID

        Returns:
            List of AssetDivisionSummary instances
        """
        return (
            self.session.query(AssetDivisionSummary)
            .filter(AssetDivisionSummary.case_id == case_id)
            .order_by(AssetDivisionSummary.calculated_at.desc())
            .all()
        )

    def delete_by_case(self, case_id: str) -> int:
        """
        Delete all division summaries for a case

        Args:
            case_id: Case ID

        Returns:
            Number of records deleted
        """
        deleted = (
            self.session.query(AssetDivisionSummary)
            .filter(AssetDivisionSummary.case_id == case_id)
            .delete(synchronize_session=False)
        )
        self.session.flush()
        return deleted
