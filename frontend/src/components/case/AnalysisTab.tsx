'use client';

/**
 * AnalysisTab Component
 * Contains LSSP (Legal Strategy) panel with expandable card layout.
 *
 * Lazy loads heavy panel components for better initial page load performance.
 */

import { Suspense, lazy } from 'react';

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
      </div>
    </div>
  );
}

/**
 * Analysis Tab - Contains LSSP (Legal Strategy) panel
 *
 * Features:
 * - Lazy loading of heavy panels for better initial load
 * - Skeleton loading states
 * - Precedent search panel
 */
export function AnalysisTab({
  caseId,
  evidenceCount,
  onDraftGenerate,
}: AnalysisTabProps) {
  return (
    <div className="space-y-6">
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
