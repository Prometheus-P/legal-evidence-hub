/**
 * AI Recommendation Card Component
 * 009-calm-control-design-system
 *
 * Displays AI-suggested tasks for the lawyer
 * Following calm-control principle: AI suggestions are always preview-only, manual trigger
 */

'use client';

import Link from 'next/link';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';

export interface AIRecommendation {
  id: string;
  type: 'draft_review' | 'evidence_tagging' | 'asset_incomplete' | 'deadline_reminder' | 'document_analysis';
  caseId: string;
  caseTitle: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  createdAt: string;
}

interface AIRecommendationCardProps {
  recommendations: AIRecommendation[];
  isLoading?: boolean;
}

const typeConfig: Record<string, { label: string; icon: string; action: string }> = {
  draft_review: { label: '초안 검토', icon: '📝', action: '검토하기' },
  evidence_tagging: { label: '증거 태깅', icon: '🏷️', action: '태깅하기' },
  asset_incomplete: { label: '재산정보 미기입', icon: '💰', action: '입력하기' },
  deadline_reminder: { label: '기일 알림', icon: '📅', action: '확인하기' },
  document_analysis: { label: '문서 분석', icon: '📄', action: '분석하기' },
};

const priorityStyles: Record<string, string> = {
  high: 'border-l-warning',
  medium: 'border-l-info',
  low: 'border-l-neutral-300',
};

function RecommendationItem({ item }: { item: AIRecommendation }) {
  const config = typeConfig[item.type] || { label: '작업', icon: '📋', action: '처리하기' };

  // Determine the correct link based on type
  const getActionLink = () => {
    switch (item.type) {
      case 'draft_review':
        return getCaseDetailPath('lawyer', item.caseId, { tab: 'draft' });
      case 'evidence_tagging':
        return getCaseDetailPath('lawyer', item.caseId, { tab: 'evidence' });
      case 'asset_incomplete':
        return getLawyerCasePath('assets', item.caseId);
      default:
        return getCaseDetailPath('lawyer', item.caseId);
    }
  };

  return (
    <div className={`group p-3 rounded-lg hover:bg-neutral-50 transition-colors border-l-4 ${priorityStyles[item.priority]}`}>
      <div className="flex items-start gap-3">
        <span className="text-lg flex-shrink-0" role="img" aria-label={config.label}>
          {config.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-info-light text-info">
              AI 제안
            </span>
            <span className="text-xs text-neutral-400">{config.label}</span>
          </div>
          <p className="font-medium text-neutral-800 truncate mt-1">
            {item.caseTitle}
          </p>
          <p className="text-sm text-neutral-500 line-clamp-2 mt-0.5">
            {item.description}
          </p>
          <Link
            href={getActionLink()}
            className="inline-flex items-center gap-1 text-sm text-primary hover:text-primary-hover mt-2"
          >
            {config.action}
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}

export function AIRecommendationCard({ recommendations, isLoading }: AIRecommendationCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-neutral-200">
        <div className="p-4 border-b border-neutral-200">
          <div className="flex items-center gap-2">
            <span className="text-lg">🤖</span>
            <h2 className="font-semibold text-neutral-800">AI 추천 작업</h2>
          </div>
        </div>
        <div className="p-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse flex gap-3">
              <div className="w-6 h-6 bg-neutral-200 rounded" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-neutral-200 rounded w-3/4" />
                <div className="h-3 bg-neutral-100 rounded w-full" />
                <div className="h-3 bg-neutral-100 rounded w-1/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-neutral-200">
      <div className="p-4 border-b border-neutral-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🤖</span>
            <h2 className="font-semibold text-neutral-800">AI 추천 작업</h2>
          </div>
          <span className="text-xs text-neutral-400 italic">미리보기 전용</span>
        </div>
        <p className="text-xs text-neutral-500 mt-1">
          AI가 분석한 우선 처리 작업입니다. 모든 작업은 수동 검토 후 진행됩니다.
        </p>
      </div>
      <div className="p-2">
        {recommendations.length > 0 ? (
          <div className="space-y-2">
            {recommendations.slice(0, 5).map((item) => (
              <RecommendationItem key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <span className="text-3xl mb-2 block">👍</span>
            <p className="text-neutral-500 text-sm">현재 추천 작업이 없습니다</p>
          </div>
        )}
      </div>
    </div>
  );
}
