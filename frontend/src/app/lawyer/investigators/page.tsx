'use client';

import { useEffect, useState } from 'react';
import {
  getLawyerAnalytics,
  LawyerAnalyticsResponse,
} from '@/lib/api/lawyer';

export default function LawyerInvestigatorsPage() {
  const [analytics, setAnalytics] = useState<LawyerAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      const response = await getLawyerAnalytics();

      if (response.error) {
        setError(response.error);
        setAnalytics(null);
      } else if (response.data) {
        setAnalytics(response.data);
        setError(null);
      }
      setLoading(false);
    };

    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
            조사원/탐정 배정
          </h1>
          <p className="text-[var(--color-text-secondary)]">
            사건 상태를 기반으로 우선순위를 계산하고 있습니다.
          </p>
        </div>
        <div className="px-4 py-2 rounded-lg bg-[var(--color-bg-secondary)] border border-[var(--color-border-default)] text-sm text-[var(--color-text-secondary)]">
          CloudFront 배포 기준 · 실시간 상태 데이터는 프로덕션 API와 동기화됩니다.
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg border border-red-200 bg-red-50 text-red-700">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)]" />
        </div>
      )}

      {!loading && analytics && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-5 shadow-sm">
              <p className="text-sm text-[var(--color-text-secondary)] mb-1">전체 증거</p>
              <p className="text-2xl font-bold text-[var(--color-text-primary)]">
                {analytics.total_evidence.toLocaleString()}건
              </p>
              <p className="text-xs text-[var(--color-text-secondary)]">
                AI 분석이 완료된 증거 포함
              </p>
            </div>
            <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-5 shadow-sm">
              <p className="text-sm text-[var(--color-text-secondary)] mb-1">평균 사건 기간</p>
              <p className="text-2xl font-bold text-[var(--color-text-primary)]">
                {analytics.avg_case_duration_days.toFixed(1)}일
              </p>
              <p className="text-xs text-[var(--color-text-secondary)]">
                배정 최적화의 기준 지표
              </p>
            </div>
            <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-5 shadow-sm">
              <p className="text-sm text-[var(--color-text-secondary)] mb-1">우선 배정 권장 사건</p>
              <p className="text-2xl font-bold text-[var(--color-text-primary)]">
                {analytics.status_distribution
                  .filter((item) => item.status !== 'closed')
                  .reduce((sum, item) => sum + item.count, 0)}
                건
              </p>
              <p className="text-xs text-[var(--color-text-secondary)]">
                진행 중/검토 대기 사건 기준
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-5 shadow-sm">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
                상태별 사건 분포
              </h2>
              <ul className="space-y-3">
                {analytics.status_distribution.map((item) => (
                  <li key={item.status} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">
                        {item.status}
                      </p>
                      <p className="text-xs text-[var(--color-text-secondary)]">
                        {item.percentage.toFixed(1)}%
                      </p>
                    </div>
                    <span className="text-lg font-semibold text-[var(--color-text-primary)]">
                      {item.count}건
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-5 shadow-sm">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
                월별 사건 트렌드
              </h2>
              <ul className="space-y-3">
                {analytics.monthly_stats.map((month) => (
                  <li key={month.month} className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">
                        {month.month}
                      </p>
                      <p className="text-xs text-[var(--color-text-secondary)]">
                        신규 {month.new_cases} · 완료 {month.completed_cases}
                      </p>
                    </div>
                    <span className="text-sm text-[var(--color-text-secondary)]">
                      증거 {month.evidence_uploaded}건
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      <div className="rounded-xl border border-dashed border-[var(--color-border-default)] bg-[var(--color-bg-secondary)]/60 p-6">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
          조사원 배정 자동화 (WIP)
        </h2>
        <p className="text-sm text-[var(--color-text-secondary)]">
          사건 진행 단계와 위험도, 증거 분석 결과를 기준으로 조사원/탐정을 자동 배정하는 기능이 곧 추가됩니다.
          현재 화면은 API 연결 상태와 배포 구성을 검증하기 위한 미리보기입니다.
        </p>
      </div>
    </div>
  );
}
