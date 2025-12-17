/**
 * ThemeToggle Component
 * 007-lawyer-portal-v1 Feature - US5 (Dark Mode)
 *
 * A button to toggle between light and dark themes.
 * Supports three modes: light, dark, and system.
 */

'use client';

import { useTheme, Theme } from '@/contexts/ThemeContext';

interface ThemeToggleProps {
  /** Show label text */
  showLabel?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// Icons
const SunIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
    />
  </svg>
);

const MoonIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
    />
  </svg>
);

const SystemIcon = ({ className = 'w-5 h-5' }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
    />
  </svg>
);

const sizeClasses = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
};

const iconSizes = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
};

/**
 * Simple toggle button (light/dark only)
 */
export function ThemeToggle({
  showLabel = false,
  className = '',
  size = 'md',
}: ThemeToggleProps) {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`
        inline-flex items-center justify-center rounded-lg
        ${sizeClasses[size]}
        ${showLabel ? 'gap-2 px-3' : ''}
        text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]
        bg-[var(--color-bg-secondary)] hover:bg-[var(--color-bg-tertiary)]
        transition-colors duration-200
        focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:ring-offset-2
        ${className}
      `}
      aria-label={isDark ? '라이트 모드로 전환' : '다크 모드로 전환'}
    >
      {isDark ? (
        <SunIcon className={iconSizes[size]} />
      ) : (
        <MoonIcon className={iconSizes[size]} />
      )}
      {showLabel && (
        <span className="text-sm font-medium">
          {isDark ? '라이트 모드' : '다크 모드'}
        </span>
      )}
    </button>
  );
}

/**
 * Advanced toggle with system option
 */
export function ThemeSelector({ className = '' }: { className?: string }) {
  const { theme, setTheme } = useTheme();

  const options: { value: Theme; label: string; icon: typeof SunIcon }[] = [
    { value: 'light', label: '라이트', icon: SunIcon },
    { value: 'dark', label: '다크', icon: MoonIcon },
    { value: 'system', label: '시스템', icon: SystemIcon },
  ];

  return (
    <div
      role="group"
      aria-label="테마 선택"
      className={`inline-flex rounded-lg bg-[var(--color-bg-secondary)] p-1 ${className}`}
    >
      {options.map(({ value, label, icon: Icon }) => (
        <button
          key={value}
          type="button"
          onClick={() => setTheme(value)}
          className={`
            inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium
            transition-colors duration-200
            ${
              theme === value
                ? 'bg-[var(--color-primary)] text-[var(--color-primary-contrast)] shadow-sm'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            }
          `}
          aria-pressed={theme === value}
        >
          <Icon className="w-4 h-4" />
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
}

export default ThemeToggle;
