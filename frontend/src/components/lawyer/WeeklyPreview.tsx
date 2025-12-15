/**
 * WeeklyPreview Component
 * 007-lawyer-portal-v1 Feature - US7 (Today View)
 *
 * Displays this week's upcoming items with D-N countdown.
 */

'use client';

import Link from 'next/link';
import { WeekItem as WeekItemType, EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from '@/lib/api/dashboard';
import { getCaseDetailPath } from '@/lib/portalPaths';

interface WeeklyPreviewProps {
  items: WeekItemType[];
  isLoading?: boolean;
}

// Icon components
const CalendarIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
    />
  </svg>
);

const ChevronRightIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

function getDayLabel(daysRemaining: number): string {
  if (daysRemaining === 1) return '내일';
  if (daysRemaining === 2) return '모레';
  return `D-${daysRemaining}`;
}

function getDayColor(daysRemaining: number): string {
  if (daysRemaining <= 1) return 'bg-red-500 text-white';
  if (daysRemaining <= 3) return 'bg-amber-500 text-white';
  return 'bg-blue-500 text-white';
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
    weekday: 'short',
  });
}

function WeekItem({ item }: { item: WeekItemType }) {
  const colors = EVENT_TYPE_COLORS[item.event_type] || EVENT_TYPE_COLORS.other;
  const label = EVENT_TYPE_LABELS[item.event_type] || item.event_type;
  const dayLabel = getDayLabel(item.days_remaining);
  const dayColor = getDayColor(item.days_remaining);

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-[var(--color-bg-secondary)] transition-colors group">
      {/* D-N Badge */}
      <div className={`flex-shrink-0 w-12 h-12 rounded-lg flex flex-col items-center justify-center ${dayColor}`}>
        <span className="text-xs font-medium">{dayLabel}</span>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium px-2 py-0.5 rounded ${colors.text} ${colors.bg}`}>
            {label}
          </span>
          <span className="text-xs text-[var(--color-text-tertiary)]">{formatDate(item.start_date)}</span>
          {item.start_time && (
            <span className="text-xs text-[var(--color-text-tertiary)]">{item.start_time}</span>
          )}
        </div>
        <p className="mt-1 font-medium text-[var(--color-text-primary)] truncate">{item.title}</p>
        {item.case_title && (
          <p className="text-xs text-[var(--color-text-secondary)] truncate">{item.case_title}</p>
        )}
      </div>

      {/* Link Arrow */}
      {item.case_id && (
            <Link
              href={getCaseDetailPath('lawyer', item.case_id)}
          className="flex-shrink-0 text-[var(--color-text-tertiary)] group-hover:text-[var(--color-primary)] transition-colors"
        >
          <ChevronRightIcon />
        </Link>
      )}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <div className="w-12 h-12 rounded-full bg-[var(--color-bg-secondary)] flex items-center justify-center mb-3">
        <CalendarIcon />
      </div>
      <p className="text-[var(--color-text-secondary)]">이번 주 예정된 일정이 없습니다.</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center gap-3 p-3">
          <div className="w-12 h-12 bg-[var(--color-bg-tertiary)] rounded-lg" />
          <div className="flex-1">
            <div className="h-4 w-20 bg-[var(--color-bg-tertiary)] rounded mb-2" />
            <div className="h-5 w-3/4 bg-[var(--color-bg-tertiary)] rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function WeeklyPreview({ items, isLoading }: WeeklyPreviewProps) {
  return (
    <div className="bg-[var(--color-bg-primary)] rounded-xl shadow-[var(--shadow-sm)] border border-[var(--color-border-default)] overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[var(--color-border-default)] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[var(--color-primary)]"><CalendarIcon /></span>
          <h2 className="font-semibold text-[var(--color-text-primary)]">이번 주 일정</h2>
        </div>
        <Link
          href="/lawyer/calendar"
          className="text-sm text-[var(--color-primary)] hover:underline"
        >
          캘린더
        </Link>
      </div>

      {/* Content */}
      <div className="p-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : items.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-1">
            {items.map((item) => (
              <WeekItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default WeeklyPreview;
