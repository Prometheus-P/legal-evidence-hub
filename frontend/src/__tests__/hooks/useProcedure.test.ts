/**
 * useProcedure Hook Tests
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useProcedure } from '@/hooks/useProcedure';
import * as procedureApi from '@/lib/api/procedure';

// Mock the API module
jest.mock('@/lib/api/procedure');

const mockProcedureApi = procedureApi as jest.Mocked<typeof procedureApi>;

// Test data
const mockStages = [
  {
    id: 'stage_1',
    case_id: 'case_123',
    stage: 'filed' as const,
    status: 'completed' as const,
    scheduled_date: '2024-01-15T10:00:00Z',
    completed_date: '2024-01-15T11:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T11:00:00Z',
    stage_label: '소장 접수',
    status_label: '완료',
  },
  {
    id: 'stage_2',
    case_id: 'case_123',
    stage: 'served' as const,
    status: 'in_progress' as const,
    scheduled_date: '2024-01-20T10:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-16T11:00:00Z',
    stage_label: '송달',
    status_label: '진행중',
  },
  {
    id: 'stage_3',
    case_id: 'case_123',
    stage: 'answered' as const,
    status: 'pending' as const,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    stage_label: '답변서',
    status_label: '대기',
  },
];

const mockTimelineResponse = {
  case_id: 'case_123',
  stages: mockStages,
  current_stage: mockStages[1],
  progress_percent: 11,
};

describe('useProcedure Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial fetch', () => {
    it('should fetch timeline on mount', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [{ stage: 'answered' as const, label: '답변서' }],
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockProcedureApi.getProcedureTimeline).toHaveBeenCalledWith('case_123');
      expect(result.current.stages).toEqual(mockStages);
      expect(result.current.currentStage).toEqual(mockStages[1]);
      expect(result.current.progressPercent).toBe(11);
      expect(result.current.isInitialized).toBe(true);
    });

    it('should handle fetch error', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: undefined,
        error: 'Failed to fetch timeline',
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe('Failed to fetch timeline');
      expect(result.current.stages).toEqual([]);
    });
  });

  describe('initializeTimeline', () => {
    it('should initialize timeline successfully', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: { case_id: 'case_123', stages: [], current_stage: undefined, progress_percent: 0 },
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });
      mockProcedureApi.initializeProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        const success = await result.current.initializeTimeline(true);
        expect(success).toBe(true);
      });

      expect(mockProcedureApi.initializeProcedureTimeline).toHaveBeenCalledWith('case_123', true);
      expect(result.current.stages).toEqual(mockStages);
    });
  });

  describe('completeStage', () => {
    it('should complete a stage successfully', async () => {
      const completedStage = { ...mockStages[1], status: 'completed' as const };

      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });
      mockProcedureApi.completeProcedureStage.mockResolvedValue({
        data: completedStage,
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        const updated = await result.current.completeStage('stage_2', 'Success');
        expect(updated).toEqual(completedStage);
      });

      expect(mockProcedureApi.completeProcedureStage).toHaveBeenCalledWith('case_123', 'stage_2', 'Success');
    });
  });

  describe('skipStage', () => {
    it('should skip a stage successfully', async () => {
      const skippedStage = { ...mockStages[2], status: 'skipped' as const };

      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });
      mockProcedureApi.skipProcedureStage.mockResolvedValue({
        data: skippedStage,
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        const updated = await result.current.skipStage('stage_3', 'Not applicable');
        expect(updated).toEqual(skippedStage);
      });

      expect(mockProcedureApi.skipProcedureStage).toHaveBeenCalledWith('case_123', 'stage_3', 'Not applicable');
    });
  });

  describe('transition', () => {
    it('should transition to next stage successfully', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [{ stage: 'answered' as const, label: '답변서' }],
        error: undefined,
      });
      mockProcedureApi.transitionToNextStage.mockResolvedValue({
        data: {
          success: true,
          message: '답변서 단계로 이동했습니다.',
          next_stage: mockStages[2],
          completed_stage: mockStages[1],
        },
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        const success = await result.current.transition({
          next_stage: 'answered',
          complete_current: true,
        });
        expect(success).toBe(true);
      });

      expect(mockProcedureApi.transitionToNextStage).toHaveBeenCalledWith('case_123', {
        next_stage: 'answered',
        complete_current: true,
      });
    });
  });

  describe('Helper functions', () => {
    it('getStageById should return correct stage', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.getStageById('stage_2')).toEqual(mockStages[1]);
      expect(result.current.getStageById('nonexistent')).toBeNull();
    });

    it('getStageByType should return correct stage', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: mockTimelineResponse,
        error: undefined,
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.getStageByType('served')).toEqual(mockStages[1]);
      expect(result.current.getStageByType('final')).toBeNull();
    });

    it('clearError should clear error state', async () => {
      mockProcedureApi.getProcedureTimeline.mockResolvedValue({
        data: undefined,
        error: 'Some error',
      });
      mockProcedureApi.getValidNextStages.mockResolvedValue({
        data: [],
        error: undefined,
      });

      const { result } = renderHook(() => useProcedure('case_123'));

      await waitFor(() => {
        expect(result.current.error).toBe('Some error');
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});
