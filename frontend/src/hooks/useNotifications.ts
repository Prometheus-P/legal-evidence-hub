/**
 * useNotifications Hook
 * 011-production-bug-fixes Feature - US2 (T035)
 *
 * Hook for notification management with polling.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  getNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
} from '@/lib/api/notifications';
import type {
  Notification,
  NotificationQueryParams,
} from '@/types/notification';

interface UseNotificationsOptions {
  limit?: number;
  pollingInterval?: number; // in milliseconds, default 5 minutes
  autoFetch?: boolean;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  markAsRead: (notificationId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refetch: () => Promise<void>;
}

const DEFAULT_POLLING_INTERVAL = 5 * 60 * 1000; // 5 minutes

export function useNotifications(
  options: UseNotificationsOptions = {}
): UseNotificationsReturn {
  const {
    limit = 10,
    pollingInterval = DEFAULT_POLLING_INTERVAL,
    autoFetch = true,
  } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const fetchNotifications = useCallback(async () => {
    setError(null);

    try {
      const params: NotificationQueryParams = { limit };
      const response = await getNotifications(params);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setNotifications(response.data.notifications || []);
        setUnreadCount(response.data.unreadCount ?? 0);
      }
    } catch {
      setError('알림을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  // Mark single notification as read
  const markAsRead = useCallback(async (notificationId: string) => {
    try {
      const response = await markNotificationAsRead(notificationId);

      if (response.error) {
        setError(response.error);
        return;
      }

      // Update local state
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId ? { ...n, isRead: true } : n
        )
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {
      setError('알림 읽음 처리 중 오류가 발생했습니다.');
    }
  }, []);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    try {
      const response = await markAllNotificationsAsRead();

      if (response.error) {
        setError(response.error);
        return;
      }

      // Update local state
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, isRead: true }))
      );
      setUnreadCount(0);
    } catch {
      setError('알림 읽음 처리 중 오류가 발생했습니다.');
    }
  }, []);

  // Initial fetch and polling setup
  useEffect(() => {
    if (autoFetch) {
      fetchNotifications();

      // Setup polling
      if (pollingInterval > 0) {
        pollingRef.current = setInterval(fetchNotifications, pollingInterval);
      }
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [fetchNotifications, pollingInterval, autoFetch]);

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    refetch: fetchNotifications,
  };
}

export default useNotifications;
