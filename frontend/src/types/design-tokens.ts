/**
 * Design Token Type Definitions
 *
 * TypeScript types for the design token system.
 * These types ensure type-safety when working with design tokens in code.
 */

// ============================================
// Color Types
// ============================================

export type PrimitiveColorScale = 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900;

export interface SemanticColorSet {
  DEFAULT: string;
  hover: string;
  active?: string;
  light: string;
  contrast: string;
}

export interface NeutralColorScale {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
}

export interface DesignColors {
  primary: SemanticColorSet;
  secondary: SemanticColorSet;
  success: Omit<SemanticColorSet, 'active'>;
  warning: Omit<SemanticColorSet, 'active'>;
  error: SemanticColorSet;
  info: Omit<SemanticColorSet, 'active'>;
  neutral: NeutralColorScale;
}

// ============================================
// Typography Types
// ============================================

export type FontSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl';
export type FontWeight = 'normal' | 'medium' | 'semibold' | 'bold';
export type LineHeight = 'tight' | 'normal' | 'relaxed';

export interface TypographyTokens {
  fontSize: Record<FontSize, string>;
  fontWeight: Record<FontWeight, number>;
  lineHeight: Record<LineHeight, number>;
}

// ============================================
// Spacing Types
// ============================================

export type SpacingScale = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20;

export type SpacingTokens = Record<SpacingScale, string>;

// ============================================
// Border Radius Types
// ============================================

export type BorderRadiusScale = 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';

export type BorderRadiusTokens = Record<BorderRadiusScale, string>;

// ============================================
// Shadow Types
// ============================================

export type ShadowScale = 'sm' | 'md' | 'lg' | 'xl';

export type ShadowTokens = Record<ShadowScale, string>;

// ============================================
// Z-Index Types
// ============================================

export type ZIndexScale = 'dropdown' | 'sticky' | 'modal' | 'tooltip' | 'toast';

export type ZIndexTokens = Record<ZIndexScale, number>;

// ============================================
// Transition Types
// ============================================

export type TransitionSpeed = 'fast' | 'normal' | 'slow';

export type TransitionTokens = Record<TransitionSpeed, string>;

// ============================================
// Component State Types
// ============================================

export type ComponentState =
  | 'default'
  | 'hover'
  | 'active'
  | 'focus'
  | 'disabled'
  | 'loading'
  | 'error';

export type DataDisplayState =
  | 'loading'
  | 'empty'
  | 'error'
  | 'success';

// ============================================
// Theme Types
// ============================================

export type ThemeName = 'light' | 'dark' | 'system';

export interface ThemeConfig {
  name: ThemeName;
  isDark: boolean;
}

// ============================================
// Viewport/Breakpoint Types
// ============================================

export type Breakpoint = 'sm' | 'md' | 'lg' | 'xl' | '2xl';

export interface BreakpointConfig {
  sm: string;   // 640px
  md: string;   // 768px
  lg: string;   // 1024px
  xl: string;   // 1280px
  '2xl': string; // 1536px
}

// ============================================
// Touch Target Types
// ============================================

export interface TouchTargetConfig {
  minWidth: string;
  minHeight: string;
}

export const TOUCH_TARGET_MOBILE: TouchTargetConfig = {
  minWidth: '44px',
  minHeight: '44px',
};

export const TOUCH_TARGET_DESKTOP: TouchTargetConfig = {
  minWidth: '36px',
  minHeight: '36px',
};

// ============================================
// Legacy Alias Mapping (for migration)
// ============================================

/**
 * Maps legacy color names to new semantic tokens.
 * Use this for gradual migration of components.
 *
 * @deprecated These aliases will be removed after all components are migrated.
 */
export const LEGACY_COLOR_ALIASES = {
  'accent': 'primary',
  'accent-dark': 'primary-hover',
  'semantic-error': 'error',
  'deep-trust-blue': 'secondary',
  'calm-grey': 'neutral-50',
  'success-green': 'success',
} as const;

export type LegacyColorAlias = keyof typeof LEGACY_COLOR_ALIASES;

// ============================================
// CSS Variable Helpers
// ============================================

/**
 * Get a CSS variable value with fallback
 */
export function getCSSVariable(name: string, fallback?: string): string {
  if (typeof window === 'undefined') {
    return fallback || '';
  }

  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(`--${name}`)
    .trim();

  return value || fallback || '';
}

/**
 * Set a CSS variable value
 */
export function setCSSVariable(name: string, value: string): void {
  if (typeof window === 'undefined') return;

  document.documentElement.style.setProperty(`--${name}`, value);
}
