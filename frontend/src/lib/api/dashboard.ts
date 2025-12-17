/**
 * Dashboard API Client
 * 007-lawyer-portal-v1 Feature - US7 (Today View)
 *
 * API functions for the Today View dashboard.
 */

import { apiClient } from './client';

// Types for Today View
export interface TodayItem {
  id: string;
  title: string;
  event_type: 'court' | 'meeting' | 'deadline' | 'internal' | 'other';
  start_time?: string;
  location?: string;
  case_id?: string;
  case_title?: string;
  description?: string;
}

export interface WeekItem {
  id: string;
  title: string;
  event_type: 'court' | 'meeting' | 'deadline' | 'internal' | 'other';
  start_date: string;
  start_time?: string;
  days_remaining: number;
  location?: string;
  case_id?: string;
  case_title?: string;
  description?: string;
}

export interface TodayViewResponse {
  date: string;
  urgent: TodayItem[];
  this_week: WeekItem[];
  all_complete: boolean;
}

/**
 * Get today's dashboard items
 * - urgent: Today's deadlines and court dates
 * - this_week: Items within 7 days
 */
export async function getTodayItems(): Promise<TodayViewResponse> {
  const response = await apiClient.get<TodayViewResponse>('/dashboard/today');
  if (!response.data) {
    throw new Error(response.error || '오늘의 일정을 불러오는데 실패했습니다.');
  }
  return response.data;
}

// Event type display helpers
export const EVENT_TYPE_LABELS: Record<string, string> = {
  court: '재판',
  meeting: '미팅',
  deadline: '마감',
  internal: '내부',
  other: '기타',
};

export const EVENT_TYPE_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  court: { bg: 'bg-red-50', border: 'border-red-500', text: 'text-red-700' },
  meeting: { bg: 'bg-blue-50', border: 'border-blue-500', text: 'text-blue-700' },
  deadline: { bg: 'bg-amber-50', border: 'border-amber-500', text: 'text-amber-700' },
  internal: { bg: 'bg-green-50', border: 'border-green-500', text: 'text-green-700' },
  other: { bg: 'bg-gray-50', border: 'border-gray-400', text: 'text-gray-700' },
};
