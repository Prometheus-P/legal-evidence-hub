/**
 * Evidence Review Card Component
 * 009-mvp-gap-closure Feature - US10 (T092)
 *
 * Card component for lawyers to review evidence uploaded by clients.
 * Shows evidence details with approve/reject actions.
 */

'use client';

import { useState } from 'react';
import type { Evidence } from '@/lib/api/evidence';

export type ReviewStatus = 'pending_review' | 'approved' | 'rejected';

export interface EvidenceWithReview extends Evidence {
  review_status?: ReviewStatus;
  uploaded_by?: string;
  uploaded_by_name?: string;
  reviewed_by?: string;
  reviewed_at?: string;
}

interface EvidenceReviewCardProps {
  evidence: EvidenceWithReview;
  onApprove?: (evidenceId: string) => Promise<void>;
  onReject?: (evidenceId: string, reason: string) => Promise<void>;
  onViewDetail?: (evidenceId: string) => void;
}

// File type icon component
function FileTypeIcon({ type }: { type: string }) {
  const iconClass = 'w-6 h-6';

  switch (type) {
    case 'image':
      return (
        <svg className={`${iconClass} text-blue-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    case 'audio':
      return (
        <svg className={`${iconClass} text-green-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      );
    case 'video':
      return (
        <svg className={`${iconClass} text-purple-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      );
    case 'pdf':
      return (
        <svg className={`${iconClass} text-red-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      );
    default:
      return (
        <svg className={`${iconClass} text-gray-500`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
  }
}

// Review status badge
function ReviewStatusBadge({ status }: { status: ReviewStatus }) {
  const config = {
    pending_review: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-700',
      label: '검토 대기',
    },
    approved: {
      bg: 'bg-green-100',
      text: 'text-green-700',
      label: '승인됨',
    },
    rejected: {
      bg: 'bg-red-100',
      text: 'text-red-700',
      label: '반려됨',
    },
  };

  const { bg, text, label } = config[status];

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${bg} ${text}`}>
      {label}
    </span>
  );
}

export default function EvidenceReviewCard({
  evidence,
  onApprove,
  onReject,
  onViewDetail,
}: EvidenceReviewCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const reviewStatus = evidence.review_status || 'pending_review';
  const isPendingReview = reviewStatus === 'pending_review';

  const handleApprove = async () => {
    if (!onApprove) return;
    setIsLoading(true);
    try {
      await onApprove(evidence.id);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReject = async () => {
    if (!onReject || !rejectReason.trim()) return;
    setIsLoading(true);
    try {
      await onReject(evidence.id, rejectReason);
      setShowRejectModal(false);
      setRejectReason('');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <>
      <div className="bg-white rounded-lg border border-[var(--color-border)] p-4 hover:shadow-md transition-shadow">
        {/* Header */}
        <div className="flex items-start gap-4">
          {/* File Icon */}
          <div className="w-12 h-12 rounded-lg bg-[var(--color-bg-secondary)] flex items-center justify-center flex-shrink-0">
            <FileTypeIcon type={evidence.type} />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-[var(--color-text-primary)] truncate">
                {evidence.filename}
              </h3>
              <ReviewStatusBadge status={reviewStatus} />
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-[var(--color-text-secondary)]">
              <span>{formatFileSize(evidence.size)}</span>
              <span>{formatDate(evidence.created_at)}</span>
              {evidence.uploaded_by_name && (
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {evidence.uploaded_by_name}
                </span>
              )}
            </div>

            {/* AI Summary */}
            {evidence.ai_summary && (
              <p className="mt-2 text-sm text-[var(--color-text-secondary)] line-clamp-2">
                {evidence.ai_summary}
              </p>
            )}

            {/* Labels */}
            {evidence.labels && evidence.labels.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {evidence.labels.slice(0, 5).map((label, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 text-xs bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] rounded"
                  >
                    {label}
                  </span>
                ))}
                {evidence.labels.length > 5 && (
                  <span className="px-2 py-0.5 text-xs text-[var(--color-text-tertiary)]">
                    +{evidence.labels.length - 5}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-[var(--color-border)]">
          <button
            type="button"
            onClick={() => onViewDetail?.(evidence.id)}
            className="text-sm text-[var(--color-primary)] hover:underline"
          >
            상세 보기
          </button>

          {isPendingReview && (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowRejectModal(true)}
                disabled={isLoading}
                className="px-3 py-1.5 text-sm border border-red-300 text-red-600 rounded-lg
                  hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed
                  min-h-[36px]"
              >
                반려
              </button>
              <button
                type="button"
                onClick={handleApprove}
                disabled={isLoading}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg
                  hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed
                  min-h-[36px] flex items-center gap-1"
              >
                {isLoading ? (
                  <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    승인
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">증거 반려</h3>
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">
              반려 사유를 입력해 주세요. 의뢰인에게 전달됩니다.
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="반려 사유 입력..."
              className="w-full p-3 border border-[var(--color-border)] rounded-lg resize-none
                focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              rows={4}
            />
            <div className="flex justify-end gap-2 mt-4">
              <button
                type="button"
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
                className="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg
                  hover:bg-[var(--color-bg-secondary)] min-h-[40px]"
              >
                취소
              </button>
              <button
                type="button"
                onClick={handleReject}
                disabled={isLoading || !rejectReason.trim()}
                className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg
                  hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed min-h-[40px]"
              >
                {isLoading ? '처리 중...' : '반려하기'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
