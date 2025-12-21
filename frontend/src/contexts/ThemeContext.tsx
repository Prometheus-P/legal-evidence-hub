/**
 * ThemeContext
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * NOTE: Dark mode is currently DISABLED.
 * This context always returns light mode for consistency.
 * To re-enable dark mode, restore the original implementation.
 */

'use client';

import {
  createContext,
  useContext,
  useEffect,
  ReactNode,
} from 'react';

export type Theme = 'light' | 'dark' | 'system';
export type ResolvedTheme = 'light' | 'dark';

interface ThemeContextType {
  /** Current theme setting (always 'light' - dark mode disabled) */
  theme: Theme;
  /** Resolved theme (always 'light' - dark mode disabled) */
  resolvedTheme: ResolvedTheme;
  /** Whether the theme is dark (always false - dark mode disabled) */
  isDark: boolean;
  /** Set theme preference (no-op - dark mode disabled) */
  setTheme: (theme: Theme) => void;
  /** Toggle between light and dark (no-op - dark mode disabled) */
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  /** Default theme if none stored */
  defaultTheme?: Theme;
  /** Force a specific theme (for testing) */
  forcedTheme?: Theme;
}

/**
 * Ensure dark class is removed from document
 */
function ensureLightMode(): void {
  if (typeof document === 'undefined') return;
  document.documentElement.classList.remove('dark');
}

export function ThemeProvider({
  children,
}: ThemeProviderProps) {
  // Always ensure light mode on mount
  useEffect(() => {
    ensureLightMode();
  }, []);

  // Dark mode disabled - always return light theme
  const value: ThemeContextType = {
    theme: 'light',
    resolvedTheme: 'light',
    isDark: false,
    setTheme: () => {}, // no-op
    toggleTheme: () => {}, // no-op
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
