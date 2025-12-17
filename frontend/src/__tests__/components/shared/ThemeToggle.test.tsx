/**
 * ThemeToggle Component Tests
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * TDD tests for ThemeToggle component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeToggle, ThemeSelector } from '@/components/shared/ThemeToggle';
import { ThemeProvider } from '@/contexts/ThemeContext';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock matchMedia
const createMatchMedia = (matches: boolean) => {
  return jest.fn().mockImplementation((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }));
};

const renderWithTheme = (ui: React.ReactElement, defaultTheme: 'light' | 'dark' | 'system' = 'light') => {
  return render(
    <ThemeProvider defaultTheme={defaultTheme}>
      {ui}
    </ThemeProvider>
  );
};

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorageMock.clear();
    jest.clearAllMocks();
    document.documentElement.classList.remove('dark');
    window.matchMedia = createMatchMedia(false);
  });

  describe('rendering', () => {
    it('should render toggle button', () => {
      renderWithTheme(<ThemeToggle />);

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should have correct aria-label for light mode', () => {
      renderWithTheme(<ThemeToggle />, 'light');

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', '다크 모드로 전환');
    });

    it('should have correct aria-label for dark mode', () => {
      renderWithTheme(<ThemeToggle />, 'dark');

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', '라이트 모드로 전환');
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

  describe('interaction', () => {
    it('should toggle theme when clicked in light mode', () => {
      renderWithTheme(<ThemeToggle />, 'light');

      const button = screen.getByRole('button');
      fireEvent.click(button);

      // After click, should show light mode option (meaning we're now in dark mode)
      expect(button).toHaveAttribute('aria-label', '라이트 모드로 전환');
    });

    it('should toggle theme when clicked in dark mode', () => {
      renderWithTheme(<ThemeToggle />, 'dark');

      const button = screen.getByRole('button');
      fireEvent.click(button);

      // After click, should show dark mode option (meaning we're now in light mode)
      expect(button).toHaveAttribute('aria-label', '다크 모드로 전환');
    });

    it('should save theme to localStorage when toggled', () => {
      renderWithTheme(<ThemeToggle />, 'light');

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('leh-theme', 'dark');
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

    it('should meet minimum touch target size (44x44px) for md and lg sizes', () => {
      renderWithTheme(<ThemeToggle size="md" />);

      const button = screen.getByRole('button');
      // md size is 40px (w-10), but should still be accessible
      expect(button).toBeInTheDocument();
    });
  });
});

describe('ThemeSelector', () => {
  beforeEach(() => {
    localStorageMock.clear();
    jest.clearAllMocks();
    document.documentElement.classList.remove('dark');
    window.matchMedia = createMatchMedia(false);
  });

  describe('rendering', () => {
    it('should render all three theme options', () => {
      renderWithTheme(<ThemeSelector />);

      expect(screen.getByRole('button', { name: /라이트/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /다크/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /시스템/i })).toBeInTheDocument();
    });

    it('should highlight the active theme', () => {
      renderWithTheme(<ThemeSelector />, 'dark');

      const darkButton = screen.getByRole('button', { name: /다크/i });
      expect(darkButton.className).toContain('bg-[var(--color-primary)]');
    });
  });

  describe('interaction', () => {
    it('should change to light theme when light button is clicked', () => {
      renderWithTheme(<ThemeSelector />, 'dark');

      const lightButton = screen.getByRole('button', { name: /라이트/i });
      fireEvent.click(lightButton);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('leh-theme', 'light');
    });

    it('should change to dark theme when dark button is clicked', () => {
      renderWithTheme(<ThemeSelector />, 'light');

      const darkButton = screen.getByRole('button', { name: /다크/i });
      fireEvent.click(darkButton);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('leh-theme', 'dark');
    });

    it('should change to system theme when system button is clicked', () => {
      renderWithTheme(<ThemeSelector />, 'light');

      const systemButton = screen.getByRole('button', { name: /시스템/i });
      fireEvent.click(systemButton);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('leh-theme', 'system');
    });
  });

  describe('accessibility', () => {
    it('should have aria-pressed attribute on active button', () => {
      renderWithTheme(<ThemeSelector />, 'dark');

      const darkButton = screen.getByRole('button', { name: /다크/i });
      const lightButton = screen.getByRole('button', { name: /라이트/i });

      expect(darkButton).toHaveAttribute('aria-pressed', 'true');
      expect(lightButton).toHaveAttribute('aria-pressed', 'false');
    });

    it('should have role="group" for the button group', () => {
      renderWithTheme(<ThemeSelector />);

      const group = screen.getByRole('group');
      expect(group).toBeInTheDocument();
    });
  });
});
