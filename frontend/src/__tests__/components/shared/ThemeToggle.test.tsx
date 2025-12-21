/**
 * ThemeToggle Component Tests
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * NOTE: Dark mode is currently DISABLED.
 * These tests verify that the component renders but toggle is a no-op.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeToggle, ThemeSelector } from '@/components/shared/ThemeToggle';
import { ThemeProvider } from '@/contexts/ThemeContext';

const renderWithTheme = (ui: React.ReactElement) => {
  return render(
    <ThemeProvider>
      {ui}
    </ThemeProvider>
  );
};

describe('ThemeToggle (Dark Mode Disabled)', () => {
  beforeEach(() => {
    document.documentElement.classList.remove('dark');
  });

  describe('rendering', () => {
    it('should render toggle button', () => {
      renderWithTheme(<ThemeToggle />);

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should always show "switch to dark mode" label since we are always in light mode', () => {
      renderWithTheme(<ThemeToggle />);

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', '다크 모드로 전환');
    });

    it('should show label when showLabel is true', () => {
      renderWithTheme(<ThemeToggle showLabel />);

      expect(screen.getByText('다크 모드')).toBeInTheDocument();
    });

    it('should not show label by default', () => {
      renderWithTheme(<ThemeToggle />);

      expect(screen.queryByText('다크 모드')).not.toBeInTheDocument();
      expect(screen.queryByText('라이트 모드')).not.toBeInTheDocument();
    });
  });

  describe('interaction (no-op)', () => {
    it('should not change theme when clicked (dark mode disabled)', () => {
      renderWithTheme(<ThemeToggle />);

      const button = screen.getByRole('button');
      fireEvent.click(button);

      // Should still show dark mode option since we're always in light mode
      expect(button).toHaveAttribute('aria-label', '다크 모드로 전환');
    });
  });

  describe('sizes', () => {
    it('should render with small size', () => {
      renderWithTheme(<ThemeToggle size="sm" />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('w-8');
      expect(button.className).toContain('h-8');
    });

    it('should render with medium size', () => {
      renderWithTheme(<ThemeToggle size="md" />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('w-10');
      expect(button.className).toContain('h-10');
    });

    it('should render with large size', () => {
      renderWithTheme(<ThemeToggle size="lg" />);

      const button = screen.getByRole('button');
      expect(button.className).toContain('w-12');
      expect(button.className).toContain('h-12');
    });
  });

  describe('accessibility', () => {
    it('should be focusable', () => {
      renderWithTheme(<ThemeToggle />);

      const button = screen.getByRole('button');
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });
});

describe('ThemeSelector (Dark Mode Disabled)', () => {
  beforeEach(() => {
    document.documentElement.classList.remove('dark');
  });

  describe('rendering', () => {
    it('should render all three theme options', () => {
      renderWithTheme(<ThemeSelector />);

      expect(screen.getByRole('button', { name: /라이트/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다크/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /시스템/i })).toBeInTheDocument();
    });

    it('should always highlight light theme since dark mode is disabled', () => {
      renderWithTheme(<ThemeSelector />);

      const lightButton = screen.getByRole('button', { name: /라이트/i });
      expect(lightButton.className).toContain('bg-[var(--color-primary)]');
    });
  });

  describe('interaction (no-op)', () => {
    it('should not change theme when buttons are clicked (dark mode disabled)', () => {
      renderWithTheme(<ThemeSelector />);

      const darkButton = screen.getByRole('button', { name: /다크/i });
      fireEvent.click(darkButton);

      // Light should still be active
      const lightButton = screen.getByRole('button', { name: /라이트/i });
      expect(lightButton.className).toContain('bg-[var(--color-primary)]');
    });
  });

  describe('accessibility', () => {
    it('should have aria-pressed attribute on light button (always active)', () => {
      renderWithTheme(<ThemeSelector />);

      const lightButton = screen.getByRole('button', { name: /라이트/i });
      expect(lightButton).toHaveAttribute('aria-pressed', 'true');
    });

    it('should have role="group" for the button group', () => {
      renderWithTheme(<ThemeSelector />);

      const group = screen.getByRole('group');
      expect(group).toBeInTheDocument();
    });
  });
});
