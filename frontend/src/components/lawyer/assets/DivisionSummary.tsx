/**
 * DivisionSummary Component
 * US2 - 재산분할표 (Asset Division Sheet)
 *
 * Displays division calculation results with Korean legal terminology
 */

'use client';

import type { DivisionSummary as DivisionSummaryType } from '@/types/asset';
import { formatKoreanCurrency } from '@/types/asset';

interface DivisionSummaryProps {
  summary: DivisionSummaryType | null;
  plaintiffRatio?: number;
  defendantRatio?: number;
  onRecalculate?: (plaintiffRatio: number, defendantRatio: number) => void;
  calculating?: boolean;
  className?: string;
}

export default function DivisionSummary({
  summary,
  plaintiffRatio = 50,
  defendantRatio = 50,
  onRecalculate,
  calculating = false,
  className = '',
}: DivisionSummaryProps) {
  const cardClass =
    'bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4';
  const labelClass = 'text-sm text-neutral-500 dark:text-neutral-400';
  const valueClass = 'text-lg font-semibold text-neutral-900 dark:text-white';

  if (!summary) {
    return (
      <div className={`${cardClass} ${className}`}>
        <div className="text-center py-8 text-neutral-500 dark:text-neutral-400">
          <p className="mb-4">아직 재산분할 계산이 수행되지 않았습니다.</p>
          {onRecalculate && (
            <button
              onClick={() => onRecalculate(plaintiffRatio, defendantRatio)}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-hover transition-colors"
              disabled={calculating}
            >
              {calculating ? '계산 중...' : '분할 계산하기'}
            </button>
          )}
        </div>
      </div>
    );
  }

  const settlementDirection =
    summary.settlement_amount > 0
      ? '원고 → 피고'
      : summary.settlement_amount < 0
        ? '피고 → 원고'
        : '없음';

  return (
    <div className={className}>
      {/* Header with recalculate button */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
          재산분할 계산 결과
        </h3>
        {onRecalculate && (
          <button
            onClick={() => onRecalculate(summary.plaintiff_ratio, summary.defendant_ratio)}
            className="px-3 py-1.5 text-sm bg-primary text-white rounded-md hover:bg-primary-hover transition-colors"
            disabled={calculating}
          >
            {calculating ? '계산 중...' : '재계산'}
          </button>
        )}
      </div>

      {/* Ratio display */}
      <div className={`${cardClass} mb-4`}>
        <div className="flex items-center justify-between mb-3">
          <span className={labelClass}>분할 비율 (원고:피고)</span>
          <span className={valueClass}>
            {summary.plaintiff_ratio}:{summary.defendant_ratio}
          </span>
        </div>
        <div className="w-full h-4 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${summary.plaintiff_ratio}%` }}
          />
        </div>
        <div className="flex justify-between mt-1 text-xs text-neutral-500 dark:text-neutral-400">
          <span>원고 {summary.plaintiff_ratio}%</span>
          <span>피고 {summary.defendant_ratio}%</span>
        </div>
      </div>

      {/* Asset totals */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className={cardClass}>
          <div className={labelClass}>공동재산 총액</div>
          <div className={valueClass}>{formatKoreanCurrency(summary.total_marital_assets)}</div>
        </div>
        <div className={cardClass}>
          <div className={labelClass}>부채 총액</div>
          <div className={`${valueClass} text-error`}>
            -{formatKoreanCurrency(summary.total_debts)}
          </div>
        </div>
        <div className={cardClass}>
          <div className={labelClass}>원고 특유재산</div>
          <div className={valueClass}>
            {formatKoreanCurrency(summary.total_separate_plaintiff)}
          </div>
        </div>
        <div className={cardClass}>
          <div className={labelClass}>피고 특유재산</div>
          <div className={valueClass}>
            {formatKoreanCurrency(summary.total_separate_defendant)}
          </div>
        </div>
      </div>

      {/* Net value and shares */}
      <div className={`${cardClass} mb-4`}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-neutral-50 dark:bg-neutral-900 rounded-lg">
            <div className={labelClass}>순 공동재산</div>
            <div className="text-2xl font-bold text-neutral-900 dark:text-white">
              {formatKoreanCurrency(summary.net_marital_value)}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              공동재산 - 부채
            </div>
          </div>
          <div className="text-center p-4 bg-primary-light rounded-lg">
            <div className={labelClass}>원고 몫</div>
            <div className="text-2xl font-bold text-primary">
              {formatKoreanCurrency(summary.plaintiff_share)}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              현재 보유: {formatKoreanCurrency(summary.plaintiff_holdings)}
            </div>
          </div>
          <div className="text-center p-4 bg-secondary-light rounded-lg">
            <div className={labelClass}>피고 몫</div>
            <div className="text-2xl font-bold text-secondary">
              {formatKoreanCurrency(summary.defendant_share)}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              현재 보유: {formatKoreanCurrency(summary.defendant_holdings)}
            </div>
          </div>
        </div>
      </div>

      {/* Settlement amount */}
      <div
        className={`${cardClass} ${
          summary.settlement_amount !== 0
            ? 'border-2 border-warning bg-warning-light'
            : ''
        }`}
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
              정산금 (Settlement)
            </div>
            <div className="text-xs text-neutral-500 dark:text-neutral-500 mt-1">
              {settlementDirection}
            </div>
          </div>
          <div
            className={`text-3xl font-bold ${
              summary.settlement_amount > 0
                ? 'text-primary'
                : summary.settlement_amount < 0
                  ? 'text-secondary'
                  : 'text-neutral-500'
            }`}
          >
            {summary.settlement_amount === 0
              ? '0원'
              : formatKoreanCurrency(Math.abs(summary.settlement_amount))}
          </div>
        </div>
        {summary.settlement_amount !== 0 && (
          <div className="mt-3 p-3 bg-white dark:bg-neutral-800 rounded-md text-sm text-neutral-600 dark:text-neutral-400">
            {summary.settlement_amount > 0
              ? `원고가 피고에게 ${formatKoreanCurrency(summary.settlement_amount)}을 지급해야 합니다.`
              : `피고가 원고에게 ${formatKoreanCurrency(Math.abs(summary.settlement_amount))}을 지급해야 합니다.`}
          </div>
        )}
      </div>

      {/* Calculation timestamp */}
      {summary.calculated_at && (
        <div className="mt-4 text-xs text-neutral-400 text-right">
          계산일시: {new Date(summary.calculated_at).toLocaleString('ko-KR')}
        </div>
      )}

      {/* Notes */}
      {summary.notes && (
        <div className="mt-4 p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
          <div className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-1">
            메모
          </div>
          <div className="text-sm text-neutral-700 dark:text-neutral-300">{summary.notes}</div>
        </div>
      )}
    </div>
  );
}
