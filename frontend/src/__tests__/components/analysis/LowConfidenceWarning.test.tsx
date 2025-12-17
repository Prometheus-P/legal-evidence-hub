/**
 * LowConfidenceWarning Component Tests
 * 011-production-bug-fixes Feature - #133
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { LowConfidenceWarning } from '@/components/analysis/LowConfidenceWarning';

describe('LowConfidenceWarning', () => {
  describe('Visibility', () => {
    it('renders when confidence is below threshold', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('does not render when confidence is above threshold', () => {
      render(<LowConfidenceWarning confidence={0.7} />);
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('does not render when confidence equals threshold', () => {
      render(<LowConfidenceWarning confidence={0.6} />);
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('respects custom threshold', () => {
      render(<LowConfidenceWarning confidence={0.7} threshold={0.8} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  describe('Severity Levels', () => {
    it('shows critical severity for very low confidence (< 0.4)', () => {
      render(<LowConfidenceWarning confidence={0.3} />);
      expect(screen.getByText(/매우 낮음/)).toBeInTheDocument();
      expect(screen.getByText(/반드시 수동으로 검토/)).toBeInTheDocument();
    });

    it('shows warning severity for low confidence (0.4 - 0.6)', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      expect(screen.getByText(/낮음/)).toBeInTheDocument();
      expect(screen.getByText(/참고용으로만 활용/)).toBeInTheDocument();
    });

    it('displays correct percentage', () => {
      render(<LowConfidenceWarning confidence={0.45} />);
      expect(screen.getByText(/45%/)).toBeInTheDocument();
    });
  });

  describe('Context', () => {
    it('displays custom context', () => {
      render(<LowConfidenceWarning confidence={0.5} context="OCR 분석" />);
      expect(screen.getByText(/OCR 분석 신뢰도 주의/)).toBeInTheDocument();
    });

    it('uses default context when not provided', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      expect(screen.getByText(/AI 분석 신뢰도 주의/)).toBeInTheDocument();
    });
  });

  describe('Dismissible', () => {
    it('can be dismissed when dismissible is true', () => {
      render(<LowConfidenceWarning confidence={0.5} dismissible />);

      const dismissButton = screen.getByLabelText('경고 닫기');
      fireEvent.click(dismissButton);

      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });

    it('calls onDismiss callback when dismissed', () => {
      const onDismiss = jest.fn();
      render(<LowConfidenceWarning confidence={0.5} dismissible onDismiss={onDismiss} />);

      const dismissButton = screen.getByLabelText('경고 닫기');
      fireEvent.click(dismissButton);

      expect(onDismiss).toHaveBeenCalledTimes(1);
    });

    it('does not show dismiss button when dismissible is false', () => {
      render(<LowConfidenceWarning confidence={0.5} dismissible={false} />);
      expect(screen.queryByLabelText('경고 닫기')).not.toBeInTheDocument();
    });
  });

  describe('Variants', () => {
    it('renders banner variant by default', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      expect(screen.getByText(/신뢰도 60% 미만 시 수동 검토 권장/)).toBeInTheDocument();
    });

    it('renders inline variant', () => {
      render(<LowConfidenceWarning confidence={0.5} variant="inline" />);
      expect(screen.getByText(/신뢰도 낮음/)).toBeInTheDocument();
      expect(screen.queryByText(/신뢰도 60% 미만/)).not.toBeInTheDocument();
    });

    it('renders toast variant', () => {
      render(<LowConfidenceWarning confidence={0.5} variant="toast" context="Article 840" />);
      expect(screen.getByText(/Article 840 신뢰도가 낮음입니다/)).toBeInTheDocument();
      expect(screen.getByText(/수동 검토를 권장합니다/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper alert role', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('has aria-live attribute', () => {
      render(<LowConfidenceWarning confidence={0.5} />);
      const alert = screen.getByRole('alert');
      expect(alert).toHaveAttribute('aria-live');
    });

    it('dismiss button has accessible label', () => {
      render(<LowConfidenceWarning confidence={0.5} dismissible />);
      expect(screen.getByLabelText('경고 닫기')).toBeInTheDocument();
    });
  });
});
