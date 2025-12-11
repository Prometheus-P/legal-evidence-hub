/**
 * useSettings Hook Tests
 * 005-lawyer-portal-pages Feature - US4 (T051)
 *
 * TDD: Write tests first, ensure they fail, then implement.
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useSettings } from '@/hooks/useSettings';
import * as settingsApi from '@/lib/api/settings';

// Mock the settings API
jest.mock('@/lib/api/settings', () => ({
  getProfile: jest.fn(),
  updateProfile: jest.fn(),
  getNotifications: jest.fn(),
  updateNotifications: jest.fn(),
}));

const mockProfile = {
  display_name: '홍길동',
  email: 'hong@example.com',
  phone: '010-1234-5678',
  avatar_url: null,
  timezone: 'Asia/Seoul',
  language: 'ko',
  role: 'lawyer',
  created_at: '2024-01-01T00:00:00Z',
};

const mockNotifications = {
  email_enabled: true,
  push_enabled: false,
  frequency: 'daily' as const,
  notification_types: {
    new_evidence: true,
    case_updates: true,
    messages: true,
    calendar_reminders: true,
    billing_alerts: false,
  },
};

describe('useSettings', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Profile Loading', () => {
    it('should start in loading state', () => {
      (settingsApi.getProfile as jest.Mock).mockReturnValue(new Promise(() => {}));
      (settingsApi.getNotifications as jest.Mock).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useSettings());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.profile).toBeNull();
    });

    it('should load profile successfully', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.profile).toEqual(mockProfile);
      expect(result.current.error).toBeNull();
    });

    it('should handle profile load error', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: null,
        error: '프로필을 불러올 수 없습니다.',
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: null,
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.profile).toBeNull();
      expect(result.current.error).toBe('프로필을 불러올 수 없습니다.');
    });
  });

  describe('Profile Update', () => {
    it('should update profile successfully', async () => {
      const updatedProfile = { ...mockProfile, display_name: '김철수' };

      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });
      (settingsApi.updateProfile as jest.Mock).mockResolvedValue({
        data: { message: '프로필이 업데이트되었습니다.', profile: updatedProfile },
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let success: boolean | undefined;
      await act(async () => {
        success = await result.current.updateProfile({ display_name: '김철수' });
      });

      expect(success).toBe(true);
      expect(result.current.profile?.display_name).toBe('김철수');
      expect(settingsApi.updateProfile).toHaveBeenCalledWith({ display_name: '김철수' });
    });

    it('should handle profile update error', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });
      (settingsApi.updateProfile as jest.Mock).mockResolvedValue({
        data: null,
        error: '업데이트 실패',
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let success: boolean | undefined;
      await act(async () => {
        success = await result.current.updateProfile({ display_name: '김철수' });
      });

      expect(success).toBe(false);
      expect(result.current.error).toBe('업데이트 실패');
    });
  });

  describe('Notifications Loading', () => {
    it('should load notifications successfully', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.notifications).toEqual(mockNotifications);
    });
  });

  describe('Notifications Update', () => {
    it('should update notifications successfully', async () => {
      const updatedNotifications = { ...mockNotifications, email_enabled: false };

      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });
      (settingsApi.updateNotifications as jest.Mock).mockResolvedValue({
        data: { message: '알림 설정이 업데이트되었습니다.' },
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let success: boolean | undefined;
      await act(async () => {
        success = await result.current.updateNotifications({ email_enabled: false });
      });

      expect(success).toBe(true);
      expect(settingsApi.updateNotifications).toHaveBeenCalledWith({ email_enabled: false });
    });

    it('should handle notifications update error', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });
      (settingsApi.updateNotifications as jest.Mock).mockResolvedValue({
        data: null,
        error: '알림 설정 업데이트 실패',
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let success: boolean | undefined;
      await act(async () => {
        success = await result.current.updateNotifications({ email_enabled: false });
      });

      expect(success).toBe(false);
      expect(result.current.error).toBe('알림 설정 업데이트 실패');
    });
  });

  describe('Refetch', () => {
    it('should refetch data when called', async () => {
      (settingsApi.getProfile as jest.Mock).mockResolvedValue({
        data: mockProfile,
        error: null,
      });
      (settingsApi.getNotifications as jest.Mock).mockResolvedValue({
        data: mockNotifications,
        error: null,
      });

      const { result } = renderHook(() => useSettings());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(settingsApi.getProfile).toHaveBeenCalledTimes(1);

      await act(async () => {
        await result.current.refetch();
      });

      expect(settingsApi.getProfile).toHaveBeenCalledTimes(2);
    });
  });
});
