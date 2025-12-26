/**
 * CaseActionsDropdown Smoke Tests
 * refactor/lawyer-case-detail-ui
 *
 * Basic rendering and interaction tests for the consolidated actions dropdown.
 *
 * Dropdown now only contains: 수정
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
