'use client';

/**
 * ContextPanel - Right Panel Context Components
 * 014-ui-settings-completion Feature
 *
 * Context panel containing:
 * - Timeline mini view (recent events)
 * - Relations mini view (party count)
 * - Asset summary (total values)
 * - Quick links to full-screen views
 */

import { ReactNode } from 'react';
import { Clock, Users, Wallet, ExternalLink, Activity } from 'lucide-react';

interface ContextCardProps {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  onViewMore?: () => void;
  viewMoreLabel?: string;
}

function ContextCard({
  title,
  icon,
  children,
  onViewMore,
  viewMoreLabel = '전체 보기',
}: ContextCardProps) {
  return (
    <div className="border-b border-gray-200 dark:border-neutral-700 last:border-b-0">
      <div className="px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[var(--color-text-secondary)]">{icon}</span>
            <h4 className="text-sm font-medium text-[var(--color-text-primary)]">{title}</h4>
          </div>
          {onViewMore && (
            <button
              onClick={onViewMore}
              className="text-xs text-[var(--color-primary)] hover:underline flex items-center gap-1"
            >
              {viewMoreLabel}
              <ExternalLink className="w-3 h-3" />
            </button>
          )}
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}

// Timeline Mini View
interface TimelineEvent {
  id: string;
  action: string;
  timestamp: string;
  user?: string;
}

interface TimelineMiniProps {
  events: TimelineEvent[];
  onViewMore?: () => void;
}

export function TimelineMini({ events, onViewMore }: TimelineMiniProps) {
  const recentEvents = events.slice(0, 5);

  return (
    <ContextCard
      title="최근 활동"
      icon={<Clock className="w-4 h-4" />}
      onViewMore={onViewMore}
      viewMoreLabel="타임라인"
    >
      {recentEvents.length === 0 ? (
        <p className="text-xs text-[var(--color-text-secondary)]">활동 기록이 없습니다.</p>
      ) : (
        <ul className="space-y-2">
          {recentEvents.map((event) => (
            <li key={event.id} className="flex items-start gap-2">
              <Activity className="w-3 h-3 mt-0.5 text-[var(--color-text-secondary)]" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-[var(--color-text-primary)] truncate">{event.action}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  {new Date(event.timestamp).toLocaleDateString('ko-KR', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </ContextCard>
  );
}

// Relations Mini View
interface RelationsMiniProps {
  partyCount: number;
  relationCount: number;
  onViewMore?: () => void;
}

export function RelationsMini({ partyCount, relationCount, onViewMore }: RelationsMiniProps) {
  return (
    <ContextCard
      title="인물 관계"
      icon={<Users className="w-4 h-4" />}
      onViewMore={onViewMore}
      viewMoreLabel="관계도"
    >
      <div className="flex gap-4">
        <div className="text-center">
          <p className="text-lg font-bold text-[var(--color-primary)]">{partyCount}</p>
          <p className="text-xs text-[var(--color-text-secondary)]">인물</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-bold text-[var(--color-text-primary)]">{relationCount}</p>
          <p className="text-xs text-[var(--color-text-secondary)]">관계</p>
        </div>
      </div>
    </ContextCard>
  );
}

// Asset Summary Mini View
interface AssetSummary {
  totalAssets: number;
  totalLiabilities: number;
  netWorth: number;
  plaintiffRatio?: string;
  defendantRatio?: string;
}

interface AssetSummaryMiniProps {
  summary: AssetSummary;
  onViewMore?: () => void;
}

export function AssetSummaryMini({ summary, onViewMore }: AssetSummaryMiniProps) {
  const formatCurrency = (value: number) => {
    if (value >= 100000000) {
      return `${(value / 100000000).toFixed(1)}억`;
    } else if (value >= 10000) {
      return `${(value / 10000).toFixed(0)}만`;
    }
    return value.toLocaleString();
  };

  return (
    <ContextCard
      title="재산 현황"
      icon={<Wallet className="w-4 h-4" />}
      onViewMore={onViewMore}
      viewMoreLabel="재산 상세"
    >
      <div className="space-y-2">
        <div className="flex justify-between text-xs">
          <span className="text-[var(--color-text-secondary)]">총 자산</span>
          <span className="text-[var(--color-text-primary)] font-medium">
            {formatCurrency(summary.totalAssets)}원
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-[var(--color-text-secondary)]">총 부채</span>
          <span className="text-red-500 font-medium">
            -{formatCurrency(summary.totalLiabilities)}원
          </span>
        </div>
        <div className="pt-2 border-t border-gray-200 dark:border-neutral-700">
          <div className="flex justify-between text-xs">
            <span className="text-[var(--color-text-secondary)]">순재산</span>
            <span className={`font-bold ${summary.netWorth >= 0 ? 'text-green-600' : 'text-red-500'}`}>
              {formatCurrency(summary.netWorth)}원
            </span>
          </div>
        </div>
        {(summary.plaintiffRatio || summary.defendantRatio) && (
          <div className="pt-2 border-t border-gray-200 dark:border-neutral-700">
            <p className="text-xs text-[var(--color-text-secondary)] mb-1">예상 분할 비율</p>
            <div className="flex gap-2 text-xs">
              <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
                원고 {summary.plaintiffRatio || '-'}
              </span>
              <span className="px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded">
                피고 {summary.defendantRatio || '-'}
              </span>
            </div>
          </div>
        )}
      </div>
    </ContextCard>
  );
}

// Main ContextPanel Component
interface ContextPanelProps {
  // Timeline
  timelineEvents?: TimelineEvent[];
  onViewTimeline?: () => void;
  // Relations
  partyCount?: number;
  relationCount?: number;
  onViewRelations?: () => void;
  // Assets
  assetSummary?: AssetSummary;
  onViewAssets?: () => void;
}

export function ContextPanel({
  timelineEvents = [],
  onViewTimeline,
  partyCount = 0,
  relationCount = 0,
  onViewRelations,
  assetSummary,
  onViewAssets,
}: ContextPanelProps) {
  return (
    <div>
      {/* Timeline Mini */}
      <TimelineMini events={timelineEvents} onViewMore={onViewTimeline} />

      {/* Relations Mini */}
      <RelationsMini
        partyCount={partyCount}
        relationCount={relationCount}
        onViewMore={onViewRelations}
      />

      {/* Asset Summary Mini */}
      {assetSummary && (
        <AssetSummaryMini summary={assetSummary} onViewMore={onViewAssets} />
      )}
    </div>
  );
}

export default ContextPanel;
