/**
 * Notifications API Client
 * 011-production-bug-fixes Feature - US2
 *
 * API functions for notification management.
 */

import { apiClient, ApiResponse } from './client';
import type {
  Notification,
  NotificationListResponse,
  NotificationQueryParams,
} from '@/types/notification';

const BASE_PATH = '/notifications';

/**
 * Get list of notifications for the current user
 */
export async function getNotifications(
  params?: NotificationQueryParams
): Promise<ApiResponse<NotificationListResponse>> {
  const searchParams = new URLSearchParams();

  if (params?.limit) {
    searchParams.append('limit', String(params.limit));
  }
  if (params?.unreadOnly) {
    searchParams.append('unread_only', 'true');
  }

  const queryString = searchParams.toString();
  const url = queryString ? `${BASE_PATH}?${queryString}` : BASE_PATH;

  return apiClient.get<NotificationListResponse>(url);
}

/**
 * Get unread notification count
 */
export async function getUnreadNotificationCount(): Promise<ApiResponse<{ count: number }>> {
  return apiClient.get<{ count: number }>(`${BASE_PATH}/unread-count`);
}

/**
 * Mark a single notification as read
 */
export async function markNotificationAsRead(
  notificationId: string
): Promise<ApiResponse<Notification>> {
  return apiClient.patch<Notification>(`${BASE_PATH}/${notificationId}/read`, {});
}

/**
 * Mark all notifications as read
 */
export async function markAllNotificationsAsRead(): Promise<ApiResponse<{ count: number }>> {
  return apiClient.post<{ count: number }>(`${BASE_PATH}/read-all`, {});
}

// Re-export types for convenience
export type { Notification, NotificationListResponse, NotificationQueryParams };
