/**
 * useTheme Hook Tests
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * NOTE: Dark mode is currently DISABLED.
 * These tests verify that the hook always returns light mode.
 */

import { renderHook } from '@testing-library/react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';
import { ReactNode } from 'react';

const createWrapper = () => {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <ThemeProvider>{children}</ThemeProvider>;
  };
};

describe('useTheme (Dark Mode Disabled)', () => {
  beforeEach(() => {
    document.documentElement.classList.remove('dark');
  });

  describe('initialization', () => {
    it('should always return light theme', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper(),
      });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });
  });

  describe('setTheme (no-op)', () => {
    it('should not change theme to dark', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper(),
      });

      result.current.setTheme('dark');

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });

    it('should not change theme to system', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper(),
      });

      result.current.setTheme('system');

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
    });
  });

  describe('toggleTheme (no-op)', () => {
    it('should not toggle theme', () => {
      const { result } = renderHook(() => useTheme(), {
        wrapper: createWrapper(),
      });

      result.current.toggleTheme();

      expect(result.current.theme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should throw error when used outside ThemeProvider', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useTheme());
      }).toThrow('useTheme must be used within a ThemeProvider');

      consoleSpy.mockRestore();
    });
  });

  describe('CSS class', () => {
    it('should never have dark class on document', () => {
      renderHook(() => useTheme(), {
        wrapper: createWrapper(),
      });

      expect(document.documentElement.classList.contains('dark')).toBe(false);
    });
  });
});
