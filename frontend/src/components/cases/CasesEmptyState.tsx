/**
 * CasesEmptyState Component (T073)
 *
 * Empty state for cases list when no cases exist.
 * Provides helpful guidance for first-time users.
 */

'use client';

import { FolderOpen, Plus, HelpCircle } from 'lucide-react';
import { EmptyState } from '@/components/shared/EmptyState';

interface CasesEmptyStateProps {
  /**
   * Handler for creating a new case
   */
  onCreateCase?: () => void;
  /**
   * Handler for viewing help/guide
   */
  onViewGuide?: () => void;
  /**
   * Whether user is a new user (shows onboarding message)
   */
  isNewUser?: boolean;
  /**
   * Size variant
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional classes
   */
  className?: string;
}

export function CasesEmptyState({
  onCreateCase,
  onViewGuide,
  isNewUser = false,
  size = 'md',
  className = '',
}: CasesEmptyStateProps) {
  const title = isNewUser
    ? '환영합니다! 첫 번째 사건을 시작해보세요'
    : '등록된 사건이 없습니다';

  const description = isNewUser
    ? '사건을 추가하고 증거를 관리하세요. AI가 분석을 도와드립니다.'
    : '새 사건을 추가하여 증거 관리를 시작하세요.';

  return (
    <EmptyState
      icon="custom"
      customIcon={
        <FolderOpen
          className="w-full h-full text-neutral-400 dark:text-neutral-500"
          aria-hidden="true"
        />
      }
      title={title}
      description={description}
      size={size}
      className={className}
      primaryAction={
        onCreateCase
          ? {
              label: '새 사건 추가',
              onClick: onCreateCase,
              variant: 'primary',
              icon: <Plus className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
      secondaryAction={
        onViewGuide
          ? {
              label: '사용 가이드',
              onClick: onViewGuide,
              variant: 'ghost',
              icon: <HelpCircle className="w-4 h-4 mr-2" />,
            }
          : undefined
      }
    />
  );
}

export default CasesEmptyState;
