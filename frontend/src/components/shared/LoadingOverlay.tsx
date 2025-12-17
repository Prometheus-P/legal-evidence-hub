/**
 * LoadingOverlay Component (T062)
 *
 * Full-screen or container-based loading overlay.
 * Shows a spinner with optional message during async operations.
 *
 * Features:
 * - Full-screen or container-relative positioning
 * - Customizable spinner and message
 * - Accessible with proper ARIA attributes
 * - Semi-transparent backdrop
 */

'use client';

import { Spinner } from '@/components/primitives';
import { ReactNode } from 'react';

interface LoadingOverlayProps {
  /**
   * Whether the overlay is visible
   */
  isLoading: boolean;
  /**
   * Loading message to display
   */
  message?: string;
  /**
   * Additional message or hint
   */
  hint?: string;
  /**
   * Spinner size
   */
  spinnerSize?: 'sm' | 'md' | 'lg';
  /**
   * Whether to cover the full screen or just the parent container
   */
  fullScreen?: boolean;
  /**
   * Custom spinner component
   */
  customSpinner?: ReactNode;
  /**
   * Whether to show a blurred backdrop
   */
  blur?: boolean;
  /**
   * Z-index for the overlay
   */
  zIndex?: number;
  /**
   * Children to render underneath the overlay
   */
  children?: ReactNode;
  /**
   * Additional classes for the overlay
   */
  className?: string;
}

export function LoadingOverlay({
  isLoading,
  message = '로딩 중...',
  hint,
  spinnerSize = 'lg',
  fullScreen = false,
  customSpinner,
  blur = false,
  zIndex = 50,
  children,
  className = '',
}: LoadingOverlayProps) {
  if (!isLoading && !children) {
    return null;
  }

  const spinnerSizes: Record<string, string> = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const overlay = isLoading ? (
    <div
      role="status"
      aria-live="polite"
      aria-label={message}
      className={`
        ${fullScreen ? 'fixed inset-0' : 'absolute inset-0'}
        flex flex-col items-center justify-center
        bg-white/80 dark:bg-neutral-900/80
        ${blur ? 'backdrop-blur-sm' : ''}
        ${className}
      `}
      style={{ zIndex }}
    >
      {/* Spinner */}
      {customSpinner || (
        <Spinner
          size={spinnerSize}
          className={`${spinnerSizes[spinnerSize]} text-primary`}
        />
      )}

      {/* Message */}
      {message && (
        <p className="mt-4 text-base font-medium text-neutral-700 dark:text-neutral-300">
          {message}
        </p>
      )}

      {/* Hint */}
      {hint && (
        <p className="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
          {hint}
        </p>
      )}

      {/* Screen reader announcement */}
      <span className="sr-only">{message}</span>
    </div>
  ) : null;

  if (children) {
    return (
      <div className="relative">
        {children}
        {overlay}
      </div>
    );
  }

  return overlay;
}

/**
 * Page-level loading component
 * Use this in Next.js loading.tsx files
 */
export function PageLoading({
  message = '페이지 로딩 중...',
}: {
  message?: string;
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="min-h-[400px] flex flex-col items-center justify-center"
    >
      <Spinner size="lg" className="w-12 h-12 text-primary" />
      <p className="mt-4 text-base font-medium text-neutral-700 dark:text-neutral-300">
        {message}
      </p>
      <span className="sr-only">{message}</span>
    </div>
  );
}

/**
 * Button loading state helper
 * Use this to show loading state inside buttons
 */
export function ButtonLoading({
  text = '처리 중...',
  className = '',
}: {
  text?: string;
  className?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <Spinner size="sm" className="w-4 h-4" />
      <span>{text}</span>
    </span>
  );
}

export default LoadingOverlay;
