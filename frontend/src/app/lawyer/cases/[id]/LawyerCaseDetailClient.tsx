'use client';

/**
 * Lawyer Case Detail Client Component
 * 003-role-based-ui Feature - US3
 *
 * Client-side component for case detail view with evidence list and AI summary.
 */

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api/client';
import ExplainerCard from '@/components/cases/ExplainerCard';
import ShareSummaryModal from '@/components/cases/ShareSummaryModal';
import EditCaseModal from '@/components/cases/EditCaseModal';
import { ApiCase } from '@/lib/api/cases';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';
import { PrecedentPanel } from '@/components/precedent';
import { PartyGraph } from '@/components/party/PartyGraph';

interface CaseDetail {
  id: string;
  title: string;
  clientName?: string;
  description?: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  ownerId: string;
  ownerName?: string;
  ownerEmail?: string;
  evidenceCount: number;
  evidenceSummary: { type: string; count: number }[];
  aiSummary?: string;
  aiLabels: string[];
  recentActivities: { action: string; timestamp: string; user: string }[];
  members: { userId: string; userName?: string; role: string }[];
}

const statusColors: Record<string, string> = {
  active: 'bg-blue-100 text-blue-800',
  open: 'bg-green-100 text-green-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  closed: 'bg-gray-100 text-gray-800',
};

const statusLabels: Record<string, string> = {
  active: '활성',
  open: '진행 중',
  in_progress: '검토 대기',
  closed: '종료',
};

interface CaseDetailResponse {
  id: string;
  title: string;
  client_name?: string;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  owner_name?: string;
  owner_email?: string;
  evidence_count?: number;
  evidence_summary?: { type: string; count: number }[];
  ai_summary?: string;
  ai_labels?: string[];
  recent_activities?: { action: string; timestamp: string; user: string }[];
  members?: { userId: string; userName?: string; role: string }[];
}

interface LawyerCaseDetailClientProps {
  id: string;
}

