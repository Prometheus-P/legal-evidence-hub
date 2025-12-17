/**
 * ThemeContext
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * Global theme context for dark/light mode switching.
 * Features:
 * - System preference detection (prefers-color-scheme)
 * - localStorage persistence
 * - Prevents flash on page load
 */

'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeContextType {
  /** Current theme setting (light, dark, or system) */
  theme: Theme;
  /** Resolved theme after applying system preference */
  resolvedTheme: ResolvedTheme;
  /** Whether the theme is dark */
  isDark: boolean;
  /** Set theme preference */
  setTheme: (theme: Theme) => void;
  /** Toggle between light and dark */
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'leh-theme';

interface ThemeProviderProps {
  children: ReactNode;
  /** Default theme if none stored */
  defaultTheme?: Theme;
  /** Force a specific theme (for testing) */
  forcedTheme?: Theme;
}

/**
 * Get system color scheme preference
 */
function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Get stored theme from localStorage
 */
function getStoredTheme(): Theme | null {
  if (typeof window === 'undefined') return null;
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored;
    }
  } catch {
    // localStorage not available
  }
  return null;
}

/**
 * Save theme to localStorage
 */
function storeTheme(theme: Theme): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // localStorage not available
  }
}

/**
 * Apply theme class to document
 */
function applyTheme(resolvedTheme: ResolvedTheme): void {
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  if (resolvedTheme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

/**
 * Resolve theme to actual light/dark value
 */
function resolveTheme(theme: Theme): ResolvedTheme {
  if (theme === 'system') {
    return getSystemTheme();
  }
  return theme;
}

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  forcedTheme,
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => {
    // On server, use default
    if (typeof window === 'undefined') return defaultTheme;
    // Check for forced theme
    if (forcedTheme) return forcedTheme;
    // Check localStorage
    return getStoredTheme() || defaultTheme;
  });

  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() => {
    return resolveTheme(forcedTheme || theme);
  });

  // Apply theme on mount and when theme changes
  useEffect(() => {
    const effectiveTheme = forcedTheme || theme;
    const resolved = resolveTheme(effectiveTheme);
    setResolvedTheme(resolved);
    applyTheme(resolved);
  }, [theme, forcedTheme]);

  // Listen for system preference changes
  useEffect(() => {
    if (forcedTheme) return;
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e: MediaQueryListEvent) => {
      const newResolved = e.matches ? 'dark' : 'light';
      setResolvedTheme(newResolved);
      applyTheme(newResolved);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, forcedTheme]);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    storeTheme(newTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    // If system, switch to opposite of current resolved
    // Otherwise, toggle between light and dark
    const newTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  }, [resolvedTheme, setTheme]);

  const value: ThemeContextType = {
    theme: forcedTheme || theme,
    resolvedTheme,
    isDark: resolvedTheme === 'dark',
    setTheme,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * useTheme hook
 * Access theme context from any component
 *
 * @example
 * const { isDark, toggleTheme, setTheme } = useTheme();
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export default ThemeContext;
