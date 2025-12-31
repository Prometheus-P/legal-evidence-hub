'use client';

/**
 * PageWrapper Component
 * WCAG 2.2 Accessibility - Semantic HTML Wrapper
 *
 * Provides consistent semantic structure for portal pages with:
 * - <article> as main content container
 * - Proper heading hierarchy (h1 for title, h2 for sections)
 * - Accessible page header with optional description
 * - Content sections with aria-labelledby support
 *
 * Usage:
 * ```tsx
 * <PageWrapper
 *   title="대시보드"
 *   description="케이스 현황을 한눈에 확인하세요"
 * >
 *   <PageWrapper.Section title="통계">
 *     <StatCards />
 *   </PageWrapper.Section>
 *   <PageWrapper.Section title="최근 케이스">
 *     <CaseList />
 *   </PageWrapper.Section>
 * </PageWrapper>
 * ```
 */

import { useId, ReactNode, createContext, useContext } from 'react';

interface PageWrapperContextValue {
  headingLevel: number;
}

const PageWrapperContext = createContext<PageWrapperContextValue>({ headingLevel: 2 });

interface PageWrapperProps {
  /** Page title (rendered as h1) */
  title: string;
  /** Optional description below title */
  description?: string;
  /** Actions to render in the header (e.g., buttons) */
  actions?: ReactNode;
  /** Page content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

interface SectionProps {
  /** Section title (rendered as h2 by default) */
  title?: string;
  /** Section content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
  /** Override heading level (2-6) */
  headingLevel?: 2 | 3 | 4 | 5 | 6;
}

function Section({
  title,
  children,
  className = '',
  headingLevel: overrideLevel,
}: SectionProps) {
  const id = useId();
  const context = useContext(PageWrapperContext);
  const level = overrideLevel ?? context.headingLevel;
  const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <section
      className={`mb-6 ${className}`}
      aria-labelledby={title ? id : undefined}
    >
      {title && (
        <HeadingTag
          id={id}
          className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4"
        >
          {title}
        </HeadingTag>
      )}
      {children}
    </section>
  );
}

export function PageWrapper({
  title,
  description,
  actions,
  children,
  className = '',
}: PageWrapperProps) {
  const titleId = useId();

  return (
    <article
      className={`max-w-full ${className}`}
      aria-labelledby={titleId}
    >
      {/* Page Header */}
      <header className="mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1
              id={titleId}
              className="text-2xl font-bold text-gray-900 dark:text-gray-100"
            >
              {title}
            </h1>
            {description && (
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {description}
              </p>
            )}
          </div>
          {actions && (
            <div className="flex items-center gap-2 flex-shrink-0">
              {actions}
            </div>
          )}
        </div>
      </header>

      {/* Page Content */}
      <PageWrapperContext.Provider value={{ headingLevel: 2 }}>
        {children}
      </PageWrapperContext.Provider>
    </article>
  );
}

// Attach Section as a compound component
PageWrapper.Section = Section;

export default PageWrapper;
