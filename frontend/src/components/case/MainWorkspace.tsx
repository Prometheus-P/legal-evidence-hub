'use client';

/**
 * MainWorkspace - Central Content Area
 * 014-ui-settings-completion Feature
 *
 * Main workspace containing:
 * - Fact summary (with editor)
 * - Issue analysis
 * - Draft generation section
 */

import { ReactNode } from 'react';
import { FileText, Scale, Sparkles, Loader2 } from 'lucide-react';

interface WorkspaceSectionProps {
  id: string;
  title: string;
  icon: ReactNode;
  description?: string;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

function WorkspaceSection({
  title,
  icon,
  description,
  children,
  actions,
  className = '',
}: WorkspaceSectionProps) {
  return (
    <section className={`bg-white dark:bg-neutral-800 rounded-lg border border-gray-200 dark:border-neutral-700 ${className}`}>
      {/* Section Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-neutral-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[var(--color-primary)]">{icon}</span>
            <div>
              <h3 className="font-semibold text-[var(--color-text-primary)]">{title}</h3>
              {description && (
                <p className="text-xs text-[var(--color-text-secondary)]">{description}</p>
              )}
            </div>
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      </div>
      {/* Section Content */}
      <div className="p-4">
        {children}
      </div>
    </section>
  );
}

interface MainWorkspaceProps {
  // Fact Summary
  factSummaryContent: ReactNode;
  // Issue Analysis (hidden by default as per Task 6)
  analysisContent?: ReactNode;
  showAnalysis?: boolean;
  // Draft Generation
  onGenerateDraft: () => void;
  hasDraft: boolean;
  isGeneratingDraft: boolean;
  draftContent?: ReactNode;
}

export function MainWorkspace({
  factSummaryContent,
  analysisContent,
  showAnalysis = false, // Hidden by default as per Task 6
  onGenerateDraft,
  hasDraft,
  isGeneratingDraft,
  draftContent,
}: MainWorkspaceProps) {
  return (
    <div className="space-y-6">
      {/* Fact Summary Section */}
      <WorkspaceSection
        id="fact-summary"
        title="사실관계 요약"
        icon={<FileText className="w-5 h-5" />}
        description="증거 자료를 기반으로 정리된 사건 사실관계"
      >
        {factSummaryContent}
      </WorkspaceSection>

      {/* Issue Analysis Section - Hidden by default (Task 6) */}
      {showAnalysis && analysisContent && (
        <WorkspaceSection
          id="analysis"
          title="쟁점 분석"
          icon={<Scale className="w-5 h-5" />}
          description="핵심 쟁점 및 법률적 판단 근거"
        >
          {analysisContent}
        </WorkspaceSection>
      )}

      {/* Draft Generation Section */}
      <WorkspaceSection
        id="draft"
        title="초안 생성"
        icon={<Sparkles className="w-5 h-5" />}
        description="사실관계와 쟁점 분석을 기반으로 법률 문서 초안 생성"
        actions={
          !hasDraft && !isGeneratingDraft ? (
            <button
              onClick={onGenerateDraft}
              className="inline-flex items-center px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary-hover)] transition-colors"
            >
              <Sparkles className="w-4 h-4 mr-1" />
              초안 생성
            </button>
          ) : null
        }
      >
        {isGeneratingDraft ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 text-[var(--color-primary)] animate-spin mx-auto mb-3" />
            <p className="text-sm text-[var(--color-text-secondary)]">
              AI가 법률 초안을 작성하고 있습니다...
            </p>
          </div>
        ) : hasDraft && draftContent ? (
          draftContent
        ) : (
          <div className="text-center py-8 text-[var(--color-text-secondary)]">
            <p className="text-sm">
              사실관계 요약이 완료되면 초안을 생성할 수 있습니다.
            </p>
          </div>
        )}
      </WorkspaceSection>
    </div>
  );
}

export default MainWorkspace;
