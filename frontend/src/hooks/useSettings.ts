/**
 * useSettings Hook
 * 005-lawyer-portal-pages Feature - US4 (T052)
 *
 * Hook for user settings management (profile, notifications, and security).
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getProfile,
  updateProfile as updateProfileApi,
  getNotifications,
  updateNotifications as updateNotificationsApi,
  getSecuritySettings,
  changePassword as changePasswordApi,
} from '@/lib/api/settings';
import type {
  UserProfile,
  ProfileUpdateRequest,
  NotificationSettings,
  NotificationUpdateRequest,
  SecuritySettings,
  PasswordChangeRequest,
} from '@/types/settings';

interface UseSettingsOptions {
  autoFetch?: boolean;
}

interface UseSettingsReturn {
  profile: UserProfile | null;
  notifications: NotificationSettings | null;
  security: SecuritySettings | null;
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;
  updateProfile: (data: ProfileUpdateRequest) => Promise<boolean>;
  updateNotifications: (data: NotificationUpdateRequest) => Promise<boolean>;
  changePassword: (data: PasswordChangeRequest) => Promise<boolean>;
  fetchSecuritySettings: () => Promise<void>;
  refetch: () => Promise<void>;
}

export function useSettings(options: UseSettingsOptions = {}): UseSettingsReturn {
  const { autoFetch = true } = options;

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [notifications, setNotifications] = useState<NotificationSettings | null>(null);
  const [security, setSecurity] = useState<SecuritySettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch profile and notifications in parallel
      const [profileResponse, notificationsResponse] = await Promise.all([
        getProfile(),
        getNotifications(),
      ]);

      if (profileResponse.error) {
        setError(profileResponse.error);
        setProfile(null);
      } else if (profileResponse.data) {
        setProfile(profileResponse.data);
      }

      if (notificationsResponse.error && !error) {
        // Only set error if profile didn't already fail
        setError(notificationsResponse.error);
      } else if (notificationsResponse.data) {
        setNotifications(notificationsResponse.data);
      }
    } catch {
      setError('설정을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (autoFetch) {
      fetchSettings();
    }
  }, [fetchSettings, autoFetch]);

  const updateProfile = useCallback(
    async (data: ProfileUpdateRequest): Promise<boolean> => {
      setIsUpdating(true);
      setError(null);

      try {
        const { data: response, error: apiError } = await updateProfileApi(data);

        if (apiError) {
          setError(apiError);
          return false;
        }

        if (response?.profile) {
          setProfile(response.profile);
        }

        return true;
      } catch {
        setError('프로필 업데이트 중 오류가 발생했습니다.');
        return false;
      } finally {
        setIsUpdating(false);
      }
    },
    []
  );

  const updateNotifications = useCallback(
    async (data: NotificationUpdateRequest): Promise<boolean> => {
      setIsUpdating(true);
      setError(null);

      try {
        const { error: apiError } = await updateNotificationsApi(data);

        if (apiError) {
          setError(apiError);
          return false;
        }

        // Optimistic update
        setNotifications((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            ...data,
            notification_types: {
              ...prev.notification_types,
              ...(data.notification_types || {}),
            },
          };
        });

        return true;
      } catch {
        setError('알림 설정 업데이트 중 오류가 발생했습니다.');
        return false;
      } finally {
        setIsUpdating(false);
      }
    },
    []
  );

  const fetchSecuritySettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await getSecuritySettings();

      if (response.error) {
        setError(response.error);
        setSecurity(null);
      } else if (response.data) {
        setSecurity(response.data);
      }
    } catch {
      setError('보안 설정을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const changePassword = useCallback(
    async (data: PasswordChangeRequest): Promise<boolean> => {
      setIsUpdating(true);
      setError(null);

      try {
        const { error: apiError } = await changePasswordApi(data);

        if (apiError) {
          setError(apiError);
          return false;
        }

        // Update last password change date
        setSecurity((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            last_password_change: new Date().toISOString(),
          };
        });

        return true;
      } catch {
        setError('비밀번호 변경 중 오류가 발생했습니다.');
        return false;
      } finally {
        setIsUpdating(false);
      }
    },
    []
  );

  return {
    profile,
    notifications,
    security,
    isLoading,
    isUpdating,
    error,
    updateProfile,
    updateNotifications,
    changePassword,
    fetchSecuritySettings,
    refetch: fetchSettings,
  };
}
