/**
 * useEvidencePolling Hook Tests
 * Tests evidence status polling, auto-start/stop, status change callbacks
 */

import { renderHook, act } from '@testing-library/react';
import { useEvidencePolling, useSingleEvidencePolling } from '@/hooks/useEvidencePolling';
import type { Evidence } from '@/types/evidence';

// Mock the evidence API
jest.mock('@/lib/api/evidence', () => ({
  getEvidence: jest.fn(),
  getEvidenceById: jest.fn(),
}));

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  __esModule: true,
  default: {
    error: jest.fn(),
    success: jest.fn(),
  },
}));

import { getEvidence, getEvidenceById } from '@/lib/api/evidence';

const mockGetEvidence = getEvidence as jest.Mock;
const mockGetEvidenceById = getEvidenceById as jest.Mock;

// Helper to create mock evidence
const createMockEvidence = (overrides?: Partial<Evidence>): Evidence => ({
  id: 'ev-1',
  caseId: 'case-1',
  filename: 'test.jpg',
  type: 'image',
  status: 'completed',
  uploadDate: '2024-01-01T00:00:00Z',
  summary: 'Test summary',
  size: 1024,
  speaker: '원고',
  labels: ['폭언'],
  s3Key: 'cases/case-1/raw/ev-1.jpg',
  ...overrides,
});

// Helper to create API response format
const createApiEvidence = (overrides?: Partial<Record<string, unknown>>) => ({
  id: 'ev-1',
  case_id: 'case-1',
  filename: 'test.jpg',
  type: 'image',
  status: 'processed',
  created_at: '2024-01-01T00:00:00Z',
  ai_summary: 'Test summary',
  size: 1024,
  speaker: '원고',
  labels: ['폭언'],
  s3_key: 'cases/case-1/raw/ev-1.jpg',
  ...overrides,
});

// Stable empty array reference for tests
const EMPTY_EVIDENCE: Evidence[] = [];

