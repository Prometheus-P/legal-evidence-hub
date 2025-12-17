"""
Unit tests for Division Calculator Service
TDD for US2 - 재산분할표 (Asset Division Sheet)

Tests Korean divorce property division calculation based on Civil Code Article 839-2.
"""

from unittest.mock import MagicMock
from app.services.division_calculator import DivisionCalculator
from app.db.models import Asset, AssetCategory, AssetOwnership, AssetNature


def create_mock_asset(
    category: AssetCategory,
    ownership: AssetOwnership,
    current_value: int,
    nature: AssetNature = AssetNature.MARITAL,
    **kwargs
) -> Asset:
    """Helper to create mock Asset objects for testing"""
    asset = MagicMock(spec=Asset)
    asset.category = category
    asset.ownership = ownership
    asset.current_value = current_value
    asset.nature = nature
    for key, value in kwargs.items():
        setattr(asset, key, value)
    return asset


class TestDivisionCalculatorBasic:
    """Basic calculation tests"""

    def test_empty_assets_returns_zero_values(self):
        """
        Given: No assets
        When: calculate is called
        Then: All values should be 0
        """
        calculator = DivisionCalculator()
        result = calculator.calculate(assets=[], plaintiff_ratio=50, defendant_ratio=50)

        assert result["total_marital_assets"] == 0
        assert result["total_debts"] == 0
        assert result["net_marital_value"] == 0
        assert result["plaintiff_share"] == 0
        assert result["defendant_share"] == 0
        assert result["settlement_amount"] == 0

    def test_single_plaintiff_asset_50_50_split(self):
        """
        Given: Single marital asset owned by plaintiff worth 100M
        When: calculate with 50:50 ratio
        Then: Plaintiff should pay defendant 50M settlement
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        assert result["total_marital_assets"] == 100_000_000
        assert result["net_marital_value"] == 100_000_000
        assert result["plaintiff_share"] == 50_000_000
        assert result["defendant_share"] == 50_000_000
        assert result["plaintiff_holdings"] == 100_000_000
        assert result["defendant_holdings"] == 0
        # Plaintiff holds 100M but entitled to 50M, so pays 50M
        assert result["settlement_amount"] == 50_000_000

    def test_single_defendant_asset_50_50_split(self):
        """
        Given: Single marital asset owned by defendant worth 100M
        When: calculate with 50:50 ratio
        Then: Defendant should pay plaintiff 50M settlement (negative value)
        """
        asset = create_mock_asset(
            category=AssetCategory.SAVINGS,
            ownership=AssetOwnership.DEFENDANT,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        assert result["plaintiff_share"] == 50_000_000
        assert result["defendant_share"] == 50_000_000
        assert result["plaintiff_holdings"] == 0
        assert result["defendant_holdings"] == 100_000_000
        # Plaintiff holds 0 but entitled to 50M, so receives 50M (negative settlement)
        assert result["settlement_amount"] == -50_000_000


class TestDivisionCalculatorRatios:
    """Tests for different division ratios"""

    def test_60_40_ratio_favoring_plaintiff(self):
        """
        Given: Asset worth 100M owned by plaintiff
        When: calculate with 60:40 (plaintiff:defendant) ratio
        Then: Plaintiff pays 40M to defendant
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset],
            plaintiff_ratio=60,
            defendant_ratio=40
        )

        assert result["plaintiff_share"] == 60_000_000
        assert result["defendant_share"] == 40_000_000
        # Plaintiff holds 100M but entitled to 60M, so pays 40M
        assert result["settlement_amount"] == 40_000_000

    def test_40_60_ratio_favoring_defendant(self):
        """
        Given: Asset worth 100M owned by plaintiff
        When: calculate with 40:60 (plaintiff:defendant) ratio
        Then: Plaintiff pays 60M to defendant
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset],
            plaintiff_ratio=40,
            defendant_ratio=60
        )

        assert result["plaintiff_share"] == 40_000_000
        assert result["defendant_share"] == 60_000_000
        # Plaintiff holds 100M but entitled to 40M, so pays 60M
        assert result["settlement_amount"] == 60_000_000


class TestDivisionCalculatorDebt:
    """Tests for debt handling"""

    def test_debt_reduces_net_marital_value(self):
        """
        Given: Asset worth 100M and debt of 30M
        When: calculate with 50:50 ratio
        Then: Net marital value is 70M
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )
        debt = create_mock_asset(
            category=AssetCategory.DEBT,
            ownership=AssetOwnership.JOINT,
            current_value=30_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset, debt],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        assert result["total_marital_assets"] == 100_000_000
        assert result["total_debts"] == 30_000_000
        assert result["net_marital_value"] == 70_000_000
        assert result["plaintiff_share"] == 35_000_000
        assert result["defendant_share"] == 35_000_000

    def test_debt_assigned_to_owner(self):
        """
        Given: Debt of 30M owned by plaintiff
        When: calculate
        Then: Debt reduces plaintiff's holdings
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )
        debt = create_mock_asset(
            category=AssetCategory.DEBT,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=30_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[asset, debt],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        # Plaintiff holds 100M asset - 30M debt = 70M
        assert result["plaintiff_holdings"] == 70_000_000
        assert result["defendant_holdings"] == 0


class TestDivisionCalculatorSeparateProperty:
    """Tests for separate property (특유재산) handling"""

    def test_separate_property_excluded_by_default(self):
        """
        Given: Separate property (혼전재산) owned by plaintiff
        When: calculate with include_separate=False
        Then: Separate property is not included in division
        """
        marital = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )
        separate = create_mock_asset(
            category=AssetCategory.SAVINGS,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=50_000_000,
            nature=AssetNature.SEPARATE
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[marital, separate],
            plaintiff_ratio=50,
            defendant_ratio=50,
            include_separate=False
        )

        assert result["total_marital_assets"] == 100_000_000
        assert result["total_separate_plaintiff"] == 50_000_000
        assert result["total_separate_defendant"] == 0
        # Only marital assets considered for holdings when include_separate=False
        assert result["plaintiff_holdings"] == 100_000_000

    def test_separate_property_included_when_requested(self):
        """
        Given: Separate property (혼전재산) owned by plaintiff
        When: calculate with include_separate=True
        Then: Separate property is included in holdings calculation
        """
        marital = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )
        separate = create_mock_asset(
            category=AssetCategory.SAVINGS,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=50_000_000,
            nature=AssetNature.SEPARATE
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[marital, separate],
            plaintiff_ratio=50,
            defendant_ratio=50,
            include_separate=True
        )

        # Separate property added to holdings when include_separate=True
        assert result["plaintiff_holdings"] == 150_000_000


class TestDivisionCalculatorJointAssets:
    """Tests for jointly owned assets"""

    def test_joint_asset_split_for_holdings(self):
        """
        Given: Joint asset worth 100M
        When: calculate
        Then: Holdings are split 50/50 between parties
        """
        joint_asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.JOINT,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[joint_asset],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        assert result["total_marital_assets"] == 100_000_000
        assert result["plaintiff_holdings"] == 50_000_000
        assert result["defendant_holdings"] == 50_000_000
        # Settlement is 0 when holdings already match shares
        assert result["settlement_amount"] == 0


class TestDivisionCalculatorMixedAssets:
    """Tests for mixed assets (혼합재산)"""

    def test_mixed_assets_treated_as_marital(self):
        """
        Given: Mixed asset (partially marital, partially separate)
        When: calculate
        Then: Mixed assets are treated as marital for division
        """
        mixed = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MIXED
        )

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=[mixed],
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        assert result["total_marital_assets"] == 100_000_000
        assert result["plaintiff_share"] == 50_000_000


class TestDivisionCalculatorContribution:
    """Tests for contribution-based calculation (기여도 기반)"""

    def test_calculate_with_contribution_normalizes_ratios(self):
        """
        Given: Plaintiff contribution 0.6, defendant contribution 0.4
        When: calculate_with_contribution is called
        Then: Ratios are normalized to 60:40
        """
        asset = create_mock_asset(
            category=AssetCategory.REAL_ESTATE,
            ownership=AssetOwnership.PLAINTIFF,
            current_value=100_000_000,
            nature=AssetNature.MARITAL
        )

        calculator = DivisionCalculator()
        result = calculator.calculate_with_contribution(
            assets=[asset],
            plaintiff_contribution=0.6,
            defendant_contribution=0.4
        )

        assert result["plaintiff_share"] == 60_000_000
        assert result["defendant_share"] == 40_000_000


class TestDivisionCalculatorFormatAmount:
    """Tests for Korean currency formatting"""

    def test_format_amount_eok(self):
        """Test formatting for 억 unit"""
        calculator = DivisionCalculator()
        assert calculator.format_amount(100_000_000) == "1억원"
        assert calculator.format_amount(250_000_000) == "2억 5,000만원"

    def test_format_amount_man(self):
        """Test formatting for 만 unit"""
        calculator = DivisionCalculator()
        assert calculator.format_amount(50_000_000) == "5,000만원"
        assert calculator.format_amount(1_000_000) == "100만원"

    def test_format_amount_won(self):
        """Test formatting for small amounts"""
        calculator = DivisionCalculator()
        assert calculator.format_amount(5000) == "5,000원"
        assert calculator.format_amount(100) == "100원"


class TestDivisionCalculatorComplexScenario:
    """Complex real-world scenario tests"""

    def test_complex_divorce_scenario(self):
        """
        Given: Multiple assets and debts representing a typical divorce case
        - Plaintiff: apartment 500M, car 30M, savings 50M, mortgage debt 200M
        - Defendant: retirement 80M, stocks 40M, credit card debt 10M
        - Joint: pension 60M
        When: calculate with 50:50 ratio
        Then: Settlement calculated correctly
        """
        assets = [
            # Plaintiff's assets
            create_mock_asset(AssetCategory.REAL_ESTATE, AssetOwnership.PLAINTIFF, 500_000_000, AssetNature.MARITAL),
            create_mock_asset(AssetCategory.VEHICLE, AssetOwnership.PLAINTIFF, 30_000_000, AssetNature.MARITAL),
            create_mock_asset(AssetCategory.SAVINGS, AssetOwnership.PLAINTIFF, 50_000_000, AssetNature.MARITAL),
            create_mock_asset(AssetCategory.DEBT, AssetOwnership.PLAINTIFF, 200_000_000, AssetNature.MARITAL),
            # Defendant's assets
            create_mock_asset(AssetCategory.RETIREMENT, AssetOwnership.DEFENDANT, 80_000_000, AssetNature.MARITAL),
            create_mock_asset(AssetCategory.STOCKS, AssetOwnership.DEFENDANT, 40_000_000, AssetNature.MARITAL),
            create_mock_asset(AssetCategory.DEBT, AssetOwnership.DEFENDANT, 10_000_000, AssetNature.MARITAL),
            # Joint assets
            create_mock_asset(AssetCategory.INSURANCE, AssetOwnership.JOINT, 60_000_000, AssetNature.MARITAL),
        ]

        calculator = DivisionCalculator()
        result = calculator.calculate(
            assets=assets,
            plaintiff_ratio=50,
            defendant_ratio=50
        )

        # Total marital assets: 500M + 30M + 50M + 80M + 40M + 60M = 760M
        assert result["total_marital_assets"] == 760_000_000
        # Total debts: 200M + 10M = 210M
        assert result["total_debts"] == 210_000_000
        # Net marital value: 760M - 210M = 550M
        assert result["net_marital_value"] == 550_000_000

        # Each party's share: 550M / 2 = 275M
        assert result["plaintiff_share"] == 275_000_000
        assert result["defendant_share"] == 275_000_000

        # Plaintiff holdings: 500M + 30M + 50M - 200M + 30M (half of joint) = 410M
        # Wait, joint 60M, half is 30M. 500 + 30 + 50 - 200 + 30 = 410M
        assert result["plaintiff_holdings"] == 410_000_000

        # Defendant holdings: 80M + 40M - 10M + 30M (half of joint) = 140M
        assert result["defendant_holdings"] == 140_000_000

        # Settlement: 410M (plaintiff holdings) - 275M (plaintiff share) = 135M
        # Plaintiff pays defendant 135M
        assert result["settlement_amount"] == 135_000_000
