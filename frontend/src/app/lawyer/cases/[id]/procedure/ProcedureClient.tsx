/**
 * Procedure Client Component
 * T145 - US3: Procedure stage tracking page for a case
 */

'use client';

import { useProcedure } from '@/hooks/useProcedure';
import { useCaseIdFromUrl } from '@/hooks/useCaseIdFromUrl';
import { ProcedureTimeline } from '@/components/procedure';
import Link from 'next/link';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';

interface ProcedureClientProps {
  caseId: string;
}

export default function ProcedureClient({ caseId: paramCaseId }: ProcedureClientProps) {
  // Use URL path for case ID (handles static export fallback)
  const caseId = useCaseIdFromUrl(paramCaseId);
  const {
    stages,
    currentStage,
    progressPercent,
    validNextStages,
    loading,
    error,
    updateStage,
    completeStage,
    skipStage,
    transition,
    initializeTimeline,
    isInitialized,
  } = useProcedure(caseId);

  const procedurePath = getLawyerCasePath('procedure', caseId);
  const detailPath = getCaseDetailPath('lawyer', caseId, { returnUrl: procedurePath });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href={detailPath}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  절차 진행 현황
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  사건 진행 단계를 관리합니다
                </p>
              </div>
            </div>

            {/* Progress Badge */}
            {isInitialized && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-full">
                <span className="text-sm text-blue-700 dark:text-blue-300">
                  진행률
                </span>
                <span className="font-semibold text-blue-700 dark:text-blue-300">
                  {progressPercent}%
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ProcedureTimeline
          stages={stages}
          currentStage={currentStage}
          progressPercent={progressPercent}
          validNextStages={validNextStages}
          loading={loading}
          error={error}
          onUpdateStage={updateStage}
          onCompleteStage={completeStage}
          onSkipStage={skipStage}
          onTransition={transition}
          onInitialize={initializeTimeline}
        />

        {/* Help Text */}
        <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <h3 className="font-medium text-gray-900 dark:text-white mb-2">
            사용 안내
          </h3>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li>• 각 단계 카드를 클릭하면 상세 정보를 확인하고 수정할 수 있습니다.</li>
            <li>• 현재 단계에서 &quot;완료&quot; 또는 &quot;건너뛰기&quot;를 선택할 수 있습니다.</li>
            <li>• 다음 단계 버튼을 클릭하면 자동으로 현재 단계가 완료되고 다음 단계로 이동합니다.</li>
            <li>• 예정일이 임박한 단계는 D-day 표시가 나타납니다.</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
