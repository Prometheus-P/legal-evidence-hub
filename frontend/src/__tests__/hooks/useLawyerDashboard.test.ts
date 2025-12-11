/**
 * useLawyerDashboard Hook Tests
 * 003-role-based-ui Feature - US2
 *
 * Tests for lawyer dashboard data fetching hook.
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useLawyerDashboard } from '@/hooks/useLawyerDashboard';
import * as lawyerApi from '@/lib/api/lawyer';

// Mock the lawyer API
jest.mock('@/lib/api/lawyer', () => ({
  getLawyerDashboard: jest.fn(),
  getLawyerAnalytics: jest.fn(),
}));

const mockDashboard = {
  stats: {
    total_cases: 15,
    active_cases: 8,
    pending_evidence: 12,
    upcoming_deadlines: 3,
  },
  recent_cases: [
    {
      id: 'case-1',
      title: '이혼 소송 - 홍길동',
      status: 'in_progress',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-10T00:00:00Z',
    },
  ],
  upcoming_events: [
    {
      id: 'event-1',
      title: '재판 기일',
      event_type: 'court',
      start_time: '2024-02-01T10:00:00Z',
    },
  ],
  recent_activities: [
    {
      id: 'activity-1',
      action: '증거 업로드',
      target: '이혼 소송 - 홍길동',
      created_at: '2024-01-10T00:00:00Z',
    },
  ],
};

const mockAnalytics = {
  cases_by_status: {
    open: 5,
    in_progress: 8,
    closed: 20,
  },
  cases_by_month: [
    { month: '2024-01', count: 3 },
    { month: '2024-02', count: 5 },
  ],
  evidence_by_type: {
    image: 50,
    audio: 20,
    video: 10,
    text: 30,
    pdf: 25,
  },
  average_case_duration: 45,
};

describe('useLawyerDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress console.error for expected errors
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    (console.error as jest.Mock).mockRestore();
  });

  describe('Initial Loading', () => {
    it('should start in loading state', () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockReturnValue(new Promise(() => {}));
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useLawyerDashboard());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.dashboard).toBeNull();
      expect(result.current.analytics).toBeNull();
    });

    it('should load dashboard data successfully', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: mockDashboard,
        error: null,
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.dashboard).toEqual(mockDashboard);
      expect(result.current.data).toEqual(mockDashboard); // alias
      expect(result.current.analytics).toEqual(mockAnalytics);
      expect(result.current.error).toBeNull();
    });

    it('should handle dashboard load error', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: null,
        error: '대시보드를 불러올 수 없습니다.',
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.dashboard).toBeNull();
      expect(result.current.error).toBe('대시보드를 불러올 수 없습니다.');
    });

    it('should handle analytics load error gracefully', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: mockDashboard,
        error: null,
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: null,
        error: '분석 데이터를 불러올 수 없습니다.',
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Dashboard should still load
      expect(result.current.dashboard).toEqual(mockDashboard);
      // Analytics error is logged, not thrown
      expect(result.current.analytics).toBeNull();
    });

    it('should handle network exception', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockRejectedValue(new Error('Network error'));
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.error).toBe('Network error');
    });
  });

  describe('Refresh', () => {
    it('should refresh dashboard data when called', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: mockDashboard,
        error: null,
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(lawyerApi.getLawyerDashboard).toHaveBeenCalledTimes(1);

      await act(async () => {
        await result.current.refresh();
      });

      expect(lawyerApi.getLawyerDashboard).toHaveBeenCalledTimes(2);
    });

    it('should refresh analytics data when called', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: mockDashboard,
        error: null,
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(lawyerApi.getLawyerAnalytics).toHaveBeenCalledTimes(1);

      await act(async () => {
        await result.current.refreshAnalytics();
      });

      expect(lawyerApi.getLawyerAnalytics).toHaveBeenCalledTimes(2);
    });
  });

  describe('Data Alias', () => {
    it('should provide data as an alias for dashboard', async () => {
      (lawyerApi.getLawyerDashboard as jest.Mock).mockResolvedValue({
        data: mockDashboard,
        error: null,
      });
      (lawyerApi.getLawyerAnalytics as jest.Mock).mockResolvedValue({
        data: mockAnalytics,
        error: null,
      });

      const { result } = renderHook(() => useLawyerDashboard());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // data and dashboard should be the same reference
      expect(result.current.data).toBe(result.current.dashboard);
    });
  });
});
