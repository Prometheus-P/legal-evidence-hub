/**
 * ThemeContext Tests
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * NOTE: Dark mode is currently DISABLED.
 * These tests verify that the context always returns light mode.
 */

import { renderHook } from '@testing-library/react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

describe('ThemeContext (Dark Mode Disabled)', () => {
  beforeEach(() => {
    document.documentElement.classList.remove('dark');
  });

  describe('ThemeProvider', () => {
    it('should always provide light theme', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider>{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });

    it('should ignore defaultTheme prop and use light', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider defaultTheme="dark">{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });

    it('should ignore forcedTheme prop and use light', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider forcedTheme="dark">{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });
  });

  describe('useTheme hook', () => {
    it('should throw error when used outside ThemeProvider', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useTheme());
      }).toThrow('useTheme must be used within a ThemeProvider');

      consoleSpy.mockRestore();
    });

    it('should always return isDark as false', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider>{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      expect(result.current.isDark).toBe(false);
    });
  });

  describe('setTheme (no-op)', () => {
    it('should not change theme when setTheme is called', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider>{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      result.current.setTheme('dark');

      expect(result.current.theme).toBe('light');
      expect(result.current.resolvedTheme).toBe('light');
    });
  });

  describe('toggleTheme (no-op)', () => {
    it('should not change theme when toggleTheme is called', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <ThemeProvider>{children}</ThemeProvider>
      );

      const { result } = renderHook(() => useTheme(), { wrapper });

      result.current.toggleTheme();

      expect(result.current.theme).toBe('light');
      expect(result.current.isDark).toBe(false);
    });
  });
});
