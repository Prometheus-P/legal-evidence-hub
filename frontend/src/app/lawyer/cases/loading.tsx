/**
 * Cases Page Loading State (T065)
 * Shows skeleton while cases list is loading
 */

import { CardListSkeleton } from '@/components/shared/LoadingSkeletons';

export default function CasesLoading() {
  return (
    <div className="space-y-6 p-6" aria-busy="true" aria-label="사건 목록 로딩 중">
      {/* Page Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="animate-pulse bg-gray-200 rounded h-8 w-32" />
          <div className="animate-pulse bg-gray-200 rounded h-4 w-48" />
        </div>
        <div className="animate-pulse bg-gray-200 rounded h-10 w-32" />
      </div>

      {/* Filter Bar Skeleton */}
      <div className="flex flex-wrap gap-3">
        <div className="animate-pulse bg-gray-200 rounded h-10 w-48" />
        <div className="animate-pulse bg-gray-200 rounded h-10 w-32" />
        <div className="animate-pulse bg-gray-200 rounded h-10 w-32" />
      </div>

      {/* Cases Grid */}
      <CardListSkeleton count={6} />

      {/* Screen reader announcement */}
      <span className="sr-only" role="status" aria-live="polite">
        사건 목록을 로딩하고 있습니다. 잠시만 기다려주세요.
      </span>
    </div>
  );
}
