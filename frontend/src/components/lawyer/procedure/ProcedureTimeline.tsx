/**
 * ProcedureTimeline Component
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 *
 * Main component for displaying procedure timeline
 */

'use client';

import { useMemo } from 'react';
import { StageCard } from './StageCard';
import type { ProcedureStage, NextStageOption } from '@/types/procedure';
import { STAGE_ORDER, STAGE_LABELS } from '@/types/procedure';

interface ProcedureTimelineProps {
  stages: ProcedureStage[];
  currentStage: ProcedureStage | null;
  progressPercent: number;
  validNextStages: NextStageOption[];
  onStageClick?: (stage: ProcedureStage) => void;
  onCompleteStage?: (stage: ProcedureStage) => void;
  onSkipStage?: (stage: ProcedureStage) => void;
  onTransition?: (nextStage: NextStageOption) => void;
  loading?: boolean;
}

export function ProcedureTimeline({
  stages,
  currentStage,
  progressPercent,
  validNextStages,
  onStageClick,
  onCompleteStage,
  onSkipStage,
  onTransition,
  loading = false,
}: ProcedureTimelineProps) {
  // Sort stages by defined order
  const sortedStages = useMemo(() => {
    return [...stages].sort((a, b) => {
      const aIndex = STAGE_ORDER.indexOf(a.stage);
      const bIndex = STAGE_ORDER.indexOf(b.stage);
      return aIndex - bIndex;
    });
  }, [stages]);

  // Check if a stage can transition to next
  const canTransitionFrom = (stage: ProcedureStage): boolean => {
    return validNextStages.some(ns => {
      const currentIndex = STAGE_ORDER.indexOf(stage.stage);
      const nextIndex = STAGE_ORDER.indexOf(ns.stage);
      return nextIndex === currentIndex + 1 ||
             (stage.stage === 'mediation' && ns.stage === 'trial') ||
             (stage.stage === 'mediation_closed' && ns.stage === 'trial');
    });
  };

  if (stages.length === 0) {
    return (
      <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-8 text-center">
        <div className="text-neutral-500 dark:text-neutral-400">
          <svg
            className="mx-auto h-12 w-12 text-neutral-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <p className="mt-4 text-lg font-medium">절차 타임라인이 없습니다</p>
          <p className="mt-2 text-sm">
            타임라인을 초기화하여 사건 진행 상황을 추적하세요
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
            진행률
          </span>
          <span className="text-sm font-semibold text-primary">
            {progressPercent}%
          </span>
        </div>
        <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2.5">
          <div
            className="bg-primary h-2.5 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        {currentStage && (
          <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
            현재 단계: <span className="font-medium">{STAGE_LABELS[currentStage.stage]}</span>
          </p>
        )}
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[23px] top-0 bottom-0 w-0.5 bg-neutral-200 dark:bg-neutral-700" />

        {/* Stage Cards */}
        <div className="space-y-4">
          {sortedStages.map((stage, index) => (
            <StageCard
              key={stage.id}
              stage={stage}
              index={index}
              isActive={currentStage?.id === stage.id}
              canComplete={stage.status === 'in_progress'}
              canSkip={stage.status === 'pending' || stage.status === 'in_progress'}
              canTransition={canTransitionFrom(stage)}
              onClick={() => onStageClick?.(stage)}
              onComplete={() => onCompleteStage?.(stage)}
              onSkip={() => onSkipStage?.(stage)}
              loading={loading}
            />
          ))}
        </div>
      </div>

      {/* Valid Next Stages */}
      {validNextStages.length > 0 && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-4">
          <h4 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-3">
            다음 단계로 이동 가능
          </h4>
          <div className="flex flex-wrap gap-2">
            {validNextStages.map((option) => (
              <button
                key={option.stage}
                onClick={() => onTransition?.(option)}
                disabled={loading}
                className="px-3 py-1.5 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 rounded-md hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors disabled:opacity-50"
              >
                {option.label}로 이동
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
