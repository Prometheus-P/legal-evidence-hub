# Data Model: UI Upgrade

**Feature**: 013-ui-upgrade | **Date**: 2025-12-17

> Note: This UI upgrade feature doesn't involve traditional database entities. This document defines the **Design Token System** structure which serves as the data model for visual consistency.

## Design Token Structure

### 1. Color Tokens

#### Primitive Colors (Raw Values)

```typescript
// types/design-tokens.ts
interface PrimitiveColors {
  // Blue scale
  blue50: string;   // #eff6ff
  blue100: string;  // #dbeafe
  blue500: string;  // #3b82f6
  blue600: string;  // #2563eb
  blue700: string;  // #1d4ed8

  // Neutral scale
  neutral50: string;   // #fafafa
  neutral100: string;  // #f5f5f5
  neutral200: string;  // #e5e5e5
  neutral300: string;  // #d4d4d4
  neutral400: string;  // #a3a3a3
  neutral500: string;  // #737373
  neutral600: string;  // #525252
  neutral700: string;  // #404040
  neutral800: string;  // #262626
  neutral900: string;  // #171717

  // Semantic colors (raw)
  red500: string;    // #ef4444 (error)
  green500: string;  // #22c55e (success)
  amber500: string;  // #f59e0b (warning)
  sky500: string;    // #0ea5e9 (info)
}
```

#### Semantic Colors (Purpose-Based)

```typescript
interface SemanticColors {
  // Primary (brand action color)
  primary: string;
  primaryHover: string;
  primaryActive: string;
  primaryLight: string;
  primaryContrast: string;

  // Secondary (supporting actions)
  secondary: string;
  secondaryHover: string;
  secondaryActive: string;
  secondaryContrast: string;

  // Status colors
  success: string;
  successHover: string;
  successLight: string;
  successContrast: string;

  warning: string;
  warningHover: string;
  warningLight: string;
  warningContrast: string;

  error: string;
  errorHover: string;
  errorActive: string;
  errorLight: string;
  errorContrast: string;

  info: string;
  infoHover: string;
  infoLight: string;
  infoContrast: string;

  // Text hierarchy
  textPrimary: string;
  textSecondary: string;
  textTertiary: string;
  textDisabled: string;
  textInverse: string;

  // Surface colors
  surfaceDefault: string;
  surfaceElevated: string;
  surfaceOverlay: string;

  // Border colors
  borderDefault: string;
  borderStrong: string;
  borderFocus: string;
}
```

### 2. Typography Tokens

```typescript
interface TypographyTokens {
  // Font families
  fontFamily: {
    sans: string;  // Pretendard, system fonts
    mono: string;  // Monospace for code
  };

  // Font sizes (with line heights)
  fontSize: {
    xs: { size: string; lineHeight: string };   // 12px / 16px
    sm: { size: string; lineHeight: string };   // 14px / 20px
    base: { size: string; lineHeight: string }; // 16px / 24px
    lg: { size: string; lineHeight: string };   // 18px / 28px
    xl: { size: string; lineHeight: string };   // 20px / 28px
    '2xl': { size: string; lineHeight: string }; // 24px / 32px
    '3xl': { size: string; lineHeight: string }; // 30px / 36px
    '4xl': { size: string; lineHeight: string }; // 36px / 40px
  };

  // Font weights
  fontWeight: {
    normal: number;   // 400
    medium: number;   // 500
    semibold: number; // 600
    bold: number;     // 700
  };
}
```

### 3. Spacing Tokens

```typescript
interface SpacingTokens {
  // Base unit: 4px
  0: string;    // 0px
  1: string;    // 4px
  2: string;    // 8px
  3: string;    // 12px
  4: string;    // 16px
  5: string;    // 20px
  6: string;    // 24px
  8: string;    // 32px
  10: string;   // 40px
  12: string;   // 48px
  16: string;   // 64px
  20: string;   // 80px
}
```

### 4. Border Radius Tokens

```typescript
interface BorderRadiusTokens {
  none: string;  // 0
  sm: string;    // 4px
  md: string;    // 6px
  lg: string;    // 8px
  xl: string;    // 12px
  '2xl': string; // 16px
  full: string;  // 9999px (circular)
}
```

