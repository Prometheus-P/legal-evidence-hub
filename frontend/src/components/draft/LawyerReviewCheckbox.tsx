/**
 * LawyerReviewCheckbox Component
 * 011-production-bug-fixes Feature - #135
 *
 * Confirmation checkbox for lawyer review of AI-generated drafts.
 * Required before downloading or submitting drafts.
 * Follows legal compliance requirements.
 */

'use client';

import { useState } from 'react';
import { CheckCircle2, AlertCircle, Scale, FileCheck } from 'lucide-react';

interface LawyerReviewCheckboxProps {
  /** Whether the review is confirmed */
  isConfirmed: boolean;
  /** Callback when confirmation state changes */
  onConfirmChange: (confirmed: boolean) => void;
  /** Whether the checkbox is disabled */
  disabled?: boolean;
  /** Optional case ID for audit logging */
  caseId?: string;
  /** Whether to show expanded legal disclaimer */
  showDisclaimer?: boolean;
}

export function LawyerReviewCheckbox({
  isConfirmed,
  onConfirmChange,
  disabled = false,
  showDisclaimer = true,
}: LawyerReviewCheckboxProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 pt-0.5">
          <input
            type="checkbox"
            id="lawyer-review-confirm"
            checked={isConfirmed}
            onChange={(e) => onConfirmChange(e.target.checked)}
            disabled={disabled}
            className="h-5 w-5 rounded border-gray-300 dark:border-neutral-600 text-primary focus:ring-primary disabled:opacity-50 dark:bg-neutral-700"
          />
        </div>
        <div className="flex-1">
          <label
            htmlFor="lawyer-review-confirm"
            className="block font-medium text-gray-900 dark:text-gray-100 cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-primary" />
              변호사 검토 완료 확인
            </span>
          </label>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            본 AI 생성 초안의 내용을 검토하였으며, 사실관계 및 법률적 정확성을 확인하였습니다.
          </p>

          {showDisclaimer && (
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-primary hover:text-primary-hover mt-2 inline-flex items-center gap-1"
            >
              {isExpanded ? '법적 고지 숨기기' : '법적 고지 보기'}
              <svg
                className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}

          {isExpanded && (
            <div className="mt-3 p-3 rounded-lg bg-gray-50 dark:bg-neutral-900 text-xs text-gray-600 dark:text-gray-400 space-y-2">
              <p>
                <strong>1. AI 생성물 고지:</strong> 본 문서는 AI(인공지능)가 생성한 초안이며,
                법률 전문가의 검토 없이 사용될 경우 법적 문제가 발생할 수 있습니다.
              </p>
              <p>
                <strong>2. 최종 책임:</strong> AI 생성 초안의 내용에 대한 최종 책임은
                이를 검토하고 사용하는 변호사에게 있습니다.
              </p>
              <p>
                <strong>3. 사실 확인 의무:</strong> 초안에 포함된 모든 사실관계, 증거 인용,
                법률 조항은 반드시 원본 자료와 대조하여 확인하여야 합니다.
              </p>
              <p>
                <strong>4. 변호사법 준수:</strong> 본 시스템은 변호사의 업무를 보조하는 도구이며,
                비변호사의 법률 사무 취급에 해당하지 않습니다.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Status */}
      <div className="mt-4 flex items-center gap-2">
        {isConfirmed ? (
          <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded-lg">
            <CheckCircle2 className="w-4 h-4" />
            <span>검토 완료 확인됨</span>
            <FileCheck className="w-4 h-4 ml-2" />
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 px-3 py-2 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            <span>다운로드 전 검토 확인이 필요합니다</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default LawyerReviewCheckbox;
