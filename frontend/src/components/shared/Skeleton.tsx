/**
 * Skeleton Component (T059)
 *
 * Loading placeholder components for content that is being loaded.
 * Provides visual feedback during async operations.
 *
 * Features:
 * - Base Skeleton with customizable dimensions
 * - SkeletonText for multi-line text placeholders
 * - SkeletonCircle for avatar placeholders
 * - SkeletonCard for card-style placeholders
 * - Accessible with proper ARIA attributes
 */

'use client';

import { HTMLAttributes } from 'react';

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /**
   * Width of the skeleton
   */
  width?: string | number;
  /**
   * Height of the skeleton
   */
  height?: string | number;
  /**
   * Border radius variant
   */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  /**
   * Whether to animate the skeleton
   */
  animated?: boolean;
}

/**
 * Base Skeleton Component
 */
export function Skeleton({
  width,
  height,
  rounded = 'md',
  animated = true,
  className = '',
  style,
  ...props
}: SkeletonProps) {
  const roundedStyles: Record<string, string> = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded',
    lg: 'rounded-lg',
    full: 'rounded-full',
  };

  return (
    <div
      aria-hidden="true"
      className={`
        bg-neutral-200 dark:bg-neutral-700
        ${animated ? 'animate-pulse' : ''}
        ${roundedStyles[rounded]}
        ${className}
      `}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        ...style,
      }}
      {...props}
    />
  );
}

interface SkeletonTextProps {
  /**
   * Number of text lines to show
   */
  lines?: number;
  /**
   * Gap between lines
   */
  gap?: 'sm' | 'md' | 'lg';
  /**
   * Width of each line (can be array for different widths)
   */
  lineWidth?: string | string[];
  /**
   * Height of each line
   */
  lineHeight?: string | number;
  /**
   * Additional classes for the container
   */
  className?: string;
}

/**
 * Skeleton for multi-line text
 */
export function SkeletonText({
  lines = 3,
  gap = 'md',
  lineWidth,
  lineHeight = 16,
  className = '',
  ...props
}: SkeletonTextProps & HTMLAttributes<HTMLDivElement>) {
  const gapStyles: Record<string, string> = {
    sm: 'space-y-1',
    md: 'space-y-2',
    lg: 'space-y-3',
  };

  const getLineWidth = (index: number): string => {
    if (Array.isArray(lineWidth)) {
      return lineWidth[index] || lineWidth[lineWidth.length - 1] || '100%';
    }
    if (lineWidth) return lineWidth;
    // Last line is shorter by default
    return index === lines - 1 ? '66%' : '100%';
  };

  return (
    <div className={`${gapStyles[gap]} ${className}`} {...props}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          height={lineHeight}
          width={getLineWidth(index)}
          rounded="sm"
        />
      ))}
    </div>
  );
}

interface SkeletonCircleProps {
  /**
   * Size of the circle in pixels
   */
  size?: number;
  /**
   * Additional classes
   */
  className?: string;
}

/**
 * Skeleton for circular elements (avatars, icons)
 */
export function SkeletonCircle({
  size = 40,
  className = '',
  ...props
}: SkeletonCircleProps & HTMLAttributes<HTMLDivElement>) {
  return (
    <Skeleton
      width={size}
      height={size}
      rounded="full"
      className={className}
      {...props}
    />
  );
}

interface SkeletonCardProps {
  /**
   * Show header skeleton
   */
  showHeader?: boolean;
  /**
   * Show avatar in header
   */
  showAvatar?: boolean;
  /**
   * Number of content lines
   */
  contentLines?: number;
  /**
   * Show footer skeleton
   */
  showFooter?: boolean;
  /**
   * Additional classes
   */
  className?: string;
}

/**
 * Skeleton for card-style content
 */
export function SkeletonCard({
  showHeader = true,
  showAvatar = false,
  contentLines = 3,
  showFooter = false,
  className = '',
  ...props
}: SkeletonCardProps & HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4 ${className}`}
      {...props}
    >
      {/* Header */}
      {showHeader && (
        <div className="flex items-center gap-3 mb-4">
          {showAvatar && <SkeletonCircle size={40} />}
          <div className="flex-1">
            <Skeleton height={24} width="60%" className="mb-2 h-6" />
            <Skeleton height={16} width="40%" />
          </div>
        </div>
      )}

      {/* Content */}
      <SkeletonText lines={contentLines} className="mb-4" />

      {/* Footer */}
      {showFooter && (
        <div className="flex justify-between items-center pt-4 border-t border-neutral-100 dark:border-neutral-700">
          <Skeleton height={32} width={80} />
          <Skeleton height={32} width={80} />
        </div>
      )}
    </div>
  );
}

export default Skeleton;
