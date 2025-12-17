/**
 * Client Dashboard Page
 * 003-role-based-ui Feature
 *
 * US4: 의뢰인 포털
 * - 케이스 진행 상황
 * - 진행 단계 시각화 (Progress Bar)
 * - 최근 활동
 * - 변호사 연락처
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getClientDashboard } from '@/lib/api/client-portal';
import { getCaseDetailPath } from '@/lib/portalPaths';
import ProgressTracker, { ProgressBar } from '@/components/client/ProgressTracker';
import type { ClientDashboardResponse, RecentActivity } from '@/types/client-portal';

// Activity Item Component
function ActivityItem({
  title,
  description,
  time_ago,
  activity_type,
}: RecentActivity) {
  const typeIcons = {
    evidence: (
      <div className="w-8 h-8 rounded-full bg-[var(--color-primary-light)] flex items-center justify-center text-[var(--color-primary)]">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
    ),
    message: (
      <div className="w-8 h-8 rounded-full bg-[var(--color-success-light)] flex items-center justify-center text-[var(--color-success)]">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </div>
    ),
    document: (
      <div className="w-8 h-8 rounded-full bg-[var(--color-warning-light)] flex items-center justify-center text-[var(--color-warning)]">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    ),
    status: (
      <div className="w-8 h-8 rounded-full bg-[var(--color-secondary-light)] flex items-center justify-center text-[var(--color-secondary)]">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    ),
  };

  return (
    <div className="flex items-start gap-3 p-3 hover:bg-[var(--color-bg-secondary)] rounded-lg transition-colors">
      {typeIcons[activity_type]}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-[var(--color-text-primary)]">{title}</p>
        <p className="text-sm text-[var(--color-text-secondary)] truncate">{description}</p>
      </div>
      <span className="text-xs text-[var(--color-text-tertiary)] whitespace-nowrap">{time_ago}</span>
    </div>
  );
}

export default function ClientDashboardPage() {
  const [dashboardData, setDashboardData] = useState<ClientDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      setError(null);

      const result = await getClientDashboard();

      if (result.error || !result.data) {
        setError(result.error || '대시보드를 불러올 수 없습니다');
      } else {
        setDashboardData(result.data);
      }

      setLoading(false);
    }

    fetchDashboard();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      </div>
    );
  }

  // Error state
  if (error || !dashboardData) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)] p-8 text-center">
          <svg className="w-16 h-16 mx-auto text-[var(--color-error)] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
            대시보드를 불러올 수 없습니다
          </h2>
          <p className="text-[var(--color-text-secondary)] mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="inline-block px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  const { user_name, case_summary, progress_steps, lawyer_info, recent_activities, unread_messages } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Welcome Message */}
      <div className="bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] rounded-xl p-6 text-white">
        <h1 className="text-2xl font-semibold">안녕하세요, {user_name}님</h1>
        {case_summary ? (
          <>
            <p className="mt-2 opacity-90">
              현재 케이스가 {case_summary.next_action ? case_summary.next_action : '순조롭게 진행되고 있습니다'}.
            </p>
            <div className="mt-4 flex items-center gap-2">
              <span className="px-3 py-1 bg-white/20 rounded-full text-sm">
                진행률 {case_summary.progress_percent}%
              </span>
              {unread_messages > 0 && (
                <Link
                  href="/client/messages"
                  className="px-3 py-1 bg-white/30 rounded-full text-sm hover:bg-white/40 transition-colors"
                >
                  읽지 않은 메시지 {unread_messages}개
                </Link>
              )}
            </div>
          </>
        ) : (
          <p className="mt-2 opacity-90">등록된 케이스가 없습니다.</p>
        )}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Case Progress - 2 columns */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-[var(--color-border-default)]">
          <div className="p-4 border-b border-[var(--color-border-default)] flex items-center justify-between">
            <h2 className="font-semibold text-[var(--color-text-primary)]">케이스 진행 상황</h2>
            {case_summary && (
                <Link
                  href={getCaseDetailPath('client', case_summary.id)}
                className="text-sm text-[var(--color-primary)] hover:underline"
              >
                상세보기
              </Link>
            )}
          </div>
          <div className="p-6">
            {progress_steps.length > 0 ? (
              <ProgressTracker steps={progress_steps} />
            ) : (
              <div className="text-center py-8 text-[var(--color-text-secondary)]">
                <svg className="w-12 h-12 mx-auto text-[var(--color-text-tertiary)] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p>진행 중인 케이스가 없습니다</p>
                <Link
                  href="/client/cases"
                  className="inline-block mt-3 text-[var(--color-primary)] hover:underline"
                >
                  케이스 목록 보기
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Lawyer Info - 1 column */}
        <div className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)]">
          <div className="p-4 border-b border-[var(--color-border-default)]">
            <h2 className="font-semibold text-[var(--color-text-primary)]">담당 변호사</h2>
          </div>
          <div className="p-6">
            {lawyer_info ? (
              <>
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full bg-[var(--color-secondary)] flex items-center justify-center text-white text-xl font-semibold">
                    {lawyer_info.name.slice(0, 1)}
                  </div>
                  <div>
                    <p className="font-semibold text-lg text-[var(--color-text-primary)]">{lawyer_info.name}</p>
                    {lawyer_info.firm && (
                      <p className="text-sm text-[var(--color-text-secondary)]">{lawyer_info.firm}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-3">
                  {lawyer_info.phone && (
                    <a
                      href={`tel:${lawyer_info.phone}`}
                      className="flex items-center gap-3 p-3 rounded-lg border border-[var(--color-border-default)] hover:bg-[var(--color-bg-secondary)] transition-colors"
                    >
                      <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      <span className="text-sm">{lawyer_info.phone}</span>
                    </a>
                  )}
                  <a
                    href={`mailto:${lawyer_info.email}`}
                    className="flex items-center gap-3 p-3 rounded-lg border border-[var(--color-border-default)] hover:bg-[var(--color-bg-secondary)] transition-colors"
                  >
                    <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span className="text-sm truncate">{lawyer_info.email}</span>
                  </a>
                  <Link
                    href="/client/messages"
                    className="flex items-center justify-center gap-2 p-3 rounded-lg bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    <span>메시지 보내기</span>
                  </Link>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-[var(--color-text-secondary)]">
                <svg className="w-12 h-12 mx-auto text-[var(--color-text-tertiary)] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <p>담당 변호사가 배정되지 않았습니다</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      {case_summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            href={getCaseDetailPath('client', case_summary.id)}
            className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)] p-4 hover:shadow-md hover:border-[var(--color-primary)] transition-all"
          >
            <svg className="w-8 h-8 text-[var(--color-primary)] mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="font-medium text-[var(--color-text-primary)]">케이스 상세</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">진행 상황 확인</p>
          </Link>

          <Link
            href={`/client/evidence?caseId=${case_summary.id}`}
            className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)] p-4 hover:shadow-md hover:border-[var(--color-primary)] transition-all"
          >
            <svg className="w-8 h-8 text-[var(--color-success)] mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="font-medium text-[var(--color-text-primary)]">증거 업로드</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">새 자료 제출</p>
          </Link>

          <Link
            href="/client/messages"
            className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)] p-4 hover:shadow-md hover:border-[var(--color-primary)] transition-all relative"
          >
            <svg className="w-8 h-8 text-[var(--color-warning)] mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            {unread_messages > 0 && (
              <span className="absolute top-3 right-3 w-5 h-5 bg-[var(--color-error)] text-white text-xs rounded-full flex items-center justify-center">
                {unread_messages}
              </span>
            )}
            <p className="font-medium text-[var(--color-text-primary)]">메시지</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">변호사와 대화</p>
          </Link>

          <Link
            href="/client/billing"
            className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)] p-4 hover:shadow-md hover:border-[var(--color-primary)] transition-all"
          >
            <svg className="w-8 h-8 text-[var(--color-secondary)] mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="font-medium text-[var(--color-text-primary)]">비용 안내</p>
            <p className="text-xs text-[var(--color-text-secondary)] mt-1">결제 내역</p>
          </Link>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-[var(--color-border-default)]">
        <div className="p-4 border-b border-[var(--color-border-default)]">
          <h2 className="font-semibold text-[var(--color-text-primary)]">최근 활동</h2>
        </div>
        {recent_activities.length > 0 ? (
          <div className="divide-y divide-[var(--color-border-default)]">
            {recent_activities.map((activity) => (
              <ActivityItem key={activity.id} {...activity} />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-[var(--color-text-secondary)]">
            <svg className="w-12 h-12 mx-auto text-[var(--color-text-tertiary)] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>최근 활동이 없습니다</p>
          </div>
        )}
      </div>
    </div>
  );
}
