/**
 * TodayCard Component
 * 007-lawyer-portal-v1 Feature - US7 (Today View)
 *
 * Displays today's urgent items (court dates, deadlines).
 */

'use client';

import Link from 'next/link';
import { TodayItem, EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from '@/lib/api/dashboard';
import { getCaseDetailPath } from '@/lib/portalPaths';

interface TodayCardProps {
  items: TodayItem[];
  allComplete: boolean;
  isLoading?: boolean;
}

// Icon components
const AlertIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
    />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

const ClockIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

const LocationIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
    />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

function UrgentItem({ item }: { item: TodayItem }) {
  const colors = EVENT_TYPE_COLORS[item.event_type] || EVENT_TYPE_COLORS.other;
  const label = EVENT_TYPE_LABELS[item.event_type] || item.event_type;

  return (
    <div className={`p-3 rounded-lg border-l-4 ${colors.bg} ${colors.border}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${colors.text} ${colors.bg}`}>
              {label}
            </span>
            {item.start_time && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <ClockIcon />
                {item.start_time}
              </span>
            )}
          </div>
          <p className="mt-1 font-medium text-gray-900 truncate">{item.title}</p>
          {item.location && (
            <p className="flex items-center gap-1 mt-1 text-xs text-gray-500">
              <LocationIcon />
              {item.location}
            </p>
          )}
        </div>
        {item.case_id && (
          <Link
            href={getCaseDetailPath('lawyer', item.case_id)}
            className="text-xs text-blue-600 hover:underline whitespace-nowrap"
          >
            {item.case_title || '케이스 보기'}
          </Link>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-3">
        <CheckCircleIcon />
      </div>
      <p className="text-gray-900 font-medium">오늘 일정이 모두 완료되었습니다!</p>
      <p className="text-sm text-gray-500 mt-1">편안한 하루 보내세요.</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      {[1, 2].map((i) => (
        <div key={i} className="p-3 rounded-lg bg-gray-100">
          <div className="h-4 w-16 bg-gray-200 rounded mb-2" />
          <div className="h-5 w-3/4 bg-gray-200 rounded" />
        </div>
      ))}
    </div>
  );
}

export function TodayCard({ items, allComplete, isLoading }: TodayCardProps) {
  const urgentCount = items.length;
  const hasUrgent = urgentCount > 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className={`px-4 py-3 border-b ${hasUrgent ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {hasUrgent ? (
              <span className="text-red-600"><AlertIcon /></span>
            ) : (
              <span className="text-green-600"><CheckCircleIcon /></span>
            )}
            <h2 className="font-semibold text-gray-900">오늘의 일정</h2>
          </div>
          {hasUrgent && (
            <span className="text-xs font-medium text-red-600 bg-red-100 px-2 py-1 rounded-full">
              {urgentCount}건 긴급
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {isLoading ? (
          <LoadingSkeleton />
        ) : allComplete && !hasUrgent ? (
          <EmptyState />
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <UrgentItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default TodayCard;
