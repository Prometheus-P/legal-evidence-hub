/**
 * Settings API Client
 * 005-lawyer-portal-pages Feature - US4
 *
 * API functions for user settings management.
 */

import { apiClient, ApiResponse } from './client';
import {
  UserProfile,
  ProfileUpdateRequest,
  NotificationSettings,
  NotificationUpdateRequest,
  SecuritySettings,
  PasswordChangeRequest,
  UserSettingsResponse,
} from '@/types/settings';

/**
 * Get user profile settings
 */
export async function getProfile(): Promise<ApiResponse<UserProfile>> {
  return apiClient.get<UserProfile>('/settings/profile');
}

/**
 * Update user profile settings
 */
export async function updateProfile(
  data: ProfileUpdateRequest
): Promise<ApiResponse<{ message: string; profile: UserProfile }>> {
  return apiClient.put<{ message: string; profile: UserProfile }>(
    '/settings/profile',
    data
  );
}

/**
 * Get notification preferences
 */
export async function getNotifications(): Promise<ApiResponse<NotificationSettings>> {
  return apiClient.get<NotificationSettings>('/settings/notifications');
}

/**
 * Update notification preferences
 */
export async function updateNotifications(
  data: NotificationUpdateRequest
): Promise<ApiResponse<{ message: string }>> {
  return apiClient.put<{ message: string }>('/settings/notifications', data);
}

/**
 * Get security settings
 */
export async function getSecuritySettings(): Promise<ApiResponse<SecuritySettings>> {
  return apiClient.get<SecuritySettings>('/settings/security');
}

/**
 * Change user password
 */
export async function changePassword(
  data: PasswordChangeRequest
): Promise<ApiResponse<{ message: string }>> {
  return apiClient.post<{ message: string }>('/settings/security/change-password', data);
}

/**
 * Get all user settings at once
 */
export async function getAllSettings(): Promise<ApiResponse<UserSettingsResponse>> {
  return apiClient.get<UserSettingsResponse>('/settings');
}

// Re-export types for convenience
export type {
  UserProfile,
  ProfileUpdateRequest,
  NotificationSettings,
  NotificationUpdateRequest,
  SecuritySettings,
  PasswordChangeRequest,
  UserSettingsResponse,
};
