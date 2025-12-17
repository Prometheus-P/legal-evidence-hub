"""
Division Calculator Service
US2 - 재산분할표 (Asset Sheet)

Korean divorce property division calculation based on Civil Code Article 839-2.

재산분할 원칙 (민법 제839조의2):
1. 혼인 중 취득한 재산은 공동재산으로 추정
2. 특유재산(혼전재산, 상속/증여)은 분할 대상에서 제외 가능
3. 기여도에 따라 분할 비율 결정 (기본 50:50)
4. 부채도 분할 대상에 포함

정산금 계산:
- 순 공동재산 = 공동재산 총액 - 부채 총액
- 원고 몫 = 순 공동재산 × 원고 비율
- 피고 몫 = 순 공동재산 × 피고 비율
- 정산금 = 원고가 보유한 재산 - 원고 몫
  (양수: 원고가 피고에게 지급, 음수: 피고가 원고에게 지급)
"""

from typing import List, Dict, Any
from app.db.models import Asset, AssetCategory, AssetOwnership, AssetNature


class DivisionCalculator:
    """
    Calculator for Korean divorce property division.

    한국 이혼 재산분할 계산기
    """

    def calculate(
        self,
        assets: List[Asset],
        plaintiff_ratio: int = 50,
        defendant_ratio: int = 50,
        include_separate: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate property division based on assets and ratios.

        Args:
            assets: List of Asset models
            plaintiff_ratio: Plaintiff's division ratio (0-100)
            defendant_ratio: Defendant's division ratio (0-100)
            include_separate: Whether to include separate property in division

        Returns:
            Dictionary with calculation results
        """
        # Initialize totals
        total_marital_assets = 0
        total_separate_plaintiff = 0
        total_separate_defendant = 0
        total_debts = 0

        # Plaintiff's and defendant's current holdings
        plaintiff_holdings = 0  # What plaintiff currently holds
        defendant_holdings = 0  # What defendant currently holds

        # Categorize assets
        for asset in assets:
            value = asset.current_value

            # Handle debts (negative values or debt category)
            if asset.category == AssetCategory.DEBT or value < 0:
                total_debts += abs(value)
                # Assign debt to owner
                if asset.ownership == AssetOwnership.PLAINTIFF:
                    plaintiff_holdings -= abs(value)
                elif asset.ownership == AssetOwnership.DEFENDANT:
                    defendant_holdings -= abs(value)
                else:  # Joint debt
                    plaintiff_holdings -= abs(value) // 2
                    defendant_holdings -= abs(value) // 2
                continue

            # Handle by nature (marital vs separate)
            if asset.nature == AssetNature.MARITAL:
                total_marital_assets += value
                # Track current holdings
                if asset.ownership == AssetOwnership.PLAINTIFF:
                    plaintiff_holdings += value
                elif asset.ownership == AssetOwnership.DEFENDANT:
                    defendant_holdings += value
                else:  # Joint - split for holdings calculation
                    plaintiff_holdings += value // 2
                    defendant_holdings += value // 2

            elif asset.nature == AssetNature.SEPARATE:
                if asset.ownership == AssetOwnership.PLAINTIFF:
                    total_separate_plaintiff += value
                    if include_separate:
                        plaintiff_holdings += value
                elif asset.ownership == AssetOwnership.DEFENDANT:
                    total_separate_defendant += value
                    if include_separate:
                        defendant_holdings += value

            elif asset.nature == AssetNature.MIXED:
                # Mixed assets treated as marital for simplicity
                total_marital_assets += value
                if asset.ownership == AssetOwnership.PLAINTIFF:
                    plaintiff_holdings += value
                elif asset.ownership == AssetOwnership.DEFENDANT:
                    defendant_holdings += value
                else:
                    plaintiff_holdings += value // 2
                    defendant_holdings += value // 2

        # Calculate net marital value (subtract debts)
        net_marital_value = total_marital_assets - total_debts

        # Calculate shares based on ratio
        # Note: ratios should sum to 100
        total_ratio = plaintiff_ratio + defendant_ratio
        if total_ratio == 0:
            total_ratio = 100  # Prevent division by zero

        plaintiff_share = int(net_marital_value * plaintiff_ratio / total_ratio)
        defendant_share = int(net_marital_value * defendant_ratio / total_ratio)

        # Settlement amount calculation
        # Positive = plaintiff pays defendant
        # Negative = defendant pays plaintiff
        settlement_amount = plaintiff_holdings - plaintiff_share

        return {
            "total_marital_assets": total_marital_assets,
            "total_separate_plaintiff": total_separate_plaintiff,
            "total_separate_defendant": total_separate_defendant,
            "total_debts": total_debts,
            "net_marital_value": net_marital_value,
            "plaintiff_share": plaintiff_share,
            "defendant_share": defendant_share,
            "settlement_amount": settlement_amount,
            "plaintiff_holdings": plaintiff_holdings,
            "defendant_holdings": defendant_holdings,
        }

    def calculate_with_contribution(
        self,
        assets: List[Asset],
        plaintiff_contribution: float = 0.5,
        defendant_contribution: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Calculate division based on contribution ratios (기여도 기반).

        This is an alternative calculation method that considers
        each party's contribution to the marital estate.

        Args:
            assets: List of Asset models
            plaintiff_contribution: Plaintiff's contribution factor (0.0-1.0)
            defendant_contribution: Defendant's contribution factor (0.0-1.0)
        """
        # Normalize contribution ratios
        total_contribution = plaintiff_contribution + defendant_contribution
        if total_contribution == 0:
            total_contribution = 1

        p_ratio = int(100 * plaintiff_contribution / total_contribution)
        d_ratio = 100 - p_ratio

        return self.calculate(
            assets=assets,
            plaintiff_ratio=p_ratio,
            defendant_ratio=d_ratio,
        )

    def suggest_fair_division(self, assets: List[Asset]) -> Dict[str, Any]:
        """
        Suggest a fair division based on Korean legal standards.

        기본 원칙:
        - 맞벌이: 50:50
        - 외벌이 + 가사노동: 40:60 또는 50:50
        - 재혼/단기혼: 기여도 비례

        This is a simplified suggestion - actual courts consider many factors.
        """
        # Default to 50:50 as the standard baseline
        return self.calculate(
            assets=assets,
            plaintiff_ratio=50,
            defendant_ratio=50,
        )

    def format_amount(self, amount: int) -> str:
        """Format amount in Korean currency style"""
        if amount >= 100000000:  # 억
            eok = amount // 100000000
            man = (amount % 100000000) // 10000
            if man > 0:
                return f"{eok}억 {man:,}만원"
            return f"{eok}억원"
        elif amount >= 10000:  # 만
            man = amount // 10000
            return f"{man:,}만원"
        else:
            return f"{amount:,}원"
