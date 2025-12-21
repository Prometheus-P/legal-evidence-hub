'use client';

/**
 * AnalysisTab Component
 * Contains LSSP (Legal Strategy) panel with expandable card layout.
 *
 * Lazy loads heavy panel components for better initial page load performance.
 *
 * Phase B.3: Added compact AI analysis status bar.
 */

import { Suspense, lazy } from 'react';
import { Sparkles, Loader2, RefreshCw } from 'lucide-react';

// Lazy load heavy panels for performance
const LSSPPanel = lazy(() =>
  import('@/components/lssp/LSSPPanel').then(mod => ({ default: mod.LSSPPanel }))
);

interface AnalysisTabProps {
  /** Case ID for data fetching */
  caseId: string;
  /** Number of evidence items in this case */
  evidenceCount: number;
  /** Callback when draft generation is requested */
  onDraftGenerate: (templateId?: string) => void;
  /** Last AI analysis timestamp (ISO 8601) */
  lastAnalyzedAt?: string;
  /** Handler for requesting AI analysis */
  onRequestAnalysis?: () => Promise<void>;
  /** Whether AI analysis is currently in progress */
  isAnalyzing?: boolean;
}

/**
 * Format relative time for last analysis timestamp
 */
function formatRelativeTime(isoDate: string): string {
  const now = new Date();
  const date = new Date(isoDate);
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) return '방금 전';
  if (diffMinutes < 60) return `${diffMinutes}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;

  return date.toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * AI Analysis Status Bar Component (Compact inline version)
 */
function AIAnalysisStatusBar({
  lastAnalyzedAt,
  onRequestAnalysis,
  isAnalyzing,
}: {
  lastAnalyzedAt?: string;
  onRequestAnalysis?: () => Promise<void>;
  isAnalyzing?: boolean;
}) {
  const handleClick = async () => {
    if (onRequestAnalysis && !isAnalyzing) {
      await onRequestAnalysis();
    }
  };

  return (
    <div className="flex items-center justify-between py-2 px-3 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg border border-neutral-200 dark:border-neutral-700">
      <div className="flex items-center gap-2 text-sm">
        <Sparkles className="w-4 h-4 text-indigo-500" />
        <span className="text-neutral-600 dark:text-neutral-400">
          {lastAnalyzedAt ? (
            <>분석 완료 · {formatRelativeTime(lastAnalyzedAt)}</>
          ) : (
            <>분석 대기 중</>
          )}
        </span>
      </div>
      <button
        type="button"
        onClick={handleClick}
        disabled={isAnalyzing}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
          isAnalyzing
            ? 'bg-neutral-200 dark:bg-neutral-700 text-neutral-400 dark:text-neutral-500 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
        }`}
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="w-3 h-3 animate-spin" />
            분석 중
          </>
        ) : (
          <>
            <RefreshCw className="w-3 h-3" />
            재분석
          </>
        )}
      </button>
    </div>
  );
}

/**
 * Skeleton loader for lazy-loaded panels
 */
function PanelSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-6 bg-gray-200 dark:bg-neutral-700 rounded w-1/3" />
      <div className="h-4 bg-gray-200 dark:bg-neutral-700 rounded w-2/3" />
      <div className="space-y-3">
        <div className="h-24 bg-gray-200 dark:bg-neutral-700 rounded" />
        <div className="h-24 bg-gray-200 dark:bg-neutral-700 rounded" />
      </div>
    </div>
  );
}

/**
 * Analysis Tab - Contains LSSP (Legal Strategy) panel
 *
 * Features:
 * - Lazy loading of heavy panels for better initial load
 * - Sub-tab navigation flattened (Precedent integrated into LSSP)
 * - Skeleton loading states
 * - Draft generation callback integration
 * - AI analysis status bar with last analyzed timestamp (Phase B.3)
 */
export function AnalysisTab({
  caseId,
  evidenceCount,
  onDraftGenerate,
  lastAnalyzedAt,
  onRequestAnalysis,
  isAnalyzing = false,
}: AnalysisTabProps) {
  return (
    <div className="space-y-6">
      {/* AI Analysis Status Bar (Phase B.3) */}
      {onRequestAnalysis && (
        <AIAnalysisStatusBar
          lastAnalyzedAt={lastAnalyzedAt}
          onRequestAnalysis={onRequestAnalysis}
          isAnalyzing={isAnalyzing}
        />
      )}

      {/* Panel content with lazy loading */}
      <Suspense fallback={<PanelSkeleton />}>
        <LSSPPanel
          caseId={caseId}
          evidenceCount={evidenceCount}
          onDraftGenerate={onDraftGenerate}
        />
      </Suspense>
    </div>
  );
}
