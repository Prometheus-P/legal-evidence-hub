/**
 * CaseSummaryTab Component
 *
 * Embedded case summary view combining ExplainerCard content
 * with case dashboard metrics.
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
  RefreshCw,
  AlertCircle,
  TrendingUp,
  Scale,
  Users,
} from 'lucide-react';
import type { CaseSummaryResponse } from '@/types/summary';
import { formatSummaryDate, formatSummaryDateTime } from '@/types/summary';
import { getCaseSummary, downloadCaseSummaryPdf } from '@/lib/api/summary';

interface CaseSummaryTabProps {
  caseId: string;
  caseTitle?: string;
  onShare?: () => void;
}

export function CaseSummaryTab({ caseId, caseTitle, onShare }: CaseSummaryTabProps) {
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
    } catch {
      setError('요약 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    if (caseId) {
      fetchSummary();
    }
  }, [caseId, fetchSummary]);

  const handleDownloadPdf = async () => {
    try {
      await downloadCaseSummaryPdf(caseId);
    } catch {
      alert('PDF 다운로드에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="w-8 h-8 animate-spin text-[var(--color-primary)]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <button
          onClick={fetchSummary}
          className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          다시 시도
        </button>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
        <p className="text-neutral-600 dark:text-neutral-400">요약 정보가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Quick Stats Dashboard */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <DashboardCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="진행률"
          value={`${summary.progress_percent}%`}
          bgColor="bg-blue-50 dark:bg-blue-900/20"
          iconColor="text-blue-600 dark:text-blue-400"
        />
        <DashboardCard
          icon={<Scale className="w-5 h-5" />}
          label="현재 단계"
          value={summary.current_stage || '진행 전'}
          bgColor="bg-purple-50 dark:bg-purple-900/20"
          iconColor="text-purple-600 dark:text-purple-400"
          isText
        />
        <DashboardCard
          icon={<FileText className="w-5 h-5" />}
          label="증거 자료"
          value={`${summary.evidence_total}건`}
          bgColor="bg-orange-50 dark:bg-orange-900/20"
          iconColor="text-orange-600 dark:text-orange-400"
        />
        <DashboardCard
          icon={<Calendar className="w-5 h-5" />}
          label="다음 일정"
          value={summary.next_schedules.length > 0 ? `${summary.next_schedules.length}건` : '없음'}
          bgColor="bg-teal-50 dark:bg-teal-900/20"
          iconColor="text-teal-600 dark:text-teal-400"
        />
      </div>

      {/* Progress Bar */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">
              {summary.current_stage || '진행 전'}
            </h3>
            <p className="text-sm text-blue-600 dark:text-blue-400">
              전체 진행률
            </p>
          </div>
          <div className="text-2xl font-bold text-blue-700 dark:text-blue-300">
            {summary.progress_percent}%
          </div>
        </div>
        <div className="h-3 bg-blue-200 dark:bg-blue-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
            style={{ width: `${summary.progress_percent}%` }}
          />
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Completed Stages */}
        <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-semibold text-neutral-900 dark:text-white mb-4">
            <CheckCircle className="w-5 h-5 text-green-500" />
            완료된 단계
          </h3>
          {summary.completed_stages.length > 0 ? (
            <ul className="space-y-3">
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
            <p className="text-neutral-500 dark:text-neutral-400 text-sm py-4 text-center">
              아직 완료된 단계가 없습니다.
            </p>
          )}
        </div>

        {/* Next Schedules */}
        <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-semibold text-neutral-900 dark:text-white mb-4">
            <Calendar className="w-5 h-5 text-blue-500" />
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
                        <span className="w-3 h-3 flex items-center justify-center text-xs">📍</span>
                        {schedule.location}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-neutral-500 dark:text-neutral-400 text-sm py-4 text-center">
              예정된 일정이 없습니다.
            </p>
          )}
        </div>
      </div>

      {/* Evidence Stats */}
      <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg p-4">
        <h3 className="flex items-center gap-2 font-semibold text-neutral-900 dark:text-white mb-4">
          <FileText className="w-5 h-5 text-orange-500" />
          증거 현황
        </h3>
        {summary.evidence_total > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {summary.evidence_stats.map((stat, index) => (
              <div key={index} className="bg-neutral-50 dark:bg-neutral-700/50 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-neutral-900 dark:text-white">
                  {stat.count}
                </div>
                <div className="text-sm text-neutral-500 dark:text-neutral-400">
                  {stat.category}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-neutral-500 dark:text-neutral-400 text-sm py-4 text-center">
            등록된 증거가 없습니다.
          </p>
        )}
      </div>

      {/* Lawyer Info */}
      {summary.lawyer && (
        <div className="bg-neutral-100 dark:bg-neutral-700/50 rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-semibold text-neutral-900 dark:text-white mb-3">
            <User className="w-5 h-5" />
            담당 변호사
          </h3>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white font-bold">
              {summary.lawyer.name.charAt(0)}
            </div>
            <div>
              <div className="font-medium text-neutral-900 dark:text-white">
                {summary.lawyer.name}
              </div>
              <div className="text-sm text-neutral-600 dark:text-neutral-400 space-y-0.5">
                {summary.lawyer.phone && <div>📞 {summary.lawyer.phone}</div>}
                {summary.lawyer.email && <div>✉️ {summary.lawyer.email}</div>}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-neutral-200 dark:border-neutral-700">
        <div className="text-xs text-neutral-400">
          생성일시: {formatSummaryDateTime(summary.generated_at)}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchSummary}
            className="flex items-center gap-2 px-4 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            새로고침
          </button>
          <button
            onClick={handleDownloadPdf}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-neutral-200 dark:bg-neutral-600 text-neutral-700 dark:text-neutral-200 rounded-lg hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-colors"
          >
            <Download className="w-4 h-4" />
            PDF 다운로드
          </button>
          {onShare && (
            <button
              onClick={onShare}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
            >
              <Share2 className="w-4 h-4" />
              의뢰인에게 전송
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Dashboard card component
function DashboardCard({
  icon,
  label,
  value,
  bgColor,
  iconColor,
  isText = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  bgColor: string;
  iconColor: string;
  isText?: boolean;
}) {
  return (
    <div className={`${bgColor} rounded-lg p-4`}>
      <div className="flex items-start justify-between">
        <div className={iconColor}>{icon}</div>
      </div>
      <div className="mt-3">
        <div className="text-sm text-neutral-600 dark:text-neutral-400">{label}</div>
        <div className={`font-bold ${isText ? 'text-base truncate' : 'text-xl'} text-neutral-900 dark:text-white mt-1`}>
          {value}
        </div>
      </div>
    </div>
  );
}

export default CaseSummaryTab;
