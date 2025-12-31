/**
 * StageCard Component
 * T142 - US3: Individual procedure stage card in timeline
 */

'use client';

import React, { memo } from 'react';
import type { ProcedureStage } from '@/types/procedure';
import {
  STAGE_LABELS,
  STATUS_LABELS,
  STATUS_COLORS,
  formatStageDate,
  calculateDaysUntil,
} from '@/types/procedure';

interface StageCardProps {
  stage: ProcedureStage;
  isActive: boolean;
  isSelected: boolean;
  onClick: (stage: ProcedureStage) => void;
  onComplete?: (stage: ProcedureStage) => void;
  onSkip?: (stage: ProcedureStage) => void;
  disabled?: boolean;
}

function StageCardComponent({
  stage,
  isActive,
  isSelected,
  onClick,
  onComplete,
  onSkip,
  disabled = false,
}: StageCardProps) {
  const statusColor = STATUS_COLORS[stage.status];
  const daysUntil = calculateDaysUntil(stage.scheduled_date);

  const getStatusIcon = () => {
    switch (stage.status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'in_progress':
        return (
          <div className="w-5 h-5 border-2 border-blue-500 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          </div>
        );
      case 'skipped':
        return (
          <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        );
      default:
        return <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />;
    }
  };

  return (
    <button
      type="button"
      className={`
        relative w-full text-left p-4 rounded-lg border-2 transition-all duration-200
        ${statusColor.bg} ${statusColor.border}
        ${isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
        ${isActive ? 'shadow-md' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-lg'}
        dark:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-blue-500
      `}
      onClick={() => onClick(stage)}
      disabled={disabled}
      aria-label={`${STAGE_LABELS[stage.stage]} - ${STATUS_LABELS[stage.status]}`}
      aria-pressed={isSelected}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <h3 className={`font-semibold ${statusColor.text}`}>
            {stage.stage_label || STAGE_LABELS[stage.stage]}
          </h3>
        </div>
        <span className={`text-xs px-2 py-1 rounded-full ${statusColor.bg} ${statusColor.text}`}>
          {stage.status_label || STATUS_LABELS[stage.status]}
        </span>
      </div>

      {/* Date Info */}
      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
        {stage.scheduled_date && (
          <p className="flex items-center gap-1">
            <span className="text-gray-500">예정일:</span>
            <span>{formatStageDate(stage.scheduled_date)}</span>
            {daysUntil !== null && daysUntil >= 0 && daysUntil <= 7 && (
              <span className={`ml-1 text-xs px-1.5 py-0.5 rounded ${
                daysUntil === 0 ? 'bg-red-100 text-red-700' :
                daysUntil <= 3 ? 'bg-orange-100 text-orange-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                D{daysUntil === 0 ? '-DAY' : `-${daysUntil}`}
              </span>
            )}
          </p>
        )}
        {stage.completed_date && (
          <p>
            <span className="text-gray-500">완료일:</span>{' '}
            {formatStageDate(stage.completed_date)}
          </p>
        )}
      </div>

      {/* Court Info */}
      {(stage.court_room || stage.judge_name) && (
        <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {stage.court_room && <span>{stage.court_room}</span>}
          {stage.court_room && stage.judge_name && <span> • </span>}
          {stage.judge_name && <span>{stage.judge_name} 판사</span>}
        </div>
      )}

      {/* Outcome */}
      {stage.outcome && (
        <div className="mt-2 text-sm">
          <span className="text-gray-500">결과:</span>{' '}
          <span className="font-medium">{stage.outcome}</span>
        </div>
      )}

      {/* Notes */}
      {stage.notes && (
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
          {stage.notes}
        </p>
      )}

      {/* Action Buttons */}
      {isActive && stage.status === 'in_progress' && (onComplete || onSkip) && (
        <div className="flex gap-2 mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
          {onComplete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onComplete(stage);
              }}
              className="flex-1 px-3 py-1.5 text-sm font-medium text-white bg-success rounded-lg hover:bg-success/90 focus:outline-none focus:ring-2 focus:ring-success focus:ring-offset-2"
              disabled={disabled}
            >
              완료
            </button>
          )}
          {onSkip && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSkip(stage);
              }}
              className="flex-1 px-3 py-1.5 text-sm font-medium text-neutral-700 bg-neutral-200 rounded-lg hover:bg-neutral-300 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 dark:bg-neutral-600 dark:text-neutral-200 dark:hover:bg-neutral-500"
              disabled={disabled}
            >
              건너뛰기
            </button>
          )}
        </div>
      )}
    </button>
  );
}

export const StageCard = memo(StageCardComponent);
export default StageCard;
