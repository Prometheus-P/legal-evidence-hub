/**
 * LawyerReviewCheckbox Component Tests
 * 011-production-bug-fixes Feature - #135
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { LawyerReviewCheckbox } from '@/components/draft/LawyerReviewCheckbox';

describe('LawyerReviewCheckbox', () => {
  const defaultProps = {
    isConfirmed: false,
    onConfirmChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders checkbox with label', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      expect(screen.getByLabelText(/변호사 검토 완료 확인/)).toBeInTheDocument();
      expect(screen.getByRole('checkbox')).toBeInTheDocument();
    });

    it('renders description text', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      expect(screen.getByText(/사실관계 및 법률적 정확성을 확인/)).toBeInTheDocument();
    });

    it('shows disclaimer toggle by default', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      expect(screen.getByText('법적 고지 보기')).toBeInTheDocument();
    });

    it('hides disclaimer toggle when showDisclaimer is false', () => {
      render(<LawyerReviewCheckbox {...defaultProps} showDisclaimer={false} />);

      expect(screen.queryByText('법적 고지 보기')).not.toBeInTheDocument();
    });
  });

  describe('Checkbox State', () => {
    it('reflects isConfirmed prop (unchecked)', () => {
      render(<LawyerReviewCheckbox {...defaultProps} isConfirmed={false} />);

      expect(screen.getByRole('checkbox')).not.toBeChecked();
    });

    it('reflects isConfirmed prop (checked)', () => {
      render(<LawyerReviewCheckbox {...defaultProps} isConfirmed={true} />);

      expect(screen.getByRole('checkbox')).toBeChecked();
    });

    it('calls onConfirmChange when checkbox is clicked', () => {
      const onConfirmChange = jest.fn();
      render(<LawyerReviewCheckbox {...defaultProps} onConfirmChange={onConfirmChange} />);

      fireEvent.click(screen.getByRole('checkbox'));

      expect(onConfirmChange).toHaveBeenCalledWith(true);
    });

    it('calls onConfirmChange with false when unchecking', () => {
      const onConfirmChange = jest.fn();
      render(
        <LawyerReviewCheckbox
          {...defaultProps}
          isConfirmed={true}
          onConfirmChange={onConfirmChange}
        />
      );

      fireEvent.click(screen.getByRole('checkbox'));

      expect(onConfirmChange).toHaveBeenCalledWith(false);
    });
  });

  describe('Disabled State', () => {
    it('disables checkbox when disabled prop is true', () => {
      render(<LawyerReviewCheckbox {...defaultProps} disabled />);

      expect(screen.getByRole('checkbox')).toBeDisabled();
    });

    it('checkbox has disabled attribute when disabled', () => {
      render(<LawyerReviewCheckbox {...defaultProps} disabled />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toBeDisabled();
      expect(checkbox).toHaveClass('disabled:opacity-50');
    });
  });

  describe('Status Indicator', () => {
    it('shows "검토 필요" status when not confirmed', () => {
      render(<LawyerReviewCheckbox {...defaultProps} isConfirmed={false} />);

      expect(screen.getByText(/다운로드 전 검토 확인이 필요합니다/)).toBeInTheDocument();
    });

    it('shows "검토 완료" status when confirmed', () => {
      render(<LawyerReviewCheckbox {...defaultProps} isConfirmed={true} />);

      expect(screen.getByText(/검토 완료 확인됨/)).toBeInTheDocument();
    });
  });

  describe('Legal Disclaimer', () => {
    it('expands disclaimer when toggle is clicked', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      const toggleButton = screen.getByText('법적 고지 보기');
      fireEvent.click(toggleButton);

      expect(screen.getByText(/1\. AI 생성물 고지/)).toBeInTheDocument();
      expect(screen.getByText(/2\. 최종 책임/)).toBeInTheDocument();
      expect(screen.getByText(/3\. 사실 확인 의무/)).toBeInTheDocument();
      expect(screen.getByText(/4\. 변호사법 준수/)).toBeInTheDocument();
    });

    it('collapses disclaimer when toggle is clicked again', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      const toggleButton = screen.getByText('법적 고지 보기');
      fireEvent.click(toggleButton);

      expect(screen.getByText('법적 고지 숨기기')).toBeInTheDocument();

      fireEvent.click(screen.getByText('법적 고지 숨기기'));

      expect(screen.queryByText(/1\. AI 생성물 고지/)).not.toBeInTheDocument();
    });

    it('contains all required legal notices', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      fireEvent.click(screen.getByText('법적 고지 보기'));

      // Check all 4 required legal notices
      expect(screen.getByText(/법률 전문가의 검토 없이 사용될 경우/)).toBeInTheDocument();
      expect(screen.getByText(/최종 책임은 이를 검토하고 사용하는 변호사/)).toBeInTheDocument();
      expect(screen.getByText(/원본 자료와 대조하여 확인/)).toBeInTheDocument();
      expect(screen.getByText(/비변호사의 법률 사무 취급에 해당하지 않습니다/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('checkbox has proper id and label association', () => {
      render(<LawyerReviewCheckbox {...defaultProps} />);

      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).toHaveAttribute('id', 'lawyer-review-confirm');

      const label = screen.getByLabelText(/변호사 검토 완료 확인/);
      expect(label).toBe(checkbox);
    });

    it('label is clickable and toggles checkbox', () => {
      const onConfirmChange = jest.fn();
      render(<LawyerReviewCheckbox {...defaultProps} onConfirmChange={onConfirmChange} />);

      const label = screen.getByText('변호사 검토 완료 확인');
      fireEvent.click(label);

      expect(onConfirmChange).toHaveBeenCalledWith(true);
    });
  });
});
