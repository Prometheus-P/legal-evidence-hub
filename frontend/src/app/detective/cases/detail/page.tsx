'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense, useState, useEffect } from 'react';
import Link from 'next/link';
import DetectiveCaseDetailClient from '../[id]/DetectiveCaseDetailClient';

function DetectiveCaseDetailContent() {
  const searchParams = useSearchParams();
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  const caseId = searchParams.get('caseId');

  if (!isHydrated) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!caseId) {
    console.error('[DetectiveCaseDetailPage] caseId is null. URL:', typeof window !== 'undefined' ? window.location.href : 'SSR');
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center text-center space-y-4">
        <p className="text-lg text-[var(--color-text-secondary)]">
          조회할 사건 ID가 전달되지 않았습니다.
        </p>
        <Link
          href="/detective/cases"
          className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          케이스 목록으로 가기
        </Link>
      </div>
    );
  }

  return <DetectiveCaseDetailClient caseId={caseId} />;
}

export default function DetectiveCaseDetailByQuery() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>}>
      <DetectiveCaseDetailContent />
    </Suspense>
  );
}
