/**
 * IconButton Accessibility Tests (T010)
 * TDD: Tests for touch targets and screen reader support
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import '@testing-library/jest-dom';

import { IconButton } from '@/components/primitives/IconButton/IconButton';

expect.extend(toHaveNoViolations);

// Mock icon component
const MockIcon = () => <span data-testid="mock-icon">✕</span>;

describe('IconButton Accessibility', () => {
  const defaultProps = {
    icon: <MockIcon />,
    'aria-label': '닫기',
  };

  describe('WCAG 2.1 AA Compliance', () => {
    it('should have no axe accessibility violations', async () => {
      const { container } = render(<IconButton {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations when disabled', async () => {
      const { container } = render(<IconButton {...defaultProps} disabled />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations with different variants', async () => {
      const variants = ['primary', 'secondary', 'ghost', 'destructive'] as const;

      for (const variant of variants) {
        const { container } = render(
          <IconButton {...defaultProps} variant={variant} />
        );
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      }
    });
  });

  describe('ARIA Label Requirement', () => {
    it('should have aria-label attribute', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', '닫기');
    });

    it('should use aria-label for accessible name', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button', { name: '닫기' });
      expect(button).toBeInTheDocument();
    });
  });

  describe('Touch Target Size (WCAG 2.1 AA)', () => {
    it('should have minimum 36px size for sm variant', () => {
      render(<IconButton {...defaultProps} size="sm" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-9', 'h-9'); // 36px
    });

    it('should have minimum 44px size for md variant', () => {
      render(<IconButton {...defaultProps} size="md" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-11', 'h-11'); // 44px
    });

    it('should have minimum 48px size for lg variant', () => {
      render(<IconButton {...defaultProps} size="lg" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('w-12', 'h-12'); // 48px
    });
  });

  describe('Type Attribute', () => {
    it('should default to type="button"', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'button');
    });

    it('should accept type="submit"', () => {
      render(<IconButton {...defaultProps} type="submit" />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should be focusable via keyboard', async () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');

      button.focus();
      expect(button).toHaveFocus();
    });

    it('should trigger onClick on Enter key', async () => {
      const handleClick = jest.fn();
      render(<IconButton {...defaultProps} onClick={handleClick} />);
      const button = screen.getByRole('button');

      button.focus();
      await userEvent.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should trigger onClick on Space key', async () => {
      const handleClick = jest.fn();
      render(<IconButton {...defaultProps} onClick={handleClick} />);
      const button = screen.getByRole('button');

      button.focus();
      await userEvent.keyboard(' ');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not trigger onClick when disabled', async () => {
      const handleClick = jest.fn();
      render(<IconButton {...defaultProps} disabled onClick={handleClick} />);
      const button = screen.getByRole('button');

      await userEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Focus Visibility', () => {
    it('should have focus-visible ring styles', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus-visible:ring-2');
    });

    it('should have focus ring offset', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus-visible:ring-offset-2');
    });
  });

  describe('Disabled State', () => {
    it('should have disabled attribute when disabled', () => {
      render(<IconButton {...defaultProps} disabled />);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should have reduced opacity when disabled', () => {
      render(<IconButton {...defaultProps} disabled />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:opacity-50');
    });

    it('should have not-allowed cursor when disabled', () => {
      render(<IconButton {...defaultProps} disabled />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('disabled:cursor-not-allowed');
    });
  });

  describe('Variant Styles', () => {
    it('should apply ghost variant by default', () => {
      render(<IconButton {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent');
    });

    it('should apply primary variant styles', () => {
      render(<IconButton {...defaultProps} variant="primary" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary');
    });

    it('should apply destructive variant styles', () => {
      render(<IconButton {...defaultProps} variant="destructive" />);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-error');
    });
  });

  describe('Icon Rendering', () => {
    it('should render the icon', () => {
      render(<IconButton {...defaultProps} />);
      expect(screen.getByTestId('mock-icon')).toBeInTheDocument();
    });
  });
});
