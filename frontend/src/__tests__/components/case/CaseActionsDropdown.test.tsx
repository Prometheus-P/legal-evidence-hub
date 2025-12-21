/**
 * CaseActionsDropdown Smoke Tests
 * refactor/lawyer-case-detail-ui
 *
 * Basic rendering and interaction tests for the consolidated actions dropdown.
 *
 * Note: 재산분할 and 요약 카드 have been moved to main tabs (Calm Control UX).
 * Dropdown now only contains: 수정, 전문가 인사이트 (optional)
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { CaseActionsDropdown } from '@/components/case/CaseActionsDropdown';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

describe('CaseActionsDropdown', () => {
  const defaultProps = {
    onEdit: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('should render the dropdown trigger button', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      expect(button).toBeInTheDocument();
    });

    it('should not show dropdown menu initially', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('dropdown interaction', () => {
    it('should open dropdown menu when clicked', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      fireEvent.click(button);

      expect(screen.getByRole('menu')).toBeInTheDocument();
    });

    it('should show edit menu item when opened', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      fireEvent.click(button);

      expect(screen.getByText('수정')).toBeInTheDocument();
    });

    it('should close dropdown when clicking toggle again', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      fireEvent.click(button); // open
      fireEvent.click(button); // close

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('menu item actions', () => {
    it('should call onEdit when edit is clicked', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      fireEvent.click(screen.getByRole('button', { name: '더보기' }));
      fireEvent.click(screen.getByText('수정'));

      expect(defaultProps.onEdit).toHaveBeenCalledTimes(1);
    });

    it('should close dropdown after clicking menu item', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      fireEvent.click(screen.getByRole('button', { name: '더보기' }));
      fireEvent.click(screen.getByText('수정'));

      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  describe('expert insights', () => {
    it('should show expert insights when handler is provided', () => {
      const onExpertInsights = jest.fn();
      render(
        <CaseActionsDropdown {...defaultProps} onExpertInsights={onExpertInsights} />
      );

      fireEvent.click(screen.getByRole('button', { name: '더보기' }));

      expect(screen.getByText('전문가 인사이트')).toBeInTheDocument();
    });

    it('should not show expert insights when handler is not provided', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      fireEvent.click(screen.getByRole('button', { name: '더보기' }));

      expect(screen.queryByText('전문가 인사이트')).not.toBeInTheDocument();
    });

    it('should call onExpertInsights when clicked', () => {
      const onExpertInsights = jest.fn();
      render(
        <CaseActionsDropdown {...defaultProps} onExpertInsights={onExpertInsights} />
      );

      fireEvent.click(screen.getByRole('button', { name: '더보기' }));
      fireEvent.click(screen.getByText('전문가 인사이트'));

      expect(onExpertInsights).toHaveBeenCalledTimes(1);
    });
  });

  describe('deprecated props (backwards compatibility)', () => {
    it('should accept deprecated assetsPath prop without error', () => {
      render(
        <CaseActionsDropdown
          {...defaultProps}
          assetsPath="/lawyer/cases/123/assets"
        />
      );

      expect(screen.getByRole('button', { name: '더보기' })).toBeInTheDocument();
    });

    it('should accept deprecated onSummaryCard prop without error', () => {
      render(
        <CaseActionsDropdown
          {...defaultProps}
          onSummaryCard={jest.fn()}
        />
      );

      expect(screen.getByRole('button', { name: '더보기' })).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have correct aria attributes on trigger', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      expect(button).toHaveAttribute('aria-expanded', 'false');
      expect(button).toHaveAttribute('aria-haspopup', 'menu');
    });

    it('should update aria-expanded when opened', () => {
      render(<CaseActionsDropdown {...defaultProps} />);

      const button = screen.getByRole('button', { name: '더보기' });
      fireEvent.click(button);

      expect(button).toHaveAttribute('aria-expanded', 'true');
    });
  });
});
