/**
 * Integration tests for DivisionSummary Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Tests for frontend/src/components/lawyer/assets/DivisionSummary.tsx:
 * - Division calculation result display
 * - Empty state
 * - Ratio display
 * - Settlement amount calculation
 * - Recalculate button
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DivisionSummary from '@/components/lawyer/assets/DivisionSummary';
import type { DivisionSummary as DivisionSummaryType } from '@/types/asset';

const mockSummary: DivisionSummaryType = {
  id: 'div_001',
  case_id: 'case_001',
  plaintiff_ratio: 50,
  defendant_ratio: 50,
  total_marital_assets: 850000000,
  total_separate_plaintiff: 100000000,
  total_separate_defendant: 50000000,
  total_debts: 200000000,
  net_marital_value: 650000000,
  plaintiff_share: 325000000,
  defendant_share: 325000000,
  plaintiff_holdings: 400000000,
  defendant_holdings: 250000000,
  settlement_amount: 75000000, // Plaintiff → Defendant
  calculated_at: '2024-01-15T10:00:00Z',
};

const mockSummaryNegative: DivisionSummaryType = {
  ...mockSummary,
  id: 'div_002',
  plaintiff_holdings: 250000000,
  defendant_holdings: 400000000,
  settlement_amount: -75000000, // Defendant → Plaintiff
};

const mockSummaryZero: DivisionSummaryType = {
  ...mockSummary,
  id: 'div_003',
  plaintiff_holdings: 325000000,
  defendant_holdings: 325000000,
  settlement_amount: 0,
};

describe('DivisionSummary Component', () => {
  describe('Empty State', () => {
    test('should show empty message when no summary', () => {
      render(<DivisionSummary summary={null} />);

      expect(screen.getByText('아직 재산분할 계산이 수행되지 않았습니다.')).toBeInTheDocument();
    });

    test('should show calculate button in empty state when onRecalculate provided', () => {
      const onRecalculate = jest.fn();
      render(<DivisionSummary summary={null} onRecalculate={onRecalculate} />);

      expect(screen.getByText('분할 계산하기')).toBeInTheDocument();
    });

    test('should call onRecalculate when calculate button clicked in empty state', () => {
      const onRecalculate = jest.fn();
      render(
        <DivisionSummary
          summary={null}
          plaintiffRatio={60}
          defendantRatio={40}
          onRecalculate={onRecalculate}
        />
      );

      fireEvent.click(screen.getByText('분할 계산하기'));
      expect(onRecalculate).toHaveBeenCalledWith(60, 40);
    });
  });

  describe('Basic Rendering', () => {
    test('should render division summary header', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('재산분할 계산 결과')).toBeInTheDocument();
    });

    test('should render ratio display', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('분할 비율 (원고:피고)')).toBeInTheDocument();
      expect(screen.getByText('50:50')).toBeInTheDocument();
    });

    test('should render plaintiff and defendant ratio percentages', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('원고 50%')).toBeInTheDocument();
      expect(screen.getByText('피고 50%')).toBeInTheDocument();
    });
  });

  describe('Asset Totals Display', () => {
    test('should display total marital assets', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('공동재산 총액')).toBeInTheDocument();
      expect(screen.getByText('8억 5,000만원')).toBeInTheDocument();
    });

    test('should display total debts', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('부채 총액')).toBeInTheDocument();
      expect(screen.getByText('-2억원')).toBeInTheDocument();
    });

    test('should display plaintiff separate property', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('원고 특유재산')).toBeInTheDocument();
      expect(screen.getByText('1억원')).toBeInTheDocument();
    });

    test('should display defendant separate property', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('피고 특유재산')).toBeInTheDocument();
      expect(screen.getByText('5,000만원')).toBeInTheDocument();
    });
  });

  describe('Net Value and Shares', () => {
    test('should display net marital value', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('순 공동재산')).toBeInTheDocument();
      expect(screen.getByText('6억 5,000만원')).toBeInTheDocument();
    });

    test('should display calculation formula', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('공동재산 - 부채')).toBeInTheDocument();
    });

    test('should display plaintiff share', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('원고 몫')).toBeInTheDocument();
      // Shares appear twice (plaintiff and defendant have same share in 50:50)
      expect(screen.getAllByText('3억 2,500만원').length).toBe(2);
    });

    test('should display defendant share', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('피고 몫')).toBeInTheDocument();
    });

    test('should display current holdings', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('현재 보유: 4억원')).toBeInTheDocument();
      expect(screen.getByText('현재 보유: 2억 5,000만원')).toBeInTheDocument();
    });
  });

  describe('Settlement Amount - Plaintiff to Defendant', () => {
    test('should display positive settlement amount', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('정산금 (Settlement)')).toBeInTheDocument();
      expect(screen.getByText('7,500만원')).toBeInTheDocument();
    });

    test('should show direction as plaintiff to defendant', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText('원고 → 피고')).toBeInTheDocument();
    });

    test('should show explanation message for positive settlement', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(
        screen.getByText(/원고가 피고에게.*을 지급해야 합니다/)
      ).toBeInTheDocument();
    });
  });

  describe('Settlement Amount - Defendant to Plaintiff', () => {
    test('should show direction as defendant to plaintiff', () => {
      render(<DivisionSummary summary={mockSummaryNegative} />);

      expect(screen.getByText('피고 → 원고')).toBeInTheDocument();
    });

    test('should show explanation message for negative settlement', () => {
      render(<DivisionSummary summary={mockSummaryNegative} />);

      expect(
        screen.getByText(/피고가 원고에게.*을 지급해야 합니다/)
      ).toBeInTheDocument();
    });
  });

  describe('Settlement Amount - Zero', () => {
    test('should show zero when no settlement needed', () => {
      render(<DivisionSummary summary={mockSummaryZero} />);

      expect(screen.getByText('0원')).toBeInTheDocument();
    });

    test('should show "없음" for settlement direction', () => {
      render(<DivisionSummary summary={mockSummaryZero} />);

      expect(screen.getByText('없음')).toBeInTheDocument();
    });

    test('should not show explanation message when zero', () => {
      render(<DivisionSummary summary={mockSummaryZero} />);

      expect(
        screen.queryByText(/을 지급해야 합니다/)
      ).not.toBeInTheDocument();
    });
  });

  describe('Recalculate Button', () => {
    test('should show recalculate button when onRecalculate provided', () => {
      const onRecalculate = jest.fn();
      render(<DivisionSummary summary={mockSummary} onRecalculate={onRecalculate} />);

      expect(screen.getByText('재계산')).toBeInTheDocument();
    });

    test('should not show recalculate button when onRecalculate not provided', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.queryByText('재계산')).not.toBeInTheDocument();
    });

    test('should call onRecalculate when button clicked', () => {
      const onRecalculate = jest.fn();
      render(<DivisionSummary summary={mockSummary} onRecalculate={onRecalculate} />);

      fireEvent.click(screen.getByText('재계산'));
      expect(onRecalculate).toHaveBeenCalledWith(50, 50);
    });

    test('should show calculating state', () => {
      render(
        <DivisionSummary
          summary={mockSummary}
          onRecalculate={jest.fn()}
          calculating={true}
        />
      );

      expect(screen.getByText('계산 중...')).toBeInTheDocument();
    });

    test('should disable button while calculating', () => {
      render(
        <DivisionSummary
          summary={mockSummary}
          onRecalculate={jest.fn()}
          calculating={true}
        />
      );

      const button = screen.getByText('계산 중...').closest('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Timestamp Display', () => {
    test('should display calculation timestamp', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.getByText(/계산일시:/)).toBeInTheDocument();
    });
  });

  describe('Notes Display', () => {
    test('should display notes when provided', () => {
      const summaryWithNotes = {
        ...mockSummary,
        notes: '기여도 인정 비율 조정',
      };
      render(<DivisionSummary summary={summaryWithNotes} />);

      expect(screen.getByText('메모')).toBeInTheDocument();
      expect(screen.getByText('기여도 인정 비율 조정')).toBeInTheDocument();
    });

    test('should not show notes section when not provided', () => {
      render(<DivisionSummary summary={mockSummary} />);

      expect(screen.queryByText('메모')).not.toBeInTheDocument();
    });
  });

  describe('Ratio Progress Bar', () => {
    test('should render progress bar', () => {
      const { container } = render(<DivisionSummary summary={mockSummary} />);

      // Should have a progress bar with width style
      const progressBar = container.querySelector('[style*="width"]');
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    test('should apply custom className', () => {
      const { container } = render(
        <DivisionSummary summary={mockSummary} className="custom-class" />
      );

      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Visual Indicators', () => {
    test('should highlight settlement card when amount is not zero', () => {
      render(<DivisionSummary summary={mockSummary} />);

      // Settlement section should have warning styling
      const settlementText = screen.getByText('정산금 (Settlement)');
      const settlementCard = settlementText.closest('div[class*="border-warning"]');
      expect(settlementCard).toBeInTheDocument();
    });

    test('should not highlight settlement card when amount is zero', () => {
      render(<DivisionSummary summary={mockSummaryZero} />);

      const settlementText = screen.getByText('정산금 (Settlement)');
      const settlementCard = settlementText.closest('div[class*="border-warning"]');
      expect(settlementCard).not.toBeInTheDocument();
    });
  });
});
