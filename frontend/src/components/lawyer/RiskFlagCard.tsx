/**
 * Risk Flag Card Component
 * 009-calm-control-design-system
 *
 * Displays high-risk cases with subtle visual emphasis
 * Following calm-control principle: no screaming colors, use icon + subtle border + placement
 */

'use client';

import Link from 'next/link';

export interface RiskCase {
  id: string;
  title: string;
  clientName: string;
  riskType: 'violence' | 'child' | 'flight' | 'evidence_tampering' | 'urgent_deadline';
  flaggedAt: string;
  description?: string;
}

interface RiskFlagCardProps {
  cases: RiskCase[];
  isLoading?: boolean;
}

const riskTypeConfig: Record<string, { label: string; icon: string }> = {
  violence: { label: '폭력 위험', icon: '⚠️' },
  child: { label: '아동 관련', icon: '👶' },
  flight: { label: '도주 위험', icon: '🚨' },
  evidence_tampering: { label: '증거 인멸', icon: '📋' },
  urgent_deadline: { label: '긴급 기일', icon: '⏰' },
};

function RiskCaseItem({ caseItem }: { caseItem: RiskCase }) {
  const config = riskTypeConfig[caseItem.riskType] || { label: '위험', icon: '⚠️' };

  return (
    <Link
      href={`/lawyer/cases/${caseItem.id}`}
      className="group flex items-start gap-3 p-3 rounded-lg hover:bg-neutral-50 transition-colors border-l-4 border-error-light hover:border-error"
    >
      <span className="text-lg flex-shrink-0" role="img" aria-label={config.label}>
        {config.icon}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-neutral-800 truncate group-hover:text-primary">
            {caseItem.title}
          </p>
          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-error-light text-error">
            {config.label}
          </span>
        </div>
        <p className="text-sm text-neutral-500 truncate">{caseItem.clientName}</p>
        {caseItem.description && (
          <p className="text-xs text-neutral-400 mt-1 line-clamp-1">{caseItem.description}</p>
        )}
      </div>
    </Link>
  );
}

export function RiskFlagCard({ cases, isLoading }: RiskFlagCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-neutral-200">
        <div className="p-4 border-b border-neutral-200">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚠️</span>
            <h2 className="font-semibold text-neutral-800">위험 플래그 사건</h2>
          </div>
        </div>
        <div className="p-4 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse flex gap-3">
              <div className="w-6 h-6 bg-neutral-200 rounded" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-neutral-200 rounded w-3/4" />
                <div className="h-3 bg-neutral-100 rounded w-1/2" />
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
            <span className="text-lg">⚠️</span>
            <h2 className="font-semibold text-neutral-800">위험 플래그 사건</h2>
            {cases.length > 0 && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-error-light text-error">
                {cases.length}건
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="p-2">
        {cases.length > 0 ? (
          <div className="space-y-1">
            {cases.slice(0, 5).map((caseItem) => (
              <RiskCaseItem key={caseItem.id} caseItem={caseItem} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <span className="text-3xl mb-2 block">✅</span>
            <p className="text-neutral-500 text-sm">위험 플래그 사건이 없습니다</p>
          </div>
        )}
      </div>
    </div>
  );
}
