/**
 * ProcedureTimeline Component
 * T141 - US3: Visual timeline of procedure stages
 */

'use client';

import React, { memo, useState, useCallback } from 'react';
import type { ProcedureStage, ProcedureStageUpdate, TransitionToNextStage } from '@/types/procedure';
import { STAGE_ORDER, STAGE_LABELS } from '@/types/procedure';
import { StageCard } from './StageCard';
import { StageModal } from './StageModal';

interface ProcedureTimelineProps {
  stages: ProcedureStage[];
  currentStage: ProcedureStage | null;
  progressPercent: number;
  validNextStages: { stage: string; label: string }[];
  loading?: boolean;
  error?: string | null;
  onUpdateStage: (stageId: string, data: ProcedureStageUpdate) => Promise<ProcedureStage | null>;
  onCompleteStage: (stageId: string, outcome?: string) => Promise<ProcedureStage | null>;
  onSkipStage: (stageId: string, reason?: string) => Promise<ProcedureStage | null>;
  onTransition: (data: TransitionToNextStage) => Promise<boolean>;
  onInitialize?: () => Promise<boolean>;
}

function ProcedureTimelineComponent({
  stages,
  currentStage,
  progressPercent,
  validNextStages,
  loading = false,
  error = null,
  onUpdateStage,
  onCompleteStage,
  onSkipStage,
  onTransition,
  onInitialize,
}: ProcedureTimelineProps) {
  const [selectedStage, setSelectedStage] = useState<ProcedureStage | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [initializing, setInitializing] = useState(false);

  // Get sorted stages by order
  const sortedStages = [...stages].sort((a, b) => {
    const aIndex = STAGE_ORDER.indexOf(a.stage);
    const bIndex = STAGE_ORDER.indexOf(b.stage);
    return aIndex - bIndex;
  });

  const handleStageClick = useCallback((stage: ProcedureStage) => {
    setSelectedStage(stage);
    setIsModalOpen(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setSelectedStage(null);
  }, []);

  const handleInitialize = useCallback(async () => {
    if (!onInitialize) return;
    setInitializing(true);
    try {
      await onInitialize();
    } finally {
      setInitializing(false);
    }
  }, [onInitialize]);

  const handleTransitionToNext = useCallback(async (nextStage: string) => {
    await onTransition({
      next_stage: nextStage as TransitionToNextStage['next_stage'],
      complete_current: true,
    });
  }, [onTransition]);

  // Empty state
  if (stages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <p className="text-gray-600 dark:text-gray-400 text-center mb-4">
          절차 타임라인이 아직 초기화되지 않았습니다.
        </p>
        {onInitialize && (
          <button
            onClick={handleInitialize}
            disabled={initializing}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {initializing ? '초기화 중...' : '타임라인 초기화'}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Progress Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium text-gray-900 dark:text-white">
            진행 상태
          </h3>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {progressPercent}% 완료
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        {currentStage && (
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            현재 단계: <span className="font-medium text-blue-600 dark:text-blue-400">
              {currentStage.stage_label || STAGE_LABELS[currentStage.stage]}
            </span>
          </p>
        )}
      </div>

      {/* Next Stage Transition Buttons */}
      {validNextStages.length > 0 && currentStage && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <p className="text-sm text-blue-700 dark:text-blue-300 mb-3">
            다음 단계로 이동할 수 있습니다:
          </p>
          <div className="flex flex-wrap gap-2">
            {validNextStages.map(({ stage, label }) => (
              <button
                key={stage}
                onClick={() => handleTransitionToNext(stage)}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-blue-800 dark:text-blue-200 dark:hover:bg-blue-700"
              >
                {label}로 이동
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-600" />

        {/* Stage Cards */}
        <div className="space-y-4">
          {sortedStages.map((stage, index) => (
            <div key={stage.id} className="relative flex items-start">
              {/* Timeline Node */}
              <div className={`
                absolute left-4 w-4 h-4 rounded-full border-2 bg-white dark:bg-gray-800 z-10
                ${stage.status === 'completed' ? 'border-green-500 bg-green-500' :
                  stage.status === 'in_progress' ? 'border-blue-500' :
                  stage.status === 'skipped' ? 'border-yellow-500' :
                  'border-gray-300'}
              `}>
                {stage.status === 'completed' && (
                  <svg className="w-3 h-3 text-white absolute -top-0.5 -left-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>

              {/* Stage Card */}
              <div className="ml-12 flex-1">
                <StageCard
                  stage={stage}
                  isActive={currentStage?.id === stage.id}
                  isSelected={selectedStage?.id === stage.id}
                  onClick={handleStageClick}
                  onComplete={stage.status === 'in_progress' ? () => {
                    setSelectedStage(stage);
                    setIsModalOpen(true);
                  } : undefined}
                  onSkip={stage.status === 'pending' || stage.status === 'in_progress' ? () => {
                    setSelectedStage(stage);
                    setIsModalOpen(true);
                  } : undefined}
                  disabled={loading}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        </div>
      )}

      {/* Stage Modal */}
      <StageModal
        stage={selectedStage}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={onUpdateStage}
        onComplete={onCompleteStage}
        onSkip={onSkipStage}
        loading={loading}
      />
    </div>
  );
}

export const ProcedureTimeline = memo(ProcedureTimelineComponent);
export default ProcedureTimeline;
