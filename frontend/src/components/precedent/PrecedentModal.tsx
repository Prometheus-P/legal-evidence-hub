/**
 * Precedent Detail Modal Component
 * 012-precedent-integration: T028
 */

'use client';

import type { PrecedentCase } from '@/types/precedent';

interface PrecedentModalProps {
  precedent: PrecedentCase | null;
  isOpen: boolean;
  onClose: () => void;
}

export function PrecedentModal({ precedent, isOpen, onClose }: PrecedentModalProps) {
  if (!isOpen || !precedent) return null;

  const scorePercentage = Math.round(precedent.similarity_score * 100);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-start">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{precedent.case_ref}</h2>
              <p className="text-sm text-gray-500">{precedent.court}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              aria-label="닫기"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-4">
            {/* Meta Info */}
            <div className="flex flex-wrap gap-4 text-sm">
              <div>
                <span className="text-gray-500">선고일:</span>
                <span className="ml-1 font-medium">{precedent.decision_date}</span>
              </div>
              <div>
                <span className="text-gray-500">유사도:</span>
                <span
                  className={`ml-1 font-medium ${
                    scorePercentage >= 80
                      ? 'text-green-600'
                      : scorePercentage >= 60
                      ? 'text-yellow-600'
                      : 'text-gray-600'
                  }`}
                >
                  {scorePercentage}%
                </span>
              </div>
            </div>

            {/* Division Ratio */}
            {precedent.division_ratio && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">재산분할 비율</h3>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>원고</span>
                      <span>피고</span>
                    </div>
                    <div className="h-4 bg-gray-200 rounded-full overflow-hidden flex">
                      <div
                        className="h-full bg-blue-500"
                        style={{ width: `${precedent.division_ratio.plaintiff}%` }}
                      />
                      <div
                        className="h-full bg-red-400"
                        style={{ width: `${precedent.division_ratio.defendant}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-lg font-bold text-gray-900">
                    {precedent.division_ratio.plaintiff}:{precedent.division_ratio.defendant}
                  </div>
                </div>
              </div>
            )}

            {/* Summary */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">판결 요지</h3>
              <p className="text-gray-600 leading-relaxed">{precedent.summary}</p>
            </div>

            {/* Key Factors */}
            {precedent.key_factors.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">주요 요인</h3>
                <div className="flex flex-wrap gap-2">
                  {precedent.key_factors.map((factor, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