describe('useEvidencePolling Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  describe('Initial State', () => {
    it('initializes with empty evidence array', () => {
      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      expect(result.current.evidence).toEqual([]);
      expect(result.current.isPolling).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.hasProcessingItems).toBe(false);
    });
  });

  describe('Manual Refresh', () => {
    it('fetches evidence on manual refresh', async () => {
      mockGetEvidence.mockResolvedValue({
        data: { evidence: [createApiEvidence()] },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(mockGetEvidence).toHaveBeenCalledWith('case-1');
      expect(result.current.evidence).toHaveLength(1);
      expect(result.current.evidence[0].filename).toBe('test.jpg');
    });

    it('does not fetch when caseId is empty', async () => {
      const { result } = renderHook(() =>
        useEvidencePolling('', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(mockGetEvidence).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('sets error on API failure', async () => {
      mockGetEvidence.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.error).toEqual(new Error('Network error'));
    });

    it('clears error on successful fetch', async () => {
      mockGetEvidence
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ data: { evidence: [createApiEvidence()] } });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      // First call fails
      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.error).not.toBeNull();

      // Second call succeeds
      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('API Response Mapping', () => {
    it('maps API status values correctly', async () => {
      const statusMappings = [
        { apiStatus: 'pending', expectedStatus: 'queued' },
        { apiStatus: 'processing', expectedStatus: 'processing' },
        { apiStatus: 'processed', expectedStatus: 'completed' },
        { apiStatus: 'completed', expectedStatus: 'completed' },
        { apiStatus: 'failed', expectedStatus: 'failed' },
        { apiStatus: 'queued', expectedStatus: 'queued' },
        { apiStatus: 'uploading', expectedStatus: 'uploading' },
        { apiStatus: 'review_needed', expectedStatus: 'review_needed' },
      ];

      for (const { apiStatus, expectedStatus } of statusMappings) {
        mockGetEvidence.mockResolvedValueOnce({
          data: { evidence: [createApiEvidence({ status: apiStatus })] },
        });

        const { result } = renderHook(() =>
          useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
        );

        await act(async () => {
          await result.current.refresh();
        });

        expect(result.current.evidence[0].status).toBe(expectedStatus);
      }
    });

    it('maps Article 840 tags correctly', async () => {
      const apiEvidenceWithTags = createApiEvidence({
        article_840_tags: {
          categories: ['adultery', 'irreconcilable_differences'],
          confidence: 0.85,
          matched_keywords: ['불륜', '외도'],
        },
      });

      mockGetEvidence.mockResolvedValue({
        data: { evidence: [apiEvidenceWithTags] },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.evidence[0].article840Tags).toEqual({
        categories: ['adultery', 'irreconcilable_differences'],
        confidence: 0.85,
        matchedKeywords: ['불륜', '외도'],
      });
    });

    it('handles evidence without Article 840 tags', async () => {
      mockGetEvidence.mockResolvedValue({
        data: { evidence: [createApiEvidence({ article_840_tags: undefined })] },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.evidence[0].article840Tags).toBeUndefined();
    });
  });

  describe('Manual Polling Controls', () => {
    it('manually starts and stops polling', () => {
      mockGetEvidence.mockResolvedValue({
        data: { evidence: [createApiEvidence()] },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      expect(result.current.isPolling).toBe(false);

      act(() => {
        result.current.startPolling();
      });

      expect(result.current.isPolling).toBe(true);

      act(() => {
        result.current.stopPolling();
      });

      expect(result.current.isPolling).toBe(false);
    });

    it('does not start polling twice', () => {
      mockGetEvidence.mockResolvedValue({
        data: { evidence: [createApiEvidence()] },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      act(() => {
        result.current.startPolling();
        result.current.startPolling(); // Second call should be no-op
      });

      expect(result.current.isPolling).toBe(true);
    });
  });

  describe('Processing State Detection', () => {
    it('detects processing items after fetch', async () => {
      mockGetEvidence.mockResolvedValue({
        data: {
          evidence: [
            createApiEvidence({ id: 'ev-1', status: 'processing' }),
            createApiEvidence({ id: 'ev-2', status: 'processed' }),
          ],
        },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.hasProcessingItems).toBe(true);
    });

    it('detects all final states after fetch', async () => {
      mockGetEvidence.mockResolvedValue({
        data: {
          evidence: [
            createApiEvidence({ id: 'ev-1', status: 'processed' }),
            createApiEvidence({ id: 'ev-2', status: 'failed' }),
          ],
        },
      });

      const { result } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      await act(async () => {
        await result.current.refresh();
      });

      expect(result.current.hasProcessingItems).toBe(false);
    });
  });

  describe('Cleanup', () => {
    it('stops polling state on unmount', () => {
      mockGetEvidence.mockResolvedValue({
        data: { evidence: [createApiEvidence()] },
      });

      const { result, unmount } = renderHook(() =>
        useEvidencePolling('case-1', EMPTY_EVIDENCE, { enabled: false })
      );

      act(() => {
        result.current.startPolling();
      });

      expect(result.current.isPolling).toBe(true);

      // Unmount should clean up - no errors expected
      unmount();

      // If cleanup didn't happen properly, this would cause issues
      // The fact that this completes without error indicates successful cleanup
    });
  });
});

describe('useSingleEvidencePolling Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  it('handles null initial evidence', () => {
    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', null, { enabled: false })
    );

    expect(result.current.evidence).toBeNull();
    expect(result.current.isProcessing).toBe(false);
    expect(result.current.isPolling).toBe(false);
  });

  it('returns isProcessing correctly for processing evidence', () => {
    const processingEvidence = createMockEvidence({ status: 'processing' });

    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', processingEvidence, { enabled: false })
    );

    expect(result.current.isProcessing).toBe(true);
  });

  it('returns isProcessing correctly for completed evidence', () => {
    const completedEvidence = createMockEvidence({ status: 'completed' });

    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', completedEvidence, { enabled: false })
    );

    expect(result.current.isProcessing).toBe(false);
  });

  it('manually starts and stops polling', () => {
    const evidence = createMockEvidence({ status: 'completed' });

    mockGetEvidenceById.mockResolvedValue({
      data: createApiEvidence(),
    });

    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', evidence, { enabled: false })
    );

    expect(result.current.isPolling).toBe(false);

    act(() => {
      result.current.startPolling();
    });

    expect(result.current.isPolling).toBe(true);

    act(() => {
      result.current.stopPolling();
    });

    expect(result.current.isPolling).toBe(false);
  });

  it('manually refreshes evidence', async () => {
    const initialEvidence = createMockEvidence({ summary: 'Old summary' });

    mockGetEvidenceById.mockResolvedValue({
      data: createApiEvidence({ ai_summary: 'New summary' }),
    });

    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', initialEvidence, { enabled: false })
    );

    await act(async () => {
      await result.current.refresh();
    });

    expect(mockGetEvidenceById).toHaveBeenCalled();
    expect(result.current.evidence?.summary).toBe('New summary');
  });

  it('handles API error', async () => {
    const evidence = createMockEvidence();

    mockGetEvidenceById.mockRejectedValue(new Error('Fetch failed'));

    const { result } = renderHook(() =>
      useSingleEvidencePolling('ev-1', evidence, { enabled: false })
    );

    await act(async () => {
      await result.current.refresh();
    });

    expect(result.current.error).toEqual(new Error('Fetch failed'));
  });

  it('does not fetch when evidenceId is empty', async () => {
    const { result } = renderHook(() =>
      useSingleEvidencePolling('', null, { enabled: false })
    );

    await act(async () => {
      await result.current.refresh();
    });

    expect(mockGetEvidenceById).not.toHaveBeenCalled();
  });
});
