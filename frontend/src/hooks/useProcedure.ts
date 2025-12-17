/**
 * useProcedure Hook
 * US3 - 절차 단계 관리 (Procedure Stage Tracking)
 *
 * Manages procedure stage state and operations for a case
 */

import { useState, useCallback, useEffect } from 'react';
import {
  getProcedureTimeline,
  initializeProcedureTimeline,
  updateProcedureStage,
  completeProcedureStage,
  skipProcedureStage,
  transitionToNextStage,
  getValidNextStages,
} from '@/lib/api/procedure';
import type {
  ProcedureStage,
  ProcedureStageUpdate,
  TransitionToNextStage,
  NextStageOption,
  ProcedureStageType,
} from '@/types/procedure';

interface UseProcedureState {
  stages: ProcedureStage[];
  currentStage: ProcedureStage | null;
  progressPercent: number;
  validNextStages: NextStageOption[];
  selectedStage: ProcedureStage | null;
  loading: boolean;
  transitioning: boolean;
  error: string | null;
}

interface UseProcedureReturn extends UseProcedureState {
  // Timeline operations
  fetchTimeline: () => Promise<void>;
  initializeTimeline: (startFiled?: boolean) => Promise<boolean>;

  // Stage operations
  updateStage: (stageId: string, data: ProcedureStageUpdate) => Promise<ProcedureStage | null>;
  completeStage: (stageId: string, outcome?: string) => Promise<ProcedureStage | null>;
  skipStage: (stageId: string, reason?: string) => Promise<ProcedureStage | null>;

  // Transition operations
  transition: (data: TransitionToNextStage) => Promise<boolean>;
  fetchValidNextStages: () => Promise<void>;

  // Selection
  selectStage: (stage: ProcedureStage | null) => void;
  getStageById: (stageId: string) => ProcedureStage | null;
  getStageByType: (stageType: ProcedureStageType) => ProcedureStage | null;

  // Helpers
  clearError: () => void;
  isInitialized: boolean;
}

