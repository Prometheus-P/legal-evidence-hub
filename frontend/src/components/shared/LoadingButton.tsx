/**
 * LoadingButton Component
 * 009-mvp-gap-closure Feature - T034
 *
 * Button with loading state indicator.
 * Shows spinner and disables interaction during API calls.
 * Implements FR-010 (버튼 로딩 상태)
 */

'use client';

import React, { forwardRef, ButtonHTMLAttributes } from 'react';

export interface LoadingButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Whether the button is in loading state */
  isLoading?: boolean;
  /** Text to show during loading (optional, shows spinner only if not provided) */
  loadingText?: string;
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  /** Button size */
  size?: 'sm' | 'md' | 'lg';
  /** Full width button */
  fullWidth?: boolean;
}

/**
 * Spinner component for loading state
 */
const Spinner: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg
    className={`animate-spin ${className}`}
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    />
  </svg>
);

/**
 * Get variant-specific classes
 */
const getVariantClasses = (variant: LoadingButtonProps['variant'], isLoading: boolean): string => {
  const baseClasses = 'transition-colors duration-200 font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: `${baseClasses} bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 disabled:bg-blue-400`,
    secondary: `${baseClasses} bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 disabled:bg-gray-100 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600`,
    danger: `${baseClasses} bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:bg-red-400`,
    ghost: `${baseClasses} bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800`,
  };

  return variants[variant || 'primary'];
};

/**
 * Get size-specific classes
 */
const getSizeClasses = (size: LoadingButtonProps['size']): string => {
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return sizes[size || 'md'];
};

/**
 * Get spinner size based on button size
 */
const getSpinnerSize = (size: LoadingButtonProps['size']): string => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return sizes[size || 'md'];
};

/**
 * LoadingButton component with loading state indicator
 *
 * @example
 * ```tsx
 * // Basic usage
 * <LoadingButton isLoading={isSubmitting} onClick={handleSubmit}>
 *   저장
 * </LoadingButton>
 *
 * // With loading text
 * <LoadingButton
 *   isLoading={isSubmitting}
 *   loadingText="저장 중..."
 *   onClick={handleSubmit}
 * >
 *   저장
 * </LoadingButton>
 *
 * // Different variants
 * <LoadingButton variant="danger" isLoading={isDeleting}>
 *   삭제
 * </LoadingButton>
 * ```
 */
export const LoadingButton = forwardRef<HTMLButtonElement, LoadingButtonProps>(
  (
    {
      children,
      isLoading = false,
      loadingText,
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      disabled,
      className = '',
      ...props
    },
    ref
  ) => {
    const variantClasses = getVariantClasses(variant, isLoading);
    const sizeClasses = getSizeClasses(size);
    const spinnerSize = getSpinnerSize(size);

    const buttonClasses = [
      variantClasses,
      sizeClasses,
      fullWidth ? 'w-full' : '',
      'inline-flex items-center justify-center gap-2',
      isLoading ? 'cursor-not-allowed' : '',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={buttonClasses}
        aria-busy={isLoading}
        aria-disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Spinner className={spinnerSize} />}
        <span className={isLoading && !loadingText ? 'sr-only' : ''}>
          {isLoading && loadingText ? loadingText : children}
        </span>
      </button>
    );
  }
);

LoadingButton.displayName = 'LoadingButton';

export default LoadingButton;
