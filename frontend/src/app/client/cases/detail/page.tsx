'use client';

/**
 * Legacy Client Case Detail Page (Query Parameter Route)
 *
 * This page exists for backwards compatibility with old URLs like:
 * /client/cases/detail?caseId=xxx
 *
 * It redirects to the new path-based route: /client/cases/{caseId}/
 * which avoids S3 redirect issues that strip query parameters.
 */

import { useSearchParams, useRouter } from 'next/navigation';
import { Suspense, useEffect } from 'react';
import Link from 'next/link';

function ClientCaseDetailRedirect() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const caseId = searchParams.get('caseId');

  useEffect(() => {
    if (caseId) {
      router.replace(`/client/cases/${caseId}/`);
    }
  }, [caseId, router]);

  if (caseId) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-[400px] flex flex-col items-center justify-center text-center space-y-4">
      <p className="text-lg text-[var(--color-text-secondary)]">
        조회할 사건 ID가 전달되지 않았습니다.
      </p>
      <Link
        href="/client/cases"
        className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
      >
        케이스 목록으로 가기
      </Link>
    </div>
  );
}

export default function ClientCaseDetailByQuery() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>}>
      <ClientCaseDetailRedirect />
    </Suspense>
  );
}