export function useProcedure(caseId: string): UseProcedureReturn {
  const [state, setState] = useState<UseProcedureState>({
    stages: [],
    currentStage: null,
    progressPercent: 0,
    validNextStages: [],
    selectedStage: null,
    loading: false,
    transitioning: false,
    error: null,
  });

  // Fetch procedure timeline
  const fetchTimeline = useCallback(async () => {
    if (!caseId) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await getProcedureTimeline(caseId);

      if (response.error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to fetch timeline',
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        stages: response.data?.stages || [],
        currentStage: response.data?.current_stage || null,
        progressPercent: response.data?.progress_percent || 0,
        loading: false,
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch timeline',
      }));
    }
  }, [caseId]);

  // Initialize procedure timeline
  const initializeTimeline = useCallback(async (startFiled: boolean = true): Promise<boolean> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await initializeProcedureTimeline(caseId, startFiled);

      if (response.error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to initialize timeline',
        }));
        return false;
      }

      setState(prev => ({
        ...prev,
        stages: response.data?.stages || [],
        currentStage: response.data?.current_stage || null,
        progressPercent: response.data?.progress_percent || 0,
        loading: false,
      }));

      return true;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to initialize timeline',
      }));
      return false;
    }
  }, [caseId]);

  // Update a procedure stage
  const updateStage = useCallback(async (
    stageId: string,
    data: ProcedureStageUpdate
  ): Promise<ProcedureStage | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await updateProcedureStage(caseId, stageId, data);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to update stage',
        }));
        return null;
      }

      // Update in local state
      setState(prev => ({
        ...prev,
        stages: prev.stages.map(s => s.id === stageId ? response.data! : s),
        selectedStage: prev.selectedStage?.id === stageId ? response.data! : prev.selectedStage,
        currentStage: prev.currentStage?.id === stageId ? response.data! : prev.currentStage,
        loading: false,
      }));

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to update stage',
      }));
      return null;
    }
  }, [caseId]);

  // Complete a procedure stage
  const completeStage = useCallback(async (
    stageId: string,
    outcome?: string
  ): Promise<ProcedureStage | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await completeProcedureStage(caseId, stageId, outcome);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to complete stage',
        }));
        return null;
      }

      // Update in local state and recalculate progress
      setState(prev => {
        const updatedStages = prev.stages.map(s => s.id === stageId ? response.data! : s);
        const completedCount = updatedStages.filter(s => s.status === 'completed').length;
        const progressPercent = Math.round((completedCount / updatedStages.length) * 100);

        return {
          ...prev,
          stages: updatedStages,
          selectedStage: prev.selectedStage?.id === stageId ? response.data! : prev.selectedStage,
          currentStage: prev.currentStage?.id === stageId ? response.data! : prev.currentStage,
          progressPercent,
          loading: false,
        };
      });

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to complete stage',
      }));
      return null;
    }
  }, [caseId]);

  // Skip a procedure stage
  const skipStage = useCallback(async (
    stageId: string,
    reason?: string
  ): Promise<ProcedureStage | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await skipProcedureStage(caseId, stageId, reason);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error || 'Failed to skip stage',
        }));
        return null;
      }

      // Update in local state
      setState(prev => ({
        ...prev,
        stages: prev.stages.map(s => s.id === stageId ? response.data! : s),
        selectedStage: prev.selectedStage?.id === stageId ? response.data! : prev.selectedStage,
        loading: false,
      }));

      return response.data;
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to skip stage',
      }));
      return null;
    }
  }, [caseId]);

  // Transition to next stage
  const transition = useCallback(async (data: TransitionToNextStage): Promise<boolean> => {
    setState(prev => ({ ...prev, transitioning: true, error: null }));

    try {
      const response = await transitionToNextStage(caseId, data);

      if (response.error || !response.data) {
        setState(prev => ({
          ...prev,
          transitioning: false,
          error: response.error || 'Failed to transition',
        }));
        return false;
      }

      // Refresh timeline to get updated state
      await fetchTimeline();

      setState(prev => ({ ...prev, transitioning: false }));
      return true;
    } catch (err) {
      setState(prev => ({
        ...prev,
        transitioning: false,
        error: err instanceof Error ? err.message : 'Failed to transition',
      }));
      return false;
    }
  }, [caseId, fetchTimeline]);

  // Fetch valid next stages
  const fetchValidNextStages = useCallback(async () => {
    try {
      const response = await getValidNextStages(caseId);

      if (!response.error && response.data) {
        setState(prev => ({
          ...prev,
          validNextStages: response.data || [],
        }));
      }
    } catch {
      // Silently fail - not critical
    }
  }, [caseId]);

  // Select a stage
  const selectStage = useCallback((stage: ProcedureStage | null) => {
    setState(prev => ({ ...prev, selectedStage: stage }));
  }, []);

  // Get stage by ID
  const getStageById = useCallback((stageId: string): ProcedureStage | null => {
    return state.stages.find(s => s.id === stageId) || null;
  }, [state.stages]);

  // Get stage by type
  const getStageByType = useCallback((stageType: ProcedureStageType): ProcedureStage | null => {
    return state.stages.find(s => s.stage === stageType) || null;
  }, [state.stages]);

  // Clear error
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Check if timeline is initialized
  const isInitialized = state.stages.length > 0;

  // Initial fetch
  useEffect(() => {
    if (caseId) {
      fetchTimeline();
      fetchValidNextStages();
    }
  }, [caseId, fetchTimeline, fetchValidNextStages]);

  return {
    ...state,
    fetchTimeline,
    initializeTimeline,
    updateStage,
    completeStage,
    skipStage,
    transition,
    fetchValidNextStages,
    selectStage,
    getStageById,
    getStageByType,
    clearError,
    isInitialized,
  };
}
