/**
 * Lawyer Dashboard Page
 * 003-role-based-ui Feature - US2
 * 007-lawyer-portal-v1 Feature - US7 (Today View)
 * 009-calm-control-design-system - Enhanced with Risk Flags & AI Recommendations
 *
 * Calm-Control Dashboard:
 * - 오늘 내가 통제해야 할 사건/증거/드래프트를 상단에 배치
 * - 우선순위/위험도 기반 카드 위주 (타임라인 아님)
 * - 위험 플래그 사건 섹션
 * - AI 추천 작업 큐 (Preview-only)
 */

'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useLawyerDashboard } from '@/hooks/useLawyerDashboard';
import { useTodayView } from '@/hooks/useTodayView';
import { useRiskFlags } from '@/hooks/useRiskFlags';
import { useAIRecommendations } from '@/hooks/useAIRecommendations';
import { StatsCard } from '@/components/lawyer/StatsCard';
import { TodayCard } from '@/components/lawyer/TodayCard';
import { WeeklyPreview } from '@/components/lawyer/WeeklyPreview';
import { RiskFlagCard } from '@/components/lawyer/RiskFlagCard';
import { AIRecommendationCard } from '@/components/lawyer/AIRecommendationCard';
import { DashboardSkeleton } from '@/components/shared/LoadingSkeletons';
import { useRole } from '@/hooks/useRole';

// Icons for stats cards
const BriefcaseIcon = () => (
  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
  </svg>
);

const ActiveIcon = () => (
  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const PendingIcon = () => (
  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CompletedIcon = () => (
  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

// Recent Case Item
function RecentCaseItem({
  id,
  title,
  client_name,
  status,
  updated_at,
  onClick,
}: {
  id: string;
  title: string;
  client_name?: string;
  status: string;
  updated_at: string;
  onClick: () => void;
}) {
  const statusStyles: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    open: 'bg-blue-100 text-blue-700',
    in_progress: 'bg-yellow-100 text-yellow-700',
    closed: 'bg-gray-100 text-gray-500',
  };

  const statusLabels: Record<string, string> = {
    active: '진행중',
    open: '열림',
    in_progress: '검토중',
    closed: '완료',
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return '방금 전';
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;
    return date.toLocaleDateString('ko-KR');
  };

  return (
    <div
      onClick={onClick}
      className="flex items-center gap-4 p-4 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 truncate">{title}</p>
        <p className="text-sm text-gray-500">{client_name || '-'}</p>
      </div>
      <div className="flex items-center gap-3">
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusStyles[status] || statusStyles.active}`}>
          {statusLabels[status] || status}
        </span>
        <span className="text-xs text-gray-400">{formatDate(updated_at)}</span>
      </div>
    </div>
  );
}

export default function LawyerDashboardPage() {
  const router = useRouter();
  const { user } = useRole();
  const { data, isLoading, error } = useLawyerDashboard();
  const {
    urgent,
    thisWeek,
    allComplete,
    isLoading: todayLoading,
  } = useTodayView();
  const { cases: riskCases, isLoading: riskLoading } = useRiskFlags();
  const { recommendations, isLoading: aiLoading } = useAIRecommendations();

  // Loading state
  if (isLoading) {
    return <DashboardSkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">대시보드</h1>
          <p className="text-red-500 mt-1">오류: {error}</p>
        </div>
      </div>
    );
  }

  const statsIcons = [<BriefcaseIcon key="0" />, <ActiveIcon key="1" />, <PendingIcon key="2" />, <CompletedIcon key="3" />];

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">대시보드</h1>
        <p className="text-gray-500 mt-1">
          환영합니다{user?.name ? `, ${user.name}님` : ''}. 오늘의 업무 현황을 확인하세요.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data?.stats?.stats_cards?.map((card, index) => (
          <StatsCard
            key={card.label}
            label={card.label}
            value={card.value}
            change={card.change}
            trend={card.trend as 'up' | 'down' | 'stable'}
            icon={statsIcons[index % statsIcons.length]}
          />
        )) || (
          <>
            <StatsCard label="전체 케이스" value={data?.stats?.total_cases || 0} icon={<BriefcaseIcon />} />
            <StatsCard label="진행 중" value={data?.stats?.active_cases || 0} icon={<ActiveIcon />} />
            <StatsCard label="검토 대기" value={data?.stats?.pending_review || 0} icon={<PendingIcon />} />
            <StatsCard label="이번 달 완료" value={data?.stats?.completed_this_month || 0} icon={<CompletedIcon />} />
          </>
        )}
      </div>

      {/* Priority Section: Risk Flags & AI Recommendations (Calm-Control) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Flag Cases - subtle emphasis, no screaming colors */}
        <RiskFlagCard cases={riskCases} isLoading={riskLoading} />

        {/* AI Recommendations - Preview-only, manual trigger */}
        <AIRecommendationCard recommendations={recommendations} isLoading={aiLoading} />
      </div>

      {/* Today View Section (US7) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Urgent Items */}
        <TodayCard items={urgent} allComplete={allComplete} isLoading={todayLoading} />

        {/* This Week's Preview */}
        <WeeklyPreview items={thisWeek} isLoading={todayLoading} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Cases - Full width */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">최근 케이스</h2>
            <Link
              href="/lawyer/cases"
              className="text-sm text-blue-600 hover:underline"
            >
              전체보기
            </Link>
          </div>
          <div className="divide-y divide-gray-200">
            {data?.recent_cases && data.recent_cases.length > 0 ? (
              data.recent_cases.map((caseItem) => (
                <RecentCaseItem
                  key={caseItem.id}
                  {...caseItem}
                  onClick={() => router.push(`/lawyer/cases/${caseItem.id}`)}
                />
              ))
            ) : (
              <p className="text-center text-gray-500 py-8">
                최근 케이스가 없습니다.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
