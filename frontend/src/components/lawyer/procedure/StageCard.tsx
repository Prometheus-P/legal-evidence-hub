/**
 * StageCard Component
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 *
 * Individual stage card in the procedure timeline
 */

'use client';

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
  index: number;
  isActive?: boolean;
  canComplete?: boolean;
  canSkip?: boolean;
  canTransition?: boolean;
  onClick?: () => void;
  onComplete?: () => void;
  onSkip?: () => void;
  loading?: boolean;
}

export function StageCard({
  stage,
  index,
  isActive = false,
  canComplete = false,
  canSkip = false,
  onClick,
  onComplete,
  onSkip,
  loading = false,
}: StageCardProps) {
  const statusColor = STATUS_COLORS[stage.status];
  const daysUntil = calculateDaysUntil(stage.scheduled_date);

  // Get status icon
  const getStatusIcon = () => {
    switch (stage.status) {
      case 'completed':
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'in_progress':
        return (
          <svg className="w-5 h-5 text-blue-600 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clipRule="evenodd"
            />
          </svg>
        );
      case 'skipped':
        return (
          <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
              clipRule="evenodd"
            />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  return (
    <div
      className={`relative pl-12 cursor-pointer transition-all ${
        isActive ? 'scale-[1.02]' : ''
      }`}
      onClick={onClick}
    >
      {/* Timeline Node */}
      <div
        className={`absolute left-0 w-12 h-12 rounded-full flex items-center justify-center ${
          statusColor.bg
        } ${statusColor.border} border-2 z-10 bg-white dark:bg-neutral-800`}
      >
        {getStatusIcon()}
      </div>

      {/* Card Content */}
      <div
        className={`bg-white dark:bg-neutral-800 rounded-lg border-2 ${
          isActive
            ? 'border-primary shadow-lg'
            : 'border-neutral-200 dark:border-neutral-700'
        } p-4 ml-4 hover:shadow-md transition-shadow`}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-neutral-500 dark:text-neutral-400">
              {index + 1}단계
            </span>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
              {STAGE_LABELS[stage.stage]}
            </h3>
          </div>
          <span
            className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColor.bg} ${statusColor.text}`}
          >
            {STATUS_LABELS[stage.status]}
          </span>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-2 gap-4 text-sm mb-3">
          <div>
            <span className="text-neutral-500 dark:text-neutral-400">예정일:</span>
            <span className="ml-2 text-neutral-700 dark:text-neutral-300">
              {formatStageDate(stage.scheduled_date)}
            </span>
          </div>
          <div>
            <span className="text-neutral-500 dark:text-neutral-400">완료일:</span>
            <span className="ml-2 text-neutral-700 dark:text-neutral-300">
              {formatStageDate(stage.completed_date)}
            </span>
          </div>
        </div>

        {/* Court Info */}
        {(stage.court_reference || stage.judge_name || stage.court_room) && (
          <div className="text-sm text-neutral-600 dark:text-neutral-400 mb-3 space-y-1">
            {stage.court_reference && (
              <p>
                <span className="font-medium">사건번호:</span> {stage.court_reference}
              </p>
            )}
            {stage.judge_name && (
              <p>
                <span className="font-medium">담당 판사:</span> {stage.judge_name}
              </p>
            )}
            {stage.court_room && (
              <p>
                <span className="font-medium">법정:</span> {stage.court_room}
              </p>
            )}
          </div>
        )}

        {/* Outcome */}
        {stage.outcome && (
          <div className="text-sm mb-3">
            <span className="text-neutral-500 dark:text-neutral-400">결과:</span>
            <span className="ml-2 font-medium text-neutral-700 dark:text-neutral-300">
              {stage.outcome}
            </span>
          </div>
        )}

        {/* Notes */}
        {stage.notes && (
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2">
            {stage.notes}
          </p>
        )}

        {/* Deadline Warning */}
        {daysUntil !== null && stage.status !== 'completed' && stage.status !== 'skipped' && (
          <div
            className={`text-xs px-2 py-1 rounded-md inline-block mb-3 ${
              daysUntil < 0
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                : daysUntil <= 3
                ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300'
                : daysUntil <= 7
                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
            }`}
          >
            {daysUntil < 0
              ? `${Math.abs(daysUntil)}일 지남`
              : daysUntil === 0
              ? '오늘'
              : `${daysUntil}일 남음`}
          </div>
        )}

        {/* Documents Badge */}
        {stage.documents && stage.documents.length > 0 && (
          <div className="flex items-center gap-1 text-xs text-neutral-500 dark:text-neutral-400 mb-3">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>{stage.documents.length}개 문서</span>
          </div>
        )}

        {/* Actions */}
        {(canComplete || canSkip) && (
          <div className="flex gap-2 pt-2 border-t border-neutral-200 dark:border-neutral-700">
            {canComplete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onComplete?.();
                }}
                disabled={loading}
                className="px-3 py-1.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-md hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors disabled:opacity-50"
              >
                완료 처리
              </button>
            )}
            {canSkip && stage.status === 'pending' && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onSkip?.();
                }}
                disabled={loading}
                className="px-3 py-1.5 text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-md hover:bg-yellow-200 dark:hover:bg-yellow-900/50 transition-colors disabled:opacity-50"
              >
                건너뛰기
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
