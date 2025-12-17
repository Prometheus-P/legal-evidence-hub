/**
 * EmptyState Component (T071)
 *
 * Displays helpful guidance when no data exists.
 * Provides actionable next steps for users.
 *
 * Features:
 * - Customizable icon, title, and description
 * - Primary and secondary action buttons
 * - Accessible with proper semantics
 * - Multiple size variants
 */

'use client';

import { ReactNode } from 'react';
import { Inbox, FileText, FolderOpen, Search, Plus } from 'lucide-react';
import { Button } from '@/components/primitives';

interface EmptyStateAction {
  /**
   * Button label
   */
  label: string;
  /**
   * Click handler
   */
  onClick: () => void;
  /**
   * Button variant
   */
  variant?: 'primary' | 'secondary' | 'ghost';
  /**
   * Button icon
   */
  icon?: ReactNode;
}

interface EmptyStateProps {
  /**
   * Icon to display (use preset or custom)
   */
  icon?: 'inbox' | 'file' | 'folder' | 'search' | 'custom';
  /**
   * Custom icon component
   */
  customIcon?: ReactNode;
  /**
   * Title text
   */
  title: string;
  /**
   * Description text
   */
  description?: string;
  /**
   * Primary action button
   */
  primaryAction?: EmptyStateAction;
  /**
   * Secondary action button
   */
  secondaryAction?: EmptyStateAction;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional classes
   */
  className?: string;
  /**
   * Children for custom content
   */
  children?: ReactNode;
}

const iconComponents: Record<string, typeof Inbox> = {
  inbox: Inbox,
  file: FileText,
  folder: FolderOpen,
  search: Search,
};

export function EmptyState({
  icon = 'inbox',
  customIcon,
  title,
  description,
  primaryAction,
  secondaryAction,
  size = 'md',
  className = '',
  children,
}: EmptyStateProps) {
  const sizeStyles: Record<string, { container: string; icon: string; title: string; description: string }> = {
    sm: {
      container: 'py-8 px-4',
      icon: 'w-10 h-10',
      title: 'text-base',
      description: 'text-sm',
    },
    md: {
      container: 'py-12 px-6',
      icon: 'w-14 h-14',
      title: 'text-lg',
      description: 'text-base',
    },
    lg: {
      container: 'py-16 px-8',
      icon: 'w-20 h-20',
      title: 'text-xl',
      description: 'text-base',
    },
  };

  const styles = sizeStyles[size];
  const IconComponent = icon !== 'custom' ? iconComponents[icon] : null;

  return (
    <div
      role="status"
      aria-label={title}
      className={`
        flex flex-col items-center justify-center text-center
        ${styles.container}
        ${className}
      `}
    >
      {/* Icon */}
      <div className="mb-4 p-4 bg-neutral-100 dark:bg-neutral-800 rounded-full">
        {customIcon || (IconComponent && (
          <IconComponent
            className={`${styles.icon} text-neutral-400 dark:text-neutral-500`}
            aria-hidden="true"
          />
        ))}
      </div>

      {/* Title */}
      <h3 className={`${styles.title} font-semibold text-neutral-900 dark:text-neutral-100 mb-2`}>
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className={`${styles.description} text-neutral-500 dark:text-neutral-400 max-w-md mb-6`}>
          {description}
        </p>
      )}

      {/* Custom Children */}
      {children && <div className="mb-6">{children}</div>}

      {/* Actions */}
      {(primaryAction || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-3">
          {primaryAction && (
            <Button
              variant={primaryAction.variant || 'primary'}
              onClick={primaryAction.onClick}
            >
              {primaryAction.icon || <Plus className="w-4 h-4 mr-2" />}
              {primaryAction.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant={secondaryAction.variant || 'ghost'}
              onClick={secondaryAction.onClick}
            >
              {secondaryAction.icon}
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * ErrorState Component (T072)
 *
 * Displays error message with retry option.
 */
interface ErrorStateProps {
  /**
   * Error title
   */
  title?: string;
  /**
   * Error message
   */
  message?: string;
  /**
   * Retry action
   */
  onRetry?: () => void;
  /**
   * Retry button text
   */
  retryText?: string;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional classes
   */
  className?: string;
}

export function ErrorState({
  title = '오류가 발생했습니다',
  message = '데이터를 불러오는 중 문제가 발생했습니다.',
  onRetry,
  retryText = '다시 시도',
  size = 'md',
  className = '',
}: ErrorStateProps) {
  const sizeStyles: Record<string, { container: string; icon: string; title: string }> = {
    sm: { container: 'py-6 px-4', icon: 'w-8 h-8', title: 'text-base' },
    md: { container: 'py-10 px-6', icon: 'w-12 h-12', title: 'text-lg' },
    lg: { container: 'py-14 px-8', icon: 'w-16 h-16', title: 'text-xl' },
  };

  const styles = sizeStyles[size];

  return (
    <div
      role="alert"
      className={`
        flex flex-col items-center justify-center text-center
        ${styles.container}
        ${className}
      `}
    >
      {/* Error Icon */}
      <div className="mb-4 p-3 bg-error-light rounded-full">
        <svg
          className={`${styles.icon} text-error`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>

      {/* Title */}
      <h3 className={`${styles.title} font-semibold text-error mb-2`}>
        {title}
      </h3>

      {/* Message */}
      <p className="text-sm text-neutral-500 dark:text-neutral-400 max-w-md mb-4">
        {message}
      </p>

      {/* Retry Button */}
      {onRetry && (
        <Button variant="secondary" onClick={onRetry}>
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          {retryText}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
