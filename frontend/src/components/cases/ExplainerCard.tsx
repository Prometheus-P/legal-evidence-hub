/**
 * ExplainerCard Component
 * US8 - 진행 상태 요약 카드 (Progress Summary Cards)
 *
 * Displays a 1-page case summary card for client communication
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle,
  Clock,
  Calendar,
  FileText,
  User,
  Download,
  Share2,
  X,
  RefreshCw,
} from 'lucide-react';
import type { CaseSummaryResponse } from '@/types/summary';
import { formatSummaryDate, formatSummaryDateTime } from '@/types/summary';
import { getCaseSummary, downloadCaseSummaryPdf } from '@/lib/api/summary';

interface ExplainerCardProps {
  caseId: string;
  isOpen: boolean;
  onClose: () => void;
  onShare?: () => void;
}

export default function ExplainerCard({
  caseId,
  isOpen,
  onClose,
  onShare,
}: ExplainerCardProps) {
  const [summary, setSummary] = useState<CaseSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = useCallback(async () => {
    if (!caseId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await getCaseSummary(caseId);
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setSummary(response.data);
      }
    } catch (err) {
      setError('요약 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    if (isOpen && caseId) {
      fetchSummary();
    }
  }, [isOpen, caseId, fetchSummary]);

  const handleDownloadPdf = async () => {
    try {
      await downloadCaseSummaryPdf(caseId);
    } catch (err) {
      alert('PDF 다운로드에 실패했습니다.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-2xl bg-white dark:bg-neutral-800 rounded-lg shadow-xl max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
            <div>
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                사건 진행 현황 요약
              </h2>
              {summary && (
                <p className="text-sm text-neutral-500 dark:text-neutral-400">
                  {summary.case_title}
                  {summary.court_reference && ` (${summary.court_reference})`}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchSummary}
                disabled={loading}
                className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 disabled:opacity-50"
                title="새로고침"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onClose}
                className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
            {loading && (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-primary" />
              </div>
            )}

            {error && (
              <div className="text-center py-12 text-red-500">
                <p>{error}</p>
                <button
                  onClick={fetchSummary}
                  className="mt-4 text-primary hover:underline"
                >
                  다시 시도
                </button>
              </div>
            )}

            {!loading && !error && summary && (
              <div className="space-y-6">
                {/* Current Stage */}
                <div className="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 p-4 rounded-r-lg">
                  <div className="text-sm text-blue-600 dark:text-blue-400 mb-1">
                    현재 단계
                  </div>
                  <div className="text-xl font-semibold text-blue-900 dark:text-blue-100">
                    {summary.current_stage || '진행 전'}
                  </div>
                  {/* Progress bar */}
                  <div className="mt-3">
                    <div className="h-2 bg-blue-200 dark:bg-blue-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 transition-all duration-300"
                        style={{ width: `${summary.progress_percent}%` }}
                      />
                    </div>
                    <div className="text-right text-sm text-blue-600 dark:text-blue-400 mt-1">
                      진행률 {summary.progress_percent}%
                    </div>
                  </div>
                </div>

                {/* Completed Stages */}
                <div>
                  <h3 className="flex items-center gap-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    완료된 단계
                  </h3>
                  {summary.completed_stages.length > 0 ? (
                    <ul className="space-y-2">
                      {summary.completed_stages.map((stage, index) => (
                        <li
                          key={index}
                          className="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-neutral-700 last:border-0"
                        >
                          <span className="flex items-center gap-2 text-neutral-700 dark:text-neutral-300">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            {stage.stage_label}
                          </span>
                          <span className="text-sm text-neutral-500 dark:text-neutral-400">
                            {formatSummaryDate(stage.completed_date)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-neutral-500 dark:text-neutral-400 text-sm">
                      아직 완료된 단계가 없습니다.
                    </p>
                  )}
                </div>

                {/* Next Schedules */}
                <div>
                  <h3 className="flex items-center gap-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                    <Calendar className="w-4 h-4 text-blue-500" />
                    다음 일정
                  </h3>
                  {summary.next_schedules.length > 0 ? (
                    <div className="space-y-3">
                      {summary.next_schedules.map((schedule, index) => (
                        <div
                          key={index}
                          className="bg-neutral-50 dark:bg-neutral-700/50 p-3 rounded-lg"
                        >
                          <div className="font-medium text-neutral-900 dark:text-white">
                            {schedule.event_type}
                          </div>
                          <div className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatSummaryDateTime(schedule.scheduled_date)}
                            </span>
                            {schedule.location && (
                              <span className="flex items-center gap-1 mt-0.5">
                                <span className="w-3 h-3 flex items-center justify-center">📍</span>
                                {schedule.location}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-neutral-500 dark:text-neutral-400 text-sm">
                      예정된 일정이 없습니다.
                    </p>
                  )}
                </div>

                {/* Evidence Stats */}
                <div>
                  <h3 className="flex items-center gap-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                    <FileText className="w-4 h-4 text-orange-500" />
                    증거 현황
                  </h3>
                  {summary.evidence_total > 0 ? (
                    <div>
                      <p className="text-neutral-900 dark:text-white mb-2">
                        총 {summary.evidence_total}건
                      </p>
                      {summary.evidence_stats.length > 0 && (
                        <ul className="text-sm text-neutral-600 dark:text-neutral-400 space-y-1">
                          {summary.evidence_stats.map((stat, index) => (
                            <li key={index}>
                              • {stat.category}: {stat.count}건
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ) : (
                    <p className="text-neutral-500 dark:text-neutral-400 text-sm">
                      등록된 증거가 없습니다.
                    </p>
                  )}
                </div>

                {/* Lawyer Info */}
                {summary.lawyer && (
                  <div className="bg-neutral-100 dark:bg-neutral-700/50 p-4 rounded-lg">
                    <h3 className="flex items-center gap-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                      <User className="w-4 h-4" />
                      담당 변호사
                    </h3>
                    <div className="text-neutral-900 dark:text-white font-medium">
                      {summary.lawyer.name}
                    </div>
                    {summary.lawyer.phone && (
                      <div className="text-sm text-neutral-600 dark:text-neutral-400">
                        📞 {summary.lawyer.phone}
                      </div>
                    )}
                    {summary.lawyer.email && (
                      <div className="text-sm text-neutral-600 dark:text-neutral-400">
                        ✉️ {summary.lawyer.email}
                      </div>
                    )}
                  </div>
                )}

                {/* Generated timestamp */}
                <div className="text-center text-xs text-neutral-400 dark:text-neutral-500 pt-4 border-t border-neutral-200 dark:border-neutral-700">
                  생성일시: {formatSummaryDateTime(summary.generated_at)}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-4 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800/50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-md transition-colors"
            >
              닫기
            </button>
            <button
              onClick={handleDownloadPdf}
              disabled={loading || !summary}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-neutral-200 dark:bg-neutral-600 text-neutral-700 dark:text-neutral-200 rounded-md hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-colors disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              PDF 다운로드
            </button>
            {onShare && (
              <button
                onClick={onShare}
                disabled={loading || !summary}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary-hover transition-colors disabled:opacity-50"
              >
                <Share2 className="w-4 h-4" />
                의뢰인에게 전송
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
