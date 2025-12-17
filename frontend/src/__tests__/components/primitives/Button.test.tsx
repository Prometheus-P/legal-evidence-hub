/**
 * Button Accessibility Tests (T007)
 * TDD: Tests should FAIL until design token integration is complete
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import '@testing-library/jest-dom';

import { Button } from '@/components/primitives/Button/Button';

expect.extend(toHaveNoViolations);

describe('Button Accessibility', () => {
  describe('WCAG 2.1 AA Compliance', () => {
    it('should have no axe accessibility violations', async () => {
      const { container } = render(<Button>Click me</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations when disabled', async () => {
      const { container } = render(<Button disabled>Disabled</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no violations when loading', async () => {
      const { container } = render(<Button isLoading>Loading</Button>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should be focusable via keyboard', async () => {
      render(<Button>Focusable</Button>);
      const button = screen.getByRole('button', { name: 'Focusable' });

      button.focus();
      expect(button).toHaveFocus();
    });

    it('should trigger onClick on Enter key', async () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Press Enter</Button>);
      const button = screen.getByRole('button');

      button.focus();
      await userEvent.keyboard('{Enter}');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should trigger onClick on Space key', async () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Press Space</Button>);
      const button = screen.getByRole('button');

      button.focus();
      await userEvent.keyboard(' ');
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should not trigger onClick when disabled', async () => {
      const handleClick = jest.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      const button = screen.getByRole('button');

      await userEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Type Attribute', () => {
    it('should default to type="button"', () => {
      render(<Button>Default Type</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'button');
    });

    it('should accept type="submit"', () => {
      render(<Button type="submit">Submit</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });
  });

  describe('ARIA Attributes', () => {
    it('should have aria-busy="true" when loading', () => {
      render(<Button isLoading>Loading</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-busy', 'true');
    });

    it('should have aria-disabled="true" when disabled', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have aria-disabled="true" when loading', () => {
      render(<Button isLoading>Loading</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-disabled', 'true');
    });
  });

  describe('Touch Target Size (WCAG 2.1 AA)', () => {
    it('should have minimum 44px height', () => {
      render(<Button>Touch Target</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('min-h-[44px]');
    });

    it('should have minimum 44px width', () => {
      render(<Button>Touch Target</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('min-w-[44px]');
    });
  });

  describe('Focus Visibility', () => {
    it('should have focus-visible ring styles', () => {
      render(<Button>Focus Ring</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('focus-visible:ring-2');
    });
  });

  describe('Screen Reader Support', () => {
    it('should announce loading state to screen readers', () => {
      render(<Button isLoading loadingText="저장 중...">Save</Button>);
      // Multiple sr-only elements exist (one in Spinner, one in Button)
      const srOnlyElements = screen.getAllByText('저장 중...');
      expect(srOnlyElements.length).toBeGreaterThan(0);
      expect(srOnlyElements.some(el => el.classList.contains('sr-only'))).toBe(true);
    });
  });

  describe('Variant Styles', () => {
    it('should apply primary variant styles', () => {
      render(<Button variant="primary">Primary</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary');
    });

    it('should apply destructive variant styles', () => {
      render(<Button variant="destructive">Delete</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-error');
    });
  });
});
