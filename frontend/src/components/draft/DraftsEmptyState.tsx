/**
 * DraftsEmptyState Component (T075)
 *
 * Empty state for drafts section when no drafts exist.
 * Guides users to generate their first draft.
 */

'use client';

import { FileEdit, Sparkles, BookOpen } from 'lucide-react';
import { EmptyState } from '@/components/shared/EmptyState';

interface DraftsEmptyStateProps {
  /**
   * Handler for generating a new draft
   */
  onGenerateDraft?: () => void;
  /**
   * Handler for viewing draft templates
   */
  onViewTemplates?: () => void;
  /**
   * Whether evidence exists (affects messaging)
   */
  hasEvidence?: boolean;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional classes
   */
  className?: string;
}

export function DraftsEmptyState({
  onGenerateDraft,
  onViewTemplates,
  hasEvidence = false,
  size = 'md',
  className = '',
}: DraftsEmptyStateProps) {
  const title = '작성된 초안이 없습니다';

  const description = hasEvidence
    ? 'AI가 업로드된 증거를 분석하여 초안을 생성합니다. 초안 생성을 시작해보세요.'
    : '초안을 생성하려면 먼저 증거 자료를 업로드해주세요. AI가 증거를 분석하여 초안을 작성합니다.';

  return (
    <EmptyState
      icon="custom"
      customIcon={
        <FileEdit
          className="w-full h-full text-neutral-400 dark:text-neutral-500"
          aria-hidden="true"
        />
      }
      title={title}
      description={description}
      size={size}
      className={className}
      primaryAction={
        onGenerateDraft && hasEvidence
          ? {
              label: 'AI 초안 생성',
              onClick: onGenerateDraft,
              variant: 'primary',
              icon: <Sparkles className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
      secondaryAction={
        onViewTemplates
          ? {
              label: '템플릿 보기',
              onClick: onViewTemplates,
              variant: 'ghost',
              icon: <BookOpen className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
    >
      {/* Draft types hint */}
      <div className="flex flex-wrap justify-center gap-2 mt-2">
        {['소장', '답변서', '준비서면', '증거설명서'].map((type) => (
          <span
            key={type}
            className="px-2 py-1 text-xs bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 rounded-full"
          >
            {type}
          </span>
        ))}
      </div>
    </EmptyState>
  );
}

export default DraftsEmptyState;
