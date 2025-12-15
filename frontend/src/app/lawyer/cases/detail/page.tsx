'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import Link from 'next/link';
import CaseDetailClient from '@/components/case/CaseDetailClient';

function LawyerCaseDetailContent() {
  const searchParams = useSearchParams();
  const caseId = searchParams.get('caseId');
  const returnUrl = searchParams.get('returnUrl');

  if (!caseId) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center text-center space-y-4">
        <p className="text-lg text-[var(--color-text-secondary)]">
          조회할 사건 ID가 전달되지 않았습니다.
        </p>
        <Link
          href="/lawyer/cases"
          className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          케이스 목록으로 가기
        </Link>
      </div>
    );
  }

  return (
    <CaseDetailClient
      id={caseId}
      apiBasePath="/lawyer"
      defaultReturnUrl={returnUrl || '/lawyer/cases'}
    />
  );
}

export default function LawyerCaseDetailByQuery() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>}>
      <LawyerCaseDetailContent />
    </Suspense>
  );
}
