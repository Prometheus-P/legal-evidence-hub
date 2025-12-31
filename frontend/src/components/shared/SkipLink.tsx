'use client';

/**
 * SkipLink Component
 * WCAG 2.2 Accessibility - Skip Navigation Link
 *
 * Provides keyboard users with a way to skip repetitive navigation
 * and jump directly to the main content.
 *
 * Features:
 * - Visually hidden until focused (sr-only → visible on focus)
 * - High contrast for visibility when focused
 * - Positioned at top-left of viewport when visible
 * - Supports custom target and label
 */

interface SkipLinkProps {
  /** Target element ID to skip to (without #) */
  targetId?: string;
  /** Label text for the skip link */
  label?: string;
  /** Additional CSS classes */
  className?: string;
}

export function SkipLink({
  targetId = 'main-content',
  label = '본문으로 건너뛰기',
  className = '',
}: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={`
        sr-only
        focus:not-sr-only
        focus:absolute
        focus:top-4
        focus:left-4
        focus:z-[100]
        focus:px-4
        focus:py-2
        focus:bg-[var(--color-primary)]
        focus:text-white
        focus:rounded-md
        focus:outline-none
        focus:ring-2
        focus:ring-[var(--color-primary)]
        focus:ring-offset-2
        focus:shadow-lg
        focus:font-medium
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {label}
    </a>
  );
}

export default SkipLink;