### 5. Shadow Tokens

```typescript
interface ShadowTokens {
  none: string;
  sm: string;    // Subtle elevation
  md: string;    // Card elevation
  lg: string;    // Modal/dropdown elevation
  xl: string;    // High elevation
}
```

### 6. Animation Tokens

```typescript
interface AnimationTokens {
  // Durations
  duration: {
    fast: string;    // 150ms
    normal: string;  // 200ms
    slow: string;    // 300ms
  };

  // Easing functions
  easing: {
    default: string;    // ease
    in: string;         // ease-in
    out: string;        // ease-out
    inOut: string;      // ease-in-out
  };
}
```

### 7. Z-Index Tokens

```typescript
interface ZIndexTokens {
  dropdown: number;  // 50
  sticky: number;    // 100
  modal: number;     // 200
  tooltip: number;   // 300
  toast: number;     // 400
}
```

## Component State Model

### Interactive Component States

```typescript
type ComponentState =
  | 'default'
  | 'hover'
  | 'active'
  | 'focus'
  | 'disabled'
  | 'loading'
  | 'error';

interface InteractiveStateStyles {
  default: {
    background: string;
    border: string;
    text: string;
  };
  hover: {
    background: string;
    border: string;
    text: string;
  };
  active: {
    background: string;
    border: string;
    text: string;
  };
  focus: {
    outline: string;
    outlineOffset: string;
  };
  disabled: {
    opacity: number;
    cursor: string;
  };
  loading: {
    opacity: number;
    cursor: string;
  };
  error: {
    border: string;
    text: string;
  };
}
```

### Data Display States

```typescript
type DataState =
  | 'loading'
  | 'empty'
  | 'error'
  | 'success';

interface DataStateProps {
  loading: {
    skeleton: boolean;
    spinner: boolean;
    message?: string;
  };
  empty: {
    icon: string;
    title: string;
    description: string;
    action?: {
      label: string;
      onClick: () => void;
    };
  };
  error: {
    icon: string;
    title: string;
    description: string;
    retry?: () => void;
  };
  success: {
    data: unknown;
  };
}
```

## Viewport Breakpoints

```typescript
interface Breakpoints {
  sm: string;  // 640px  - Mobile landscape
  md: string;  // 768px  - Tablet portrait
  lg: string;  // 1024px - Tablet landscape / small desktop
  xl: string;  // 1280px - Desktop
  '2xl': string; // 1536px - Large desktop
}

// Touch target requirements by breakpoint
interface TouchTargets {
  mobile: {
    minWidth: string;   // 44px
    minHeight: string;  // 44px
  };
  desktop: {
    minWidth: string;   // 36px (can be smaller with mouse)
    minHeight: string;  // 36px
  };
}
```

## Theme Configuration

```typescript
interface ThemeConfig {
  name: 'light' | 'dark';
  colors: SemanticColors;
  isDark: boolean;
}

// CSS variable mapping for theme switching
const lightTheme: ThemeConfig = {
  name: 'light',
  colors: {
    primary: 'var(--color-blue-500)',
    textPrimary: 'var(--color-neutral-900)',
    surfaceDefault: 'var(--color-neutral-50)',
    // ... rest of semantic colors
  },
  isDark: false,
};

const darkTheme: ThemeConfig = {
  name: 'dark',
  colors: {
    primary: 'var(--color-blue-400)',
    textPrimary: 'var(--color-neutral-50)',
    surfaceDefault: 'var(--color-neutral-900)',
    // ... rest of semantic colors
  },
  isDark: true,
};
```

## Legacy Alias Mapping (For Migration)

```typescript
// Map legacy color names to new semantic tokens
const legacyAliases = {
  'accent': 'primary',
  'accent-dark': 'primaryHover',
  'semantic-error': 'error',
  'deep-trust-blue': 'secondary',
  'calm-grey': 'neutral50',
  'success-green': 'success',
};

// Migration script will search for these and replace with semantic names
```
