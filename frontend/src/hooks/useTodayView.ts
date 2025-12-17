/**
 * useTodayView Hook
 * 007-lawyer-portal-v1 Feature - US7 (Today View)
 *
 * Hook for fetching and managing today's dashboard data.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getTodayItems,
  TodayViewResponse,
  TodayItem,
  WeekItem,
} from '@/lib/api/dashboard';

export interface UseTodayViewResult {
  /** Today's date */
  date: string | null;
  /** Today's urgent items (deadlines, court dates) */
  urgent: TodayItem[];
  /** This week's upcoming items */
  thisWeek: WeekItem[];
  /** Whether all urgent items are complete */
  allComplete: boolean;
  /** Loading state */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Refresh data */
  refresh: () => Promise<void>;
}

/**
 * useTodayView - Fetch and manage today's dashboard items
 *
 * Usage:
 * ```tsx
 * const { urgent, thisWeek, allComplete, isLoading, error } = useTodayView();
 *
 * if (isLoading) return <Loading />;
 * if (error) return <Error message={error} />;
 *
 * return (
 *   <>
 *     <TodayCard items={urgent} allComplete={allComplete} />
 *     <WeeklyPreview items={thisWeek} />
 *   </>
 * );
 * ```
 */
export function useTodayView(): UseTodayViewResult {
  const [data, setData] = useState<TodayViewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTodayItems = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await getTodayItems();
      setData(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : '오늘의 일정을 불러오는데 실패했습니다.'
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodayItems();
  }, [fetchTodayItems]);

  return {
    date: data?.date ?? null,
    urgent: data?.urgent ?? [],
    thisWeek: data?.this_week ?? [],
    allComplete: data?.all_complete ?? true,
    isLoading,
    error,
    refresh: fetchTodayItems,
  };
}

export default useTodayView;
