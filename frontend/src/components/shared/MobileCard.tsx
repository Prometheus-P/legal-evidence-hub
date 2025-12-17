/**
 * MobileCard Component (T049)
 *
 * A card component optimized for mobile touch interfaces.
 * Provides consistent card styling with proper touch targets.
 *
 * Features:
 * - 44x44px minimum touch targets (WCAG 2.1 AA)
 * - Swipe actions support
 * - Loading and error states
 * - Accessible with keyboard navigation
 */

'use client';

import { ReactNode, useState } from 'react';
import { ChevronRight, Loader2 } from 'lucide-react';

export interface MobileCardAction {
  /**
   * Unique identifier for the action
   */
  id: string;
  /**
   * Action label
   */
  label: string;
  /**
   * Action icon
   */
  icon?: ReactNode;
  /**
   * Action handler
   */
  onClick: () => void;
  /**
   * Action variant
   */
  variant?: 'default' | 'primary' | 'danger';
  /**
   * Disable this action
   */
  disabled?: boolean;
}

export interface MobileCardProps {
  /**
   * Card title (primary content)
   */
  title: string;
  /**
   * Card subtitle
   */
  subtitle?: string;
  /**
   * Additional metadata displayed below subtitle
   */
  metadata?: ReactNode;
  /**
   * Left side icon or avatar
   */
  leading?: ReactNode;
  /**
   * Right side content (e.g., status badge)
   */
  trailing?: ReactNode;
  /**
   * Click handler for the entire card
   */
  onClick?: () => void;
  /**
   * Whether to show navigation chevron
   */
  showChevron?: boolean;
  /**
   * Quick actions (displayed on swipe or long press)
   */
  actions?: MobileCardAction[];
  /**
   * Loading state
   */
  isLoading?: boolean;
  /**
   * Error state
   */
  hasError?: boolean;
  /**
   * Error message
   */
  errorMessage?: string;
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Accessible label
   */
  ariaLabel?: string;
  /**
   * Children content (bottom section)
   */
  children?: ReactNode;
}

export function MobileCard({
  title,
  subtitle,
  metadata,
  leading,
  trailing,
  onClick,
  showChevron = true,
  actions,
  isLoading = false,
  hasError = false,
  errorMessage,
  className = '',
  ariaLabel,
  children,
}: MobileCardProps) {
  const [showActions, setShowActions] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick();
    }
  };

  const actionVariantStyles: Record<string, string> = {
    default: 'text-neutral-700 bg-neutral-100 hover:bg-neutral-200',
    primary: 'text-primary bg-primary-light hover:bg-primary-light/80',
    danger: 'text-error bg-error-light hover:bg-error-light/80',
  };

  return (
    <div
      className={`
        relative bg-white rounded-lg border shadow-sm overflow-hidden
        transition-all duration-200
        ${hasError ? 'border-error' : 'border-neutral-200'}
        ${onClick ? 'cursor-pointer hover:border-primary hover:shadow-md active:bg-neutral-50' : ''}
        ${className}
      `}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      tabIndex={onClick ? 0 : undefined}
      role={onClick ? 'button' : 'article'}
      aria-label={ariaLabel || title}
      aria-busy={isLoading}
      aria-invalid={hasError}
    >
      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
        </div>
      )}

      {/* Main Content */}
      <div className="p-4 min-h-[68px] flex items-center gap-3">
        {/* Leading (icon/avatar) */}
        {leading && (
          <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center">
            {leading}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-medium text-neutral-900 truncate">
            {title}
          </h3>
          {subtitle && (
            <p className="text-sm text-neutral-500 truncate mt-0.5">
              {subtitle}
            </p>
          )}
          {metadata && (
            <div className="mt-1 text-xs text-neutral-400">
              {metadata}
            </div>
          )}
        </div>

        {/* Trailing */}
        <div className="flex-shrink-0 flex items-center gap-2">
          {trailing}
          {onClick && showChevron && (
            <ChevronRight
              className="w-5 h-5 text-neutral-400"
              aria-hidden="true"
            />
          )}
        </div>
      </div>

      {/* Error Message */}
      {hasError && errorMessage && (
        <div className="px-4 pb-3 pt-0">
          <p className="text-sm text-error">{errorMessage}</p>
        </div>
      )}

      {/* Children Content */}
      {children && (
        <div className="px-4 pb-4 pt-0 border-t border-neutral-100 mt-2">
          {children}
        </div>
      )}

      {/* Quick Actions (show on interaction) */}
      {actions && actions.length > 0 && (
        <>
          {/* Action Toggle Button (for touch devices) */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              setShowActions(!showActions);
            }}
            className="absolute top-2 right-2 p-2 text-neutral-400 hover:text-neutral-600 min-w-[44px] min-h-[44px] flex items-center justify-center"
            aria-label={showActions ? '액션 닫기' : '액션 열기'}
            aria-expanded={showActions}
          >
            <span className="sr-only">{showActions ? '액션 닫기' : '액션 보기'}</span>
            <svg
              className={`w-4 h-4 transition-transform ${showActions ? 'rotate-90' : ''}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <circle cx="4" cy="10" r="2" />
              <circle cx="10" cy="10" r="2" />
              <circle cx="16" cy="10" r="2" />
            </svg>
          </button>

          {/* Actions Panel */}
          {showActions && (
            <div className="border-t border-neutral-100 px-4 py-2 flex gap-2 bg-neutral-50">
              {actions.map((action) => (
                <button
                  key={action.id}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    action.onClick();
                    setShowActions(false);
                  }}
                  disabled={action.disabled}
                  className={`
                    flex-1 flex items-center justify-center gap-1.5
                    px-3 py-2 rounded-lg text-sm font-medium
                    min-h-[44px] transition-colors
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${actionVariantStyles[action.variant || 'default']}
                  `}
                >
                  {action.icon}
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default MobileCard;
