/**
 * Notification Types for Lawyer Portal
 * 011-production-bug-fixes Feature - US2
 */

// ============== Notification Types ==============

export type NotificationType = 'case_update' | 'message' | 'system';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  content: string;
  isRead: boolean;
  relatedId?: string;
  createdAt: string; // ISO 8601
}

export interface NotificationListResponse {
  notifications: Notification[];
  unreadCount: number;
}

export interface NotificationQueryParams {
  limit?: number;
  unreadOnly?: boolean;
}

// ============== Notification State ==============

export interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}

// ============== Notification Actions ==============

export interface MarkAsReadRequest {
  notificationId: string;
}

export interface MarkAllAsReadRequest {
  // Empty - marks all notifications as read
}
