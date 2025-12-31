/**
 * Precedent Card Component
 * 012-precedent-integration: T026
 */

'use client';

import type { PrecedentCase } from '@/types/precedent';

interface PrecedentCardProps {
  precedent: PrecedentCase;
  onClick?: () => void;
}

export function PrecedentCard({ precedent, onClick }: PrecedentCardProps) {
  const scorePercentage = Math.round(precedent.similarity_score * 100);

  return (
    <button
      type="button"
      className="w-full text-left border rounded-lg p-4 hover:border-blue-500 transition-colors bg-white dark:bg-neutral-800 dark:border-neutral-700 dark:hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">{precedent.case_ref}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">{precedent.court}</p>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-2 py-1 rounded text-xs font-medium ${
              scorePercentage >= 80
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                : scorePercentage >= 60
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                : 'bg-gray-100 text-gray-800 dark:bg-neutral-700 dark:text-gray-300'
            }`}
          >
            {scorePercentage}% 유사
          </span>
        </div>
      </div>

      {/* Date */}
      <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">선고일: {precedent.decision_date}</p>

      {/* Summary */}
      <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-3">{precedent.summary}</p>

      {/* Division Ratio */}
      {precedent.division_ratio && (
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs text-gray-500 dark:text-gray-400">재산분할:</span>
          <div className="flex-1 h-2 bg-gray-200 dark:bg-neutral-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500"
              style={{ width: `${precedent.division_ratio.plaintiff}%` }}
            />
          </div>
          <span className="text-xs text-gray-600 dark:text-gray-400">
            {precedent.division_ratio.plaintiff}:{precedent.division_ratio.defendant}
          </span>
        </div>
      )}

      {/* Key Factors */}
      {precedent.key_factors.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {precedent.key_factors.slice(0, 4).map((factor, index) => (
            <span
              key={index}
              className="px-2 py-0.5 bg-gray-100 dark:bg-neutral-700 text-gray-600 dark:text-gray-300 text-xs rounded"
            >
              {factor}
            </span>
          ))}
        </div>
      )}
    </button>
  );
}