export default function LawyerCaseDetailClient({ id }: LawyerCaseDetailClientProps) {
  const router = useRouter();

  // caseId 설정 - 빈 값이면 빈 문자열 유지 (API 레벨에서 방어됨)
  const caseId = id || '';
  const detailPath = caseId ? getCaseDetailPath('lawyer', caseId) : '/lawyer/cases/detail';
  const procedurePath = caseId ? getLawyerCasePath('procedure', caseId) : '/lawyer/cases/procedure';
  const assetsPath = caseId ? getLawyerCasePath('assets', caseId) : '/lawyer/cases/assets';

  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'evidence' | 'timeline' | 'members' | 'relations'>('evidence');
  const [showSummaryCard, setShowSummaryCard] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  // 무한 스피너 방지: ID 대기 타임아웃 상태
  const [idWaitTimedOut, setIdWaitTimedOut] = useState(false);

  // Race condition 방어를 위한 ID 검증 플래그 (hooks 이후에 위치해야 함)
  const isIdMissing = !id || id.trim() === '';

  // 무한 스피너 방지: 2초 후에도 ID가 없으면 에러 상태로 전환
  useEffect(() => {
    if (!isIdMissing) {
      setIdWaitTimedOut(false);
      return;
    }

    const timeout = setTimeout(() => {
      if (isIdMissing) {
        setIdWaitTimedOut(true);
      }
    }, 2000);

    return () => clearTimeout(timeout);
  }, [isIdMissing]);

  // Fetch case data with race condition prevention
  useEffect(() => {
    // ID가 없으면 fetch 건너뛰기
    if (!caseId) {
      setIsLoading(false);
      return;
    }

    // 이전 요청 무시 플래그
    let isCancelled = false;

    const fetchCaseDetail = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<CaseDetailResponse>(`/lawyer/cases/${caseId}`);

        // caseId가 변경되어 이 요청이 무효화된 경우 무시
        if (isCancelled) return;

        if (response.error || !response.data) {
          throw new Error(response.error || '케이스 정보를 불러오는데 실패했습니다.');
        }

        const data = response.data;
        setCaseDetail({
          id: data.id,
          title: data.title,
          clientName: data.client_name,
          description: data.description,
          status: data.status,
          createdAt: data.created_at,
          updatedAt: data.updated_at,
          ownerId: data.owner_id,
          ownerName: data.owner_name,
          ownerEmail: data.owner_email,
          evidenceCount: data.evidence_count || 0,
          evidenceSummary: data.evidence_summary || [],
          aiSummary: data.ai_summary,
          aiLabels: data.ai_labels || [],
          recentActivities: data.recent_activities || [],
          members: data.members || [],
        });
      } catch (err) {
        if (isCancelled) return;
        setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchCaseDetail();

    // cleanup: caseId 변경 또는 언마운트 시 이전 요청 무시
    return () => {
      isCancelled = true;
    };
  }, [caseId, router]);

  // Race condition 방어: ID가 없으면 로딩 스피너 또는 에러 표시
  if (isIdMissing) {
    // 2초 후에도 ID가 없으면 에러 UI 표시
    if (idWaitTimedOut) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">잘못된 접근입니다</h2>
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">사건 ID가 올바르지 않거나 전달되지 않았습니다.</p>
            <Link
              href="/lawyer/cases"
              className="inline-flex items-center px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              목록으로 돌아가기
            </Link>
          </div>
        </div>
      );
    }
    // 타임아웃 전에는 로딩 스피너 표시
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
      </div>
    );
  }

  if (error || !caseDetail) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
          {error || '케이스를 찾을 수 없습니다'}
        </h2>
        <Link
          href="/lawyer/cases"
          className="text-[var(--color-primary)] hover:underline"
        >
          케이스 목록으로 돌아가기
        </Link>
      </div>
    );
  }

  const statusColor = statusColors[caseDetail.status] || statusColors.active;
  const statusLabel = statusLabels[caseDetail.status] || caseDetail.status;

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="text-sm text-[var(--color-text-secondary)]">
        <Link href="/lawyer/cases" className="hover:text-[var(--color-primary)]">
          케이스 관리
        </Link>
        <span className="mx-2">/</span>
        <span className="text-[var(--color-text-primary)]">{caseDetail.title}</span>
      </nav>

      {/* Header */}
      <div className="bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
                {caseDetail.title}
              </h1>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusColor}`}>
                {statusLabel}
              </span>
            </div>
            {caseDetail.clientName && (
              <p className="text-[var(--color-text-secondary)]">
                의뢰인: {caseDetail.clientName}
              </p>
            )}
            {caseDetail.description && (
              <p className="mt-2 text-[var(--color-text-secondary)]">
                {caseDetail.description}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Link
              href={procedurePath}
              className="px-4 py-2 border border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-400 rounded-lg text-sm hover:bg-blue-50 dark:hover:bg-blue-900/30 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              절차 진행
            </Link>
            <Link
              href={assetsPath}
              className="px-4 py-2 border border-green-300 dark:border-green-700 text-green-700 dark:text-green-400 rounded-lg text-sm hover:bg-green-50 dark:hover:bg-green-900/30 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              재산분할
            </Link>
            <button
              type="button"
              onClick={() => setShowEditModal(true)}
              className="px-4 py-2 border border-gray-300 dark:border-neutral-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-neutral-700"
            >
              수정
            </button>
            <button
              type="button"
              onClick={() => setShowSummaryCard(true)}
              className="px-4 py-2 border border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-400 rounded-lg text-sm hover:bg-purple-50 dark:hover:bg-purple-900/30 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              요약 카드
            </button>
            <button
              type="button"
              className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg text-sm hover:bg-[var(--color-primary-hover)]"
            >
              AI 분석 요청
            </button>
          </div>
        </div>

        {/* Meta Info */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-neutral-700 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-[var(--color-text-secondary)]">담당자</span>
            <p className="font-medium">{caseDetail.ownerName || '-'}</p>
          </div>
          <div>
            <span className="text-[var(--color-text-secondary)]">생성일</span>
            <p className="font-medium">
              {new Date(caseDetail.createdAt).toLocaleDateString('ko-KR')}
            </p>
          </div>
          <div>
            <span className="text-[var(--color-text-secondary)]">최근 업데이트</span>
            <p className="font-medium">
              {new Date(caseDetail.updatedAt).toLocaleDateString('ko-KR')}
            </p>
          </div>
          <div>
            <span className="text-[var(--color-text-secondary)]">증거 자료</span>
            <p className="font-medium">{caseDetail.evidenceCount}건</p>
          </div>
        </div>

        {/* AI Labels */}
        {caseDetail.aiLabels.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-neutral-700">
            <span className="text-sm text-[var(--color-text-secondary)]">AI 분석 태그</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {caseDetail.aiLabels.map((label, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-sm rounded-full"
                >
                  {label}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Summary */}
      {caseDetail.aiSummary && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-3">
            <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="font-semibold text-purple-800 dark:text-purple-300">AI 분석 요약</h3>
            <span className="text-xs text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/50 px-2 py-0.5 rounded-full">
              Preview Only
            </span>
          </div>
          <p className="text-purple-900 dark:text-purple-200">{caseDetail.aiSummary}</p>
        </div>
      )}

      {/* 012-precedent-integration: T029 - Similar Precedents Panel */}
      <PrecedentPanel caseId={caseId} />

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-neutral-700">
        <nav className="flex gap-6">
          {[
            { id: 'evidence', label: '증거 자료', count: caseDetail.evidenceCount },
            { id: 'timeline', label: '타임라인', count: caseDetail.recentActivities.length },
            { id: 'members', label: '팀원', count: caseDetail.members.length },
            { id: 'relations', label: '관계도', count: null },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`
                pb-3 text-sm font-medium border-b-2 transition-colors
                ${activeTab === tab.id
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                }
              `}
            >
              {tab.label}
              {tab.count != null && tab.count > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-gray-100 dark:bg-neutral-700 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg p-6">
        {activeTab === 'evidence' && (
          <div>
            {caseDetail.evidenceCount > 0 ? (
              <div className="space-y-4">
                {caseDetail.evidenceSummary.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-neutral-700 rounded-lg"
                  >
                    <span className="font-medium">{item.type}</span>
                    <span className="text-[var(--color-text-secondary)]">{item.count}건</span>
                  </div>
                ))}
                <Link
                  href={detailPath}
                  className="inline-flex items-center gap-2 text-[var(--color-primary)] hover:underline"
                >
                  전체 증거 자료 보기
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            ) : (
              <p className="text-center text-[var(--color-text-secondary)] py-8">
                등록된 증거 자료가 없습니다.
              </p>
            )}
          </div>
        )}

        {activeTab === 'timeline' && (
          <div>
            {caseDetail.recentActivities.length > 0 ? (
              <div className="space-y-4">
                {caseDetail.recentActivities.map((activity, index) => (
                  <div key={index} className="flex gap-3">
                    <div className="w-2 h-2 mt-2 rounded-full bg-[var(--color-primary)]" />
                    <div>
                      <p className="text-[var(--color-text-primary)]">{activity.action}</p>
                      <p className="text-sm text-[var(--color-text-secondary)]">
                        {activity.user} - {new Date(activity.timestamp).toLocaleString('ko-KR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-[var(--color-text-secondary)] py-8">
                활동 기록이 없습니다.
              </p>
            )}
          </div>
        )}

        {activeTab === 'members' && (
          <div>
            {caseDetail.members.length > 0 ? (
              <div className="space-y-3">
                {caseDetail.members.map((member, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-neutral-700 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white text-sm font-medium">
                        {member.userName?.slice(0, 1) || '?'}
                      </div>
                      <span className="font-medium">{member.userName || member.userId}</span>
                    </div>
                    <span className="text-sm text-[var(--color-text-secondary)] capitalize">
                      {member.role}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-[var(--color-text-secondary)] py-8">
                팀원이 없습니다.
              </p>
            )}
          </div>
        )}

        {activeTab === 'relations' && (
          <div className="h-[600px]">
            <PartyGraph caseId={caseId} />
          </div>
        )}
      </div>

      {/* Summary Card Modal */}
      <ExplainerCard
        caseId={caseId}
        isOpen={showSummaryCard}
        onClose={() => setShowSummaryCard(false)}
        onShare={() => {
          setShowSummaryCard(false);
          setShowShareModal(true);
        }}
      />

      {/* Share Summary Modal */}
      <ShareSummaryModal
        caseId={caseId}
        caseTitle={caseDetail.title}
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
      />

      {/* Edit Case Modal */}
      <EditCaseModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        caseData={{
          id: caseDetail.id,
          title: caseDetail.title,
          clientName: caseDetail.clientName,
          description: caseDetail.description,
        }}
        onSuccess={(updatedCase: ApiCase) => {
          setCaseDetail((prev) =>
            prev
              ? {
                  ...prev,
                  title: updatedCase.title,
                  clientName: updatedCase.client_name,
                  description: updatedCase.description,
                  updatedAt: updatedCase.updated_at,
                }
              : null
          );
        }}
      />
    </div>
  );
}
