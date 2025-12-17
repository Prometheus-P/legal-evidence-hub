/**
 * useTheme Hook Tests
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 * Task: T080
 */

import { renderHook, act } from '@testing-library/react';
import { ThemeProvider, useTheme, Theme } from '@/contexts/ThemeContext';
import { ReactNode } from 'react';

// Mock localStorage
const mockLocalStorage = (() => {
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

Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Mock matchMedia
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query: string) => ({
      matches,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
};

// Wrapper component for testing
const createWrapper = (defaultTheme?: Theme) => {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <ThemeProvider defaultTheme={defaultTheme}>
        {children}
      </ThemeProvider>
    );
  };
};

describe('useTheme', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    mockMatchMedia(false); // Default to light mode system preference
    document.documentElement.classList.remove('dark');
  });

  describe('initialization', () => {
    it('should use system preference when defaultTheme is system', () => {
      mockMatchMedia(true); // Dark mode system preference

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('system'),
      });

      expect(result.current.theme).toBe('system');
      expect(result.current.resolvedTheme).toBe('dark');
      expect(result.current.isDark).toBe(true);
    });

    it('should use stored theme from localStorage', () => {
      mockLocalStorage.setItem('leh-theme', 'dark');

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      expect(result.current.theme).toBe('dark');
      expect(result.current.resolvedTheme).toBe('dark');
    });

    it('should use defaultTheme when no stored preference', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });
  });

  describe('setTheme', () => {
    it('should update theme to dark', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      act(() => {
        result.current.setTheme('dark');
      });

      expect(result.current.theme).toBe('dark');
      expect(result.current.resolvedTheme).toBe('dark');
      expect(result.current.isDark).toBe(true);
    });

    it('should update theme to light', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('dark'),
      });

      act(() => {
        result.current.setTheme('light');
      });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });

    it('should update theme to system', () => {
      mockMatchMedia(true); // Dark system preference

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      act(() => {
        result.current.setTheme('system');
      });

      expect(result.current.theme).toBe('system');
      expect(result.current.resolvedTheme).toBe('dark');
    });

    it('should persist theme to localStorage', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      act(() => {
        result.current.setTheme('dark');
      });

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('leh-theme', 'dark');
    });
  });

  describe('toggleTheme', () => {
    it('should toggle from light to dark', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.theme).toBe('dark');
      expect(result.current.isDark).toBe(true);
    });

    it('should toggle from dark to light', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('dark'),
      });

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.theme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });

    it('should toggle from system (dark) to light', () => {
      mockMatchMedia(true); // Dark system preference

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('system'),
      });

      expect(result.current.resolvedTheme).toBe('dark');

      act(() => {
        result.current.toggleTheme();
      });

      expect(result.current.theme).toBe('light');
    });
  });

  describe('error handling', () => {
    it('should throw error when used outside ThemeProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useTheme());
      }).toThrow('useTheme must be used within a ThemeProvider');

      consoleSpy.mockRestore();
    });
  });

  describe('CSS class application', () => {
    it('should add dark class to document when theme is dark', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('light'),
      });

      act(() => {
        result.current.setTheme('dark');
      });

      expect(document.documentElement.classList.contains('dark')).toBe(true);
    });

    it('should remove dark class from document when theme is light', () => {
      document.documentElement.classList.add('dark');

      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper('dark'),
      });

      act(() => {
        result.current.setTheme('light');
      });

      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });
});
