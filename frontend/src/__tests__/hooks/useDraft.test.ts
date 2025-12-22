/**
 * useDraft Hook Tests
 * Tests for draft generation, preview, and download functionality
 *
 * Covers:
 * - Modal state management
 * - Draft generation flow
 * - Download functionality
 * - Error handling
 * - State management
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useDraft } from '@/hooks/useDraft';

// Mock the draft API
jest.mock('@/lib/api/draft', () => ({
  generateDraftPreview: jest.fn(),
}));

// Mock the document service
jest.mock('@/services/documentService', () => ({
  downloadDraftAsDocx: jest.fn(),
}));

// Mock the logger
jest.mock('@/lib/logger', () => ({
  logger: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
  },
}));

import { generateDraftPreview } from '@/lib/api/draft';
import { downloadDraftAsDocx } from '@/services/documentService';

const mockGenerateDraftPreview = generateDraftPreview as jest.Mock;
const mockDownloadDraftAsDocx = downloadDraftAsDocx as jest.Mock;

describe('useDraft', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns initial state correctly', () => {
      const { result } = renderHook(() => useDraft('case-123'));

      expect(result.current.showDraftModal).toBe(false);
      expect(result.current.draftText).toBe('');
      expect(result.current.draftCitations).toEqual([]);
      expect(result.current.hasExistingDraft).toBe(false);
      expect(result.current.isGenerating).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('handles null caseId', () => {
      const { result } = renderHook(() => useDraft(null));

      expect(result.current.showDraftModal).toBe(false);
      expect(result.current.draftText).toBe('');
    });
  });

  describe('Modal State Management', () => {
    it('opens draft modal', () => {
      const { result } = renderHook(() => useDraft('case-123'));

      act(() => {
        result.current.openDraftModal();
      });

      expect(result.current.showDraftModal).toBe(true);
    });

    it('closes draft modal', () => {
      const { result } = renderHook(() => useDraft('case-123'));

      act(() => {
        result.current.openDraftModal();
      });

      expect(result.current.showDraftModal).toBe(true);

      act(() => {
        result.current.closeDraftModal();
      });

      expect(result.current.showDraftModal).toBe(false);
    });

    it('regenerateDraft opens modal', () => {
      const { result } = renderHook(() => useDraft('case-123'));

      act(() => {
        result.current.regenerateDraft();
      });

      expect(result.current.showDraftModal).toBe(true);
    });
  });

  describe('Draft Generation', () => {
    it('generates draft successfully', async () => {
      const mockResponse = {
        data: {
          draft_text: '# 소장\n\n## 청구취지\n\n테스트 내용입니다.',
          citations: [
            {
              evidence_id: 'ev-1',
              snippet: '증거 내용 일부분입니다. 이것은 테스트 인용문입니다.',
            },
            {
              evidence_id: 'ev-2',
              snippet: '짧은 인용',
            },
          ],
        },
      };

      mockGenerateDraftPreview.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(mockGenerateDraftPreview).toHaveBeenCalledWith('case-123', {
        sections: ['청구취지', '청구원인'],
        language: 'ko',
        style: '법원 제출용_표준',
      });

      expect(result.current.draftText).toBe('# 소장\n\n## 청구취지\n\n테스트 내용입니다.');
      expect(result.current.draftCitations).toHaveLength(2);
      expect(result.current.hasExistingDraft).toBe(true);
      expect(result.current.showDraftModal).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('maps citations correctly with truncation', async () => {
      const longSnippet = 'A'.repeat(100);
      const mockResponse = {
        data: {
          draft_text: 'Draft content',
          citations: [
            {
              evidence_id: 'ev-1',
              snippet: longSnippet,
            },
          ],
        },
      };

      mockGenerateDraftPreview.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      // Title should be truncated to 50 chars + "..."
      expect(result.current.draftCitations[0].title.length).toBe(53);
      expect(result.current.draftCitations[0].title.endsWith('...')).toBe(true);
      // Quote should be full snippet
      expect(result.current.draftCitations[0].quote).toBe(longSnippet);
    });

    it('sets isGenerating during generation', async () => {
      let resolvePromise: (value: unknown) => void;
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockGenerateDraftPreview.mockReturnValue(pendingPromise);

      const { result } = renderHook(() => useDraft('case-123'));

      // Start generation without awaiting
      act(() => {
        result.current.generateDraft();
      });

      // Should be generating
      expect(result.current.isGenerating).toBe(true);

      // Resolve the promise
      await act(async () => {
        resolvePromise!({
          data: {
            draft_text: 'Content',
            citations: [],
          },
        });
      });

      // Should no longer be generating
      await waitFor(() => {
        expect(result.current.isGenerating).toBe(false);
      });
    });

    it('handles API error response', async () => {
      mockGenerateDraftPreview.mockResolvedValue({
        error: '서버 오류가 발생했습니다.',
        data: null,
      });

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.error).toBe('서버 오류가 발생했습니다.');
      expect(result.current.draftText).toBe('');
      expect(result.current.hasExistingDraft).toBe(false);
    });

    it('handles API exception', async () => {
      mockGenerateDraftPreview.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.error).toBe('Network error');
      expect(result.current.isGenerating).toBe(false);
    });

    it('does nothing when caseId is null', async () => {
      const { result } = renderHook(() => useDraft(null));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(mockGenerateDraftPreview).not.toHaveBeenCalled();
    });

    it('clears previous error on new generation', async () => {
      // First call fails
      mockGenerateDraftPreview.mockResolvedValueOnce({
        error: 'First error',
        data: null,
      });

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.error).toBe('First error');

      // Second call succeeds
      mockGenerateDraftPreview.mockResolvedValueOnce({
        data: {
          draft_text: 'Success',
          citations: [],
        },
      });

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.error).toBeNull();
      expect(result.current.draftText).toBe('Success');
    });
  });

  describe('Draft Download', () => {
    it('downloads draft successfully', async () => {
      mockDownloadDraftAsDocx.mockResolvedValue({
        success: true,
      });

      const { result } = renderHook(() => useDraft('case-123'));

      let downloadResult: { success: boolean };
      await act(async () => {
        downloadResult = await result.current.downloadDraft({
          format: 'docx',
          content: 'Draft content here',
        });
      });

      expect(mockDownloadDraftAsDocx).toHaveBeenCalledWith(
        'Draft content here',
        'case-123',
        'docx'
      );
      expect(downloadResult!.success).toBe(true);
    });

    it('handles download error', async () => {
      mockDownloadDraftAsDocx.mockResolvedValue({
        success: false,
        error: 'Download failed',
      });

      const { result } = renderHook(() => useDraft('case-123'));

      let downloadResult: { success: boolean; error?: string };
      await act(async () => {
        downloadResult = await result.current.downloadDraft({
          format: 'pdf',
          content: 'Draft content',
        });
      });

      expect(downloadResult!.success).toBe(false);
      expect(downloadResult!.error).toBe('Download failed');
    });

    it('handles download exception', async () => {
      mockDownloadDraftAsDocx.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useDraft('case-123'));

      let downloadResult: { success: boolean; error?: string };
      await act(async () => {
        downloadResult = await result.current.downloadDraft({
          format: 'docx',
          content: 'Draft content',
        });
      });

      expect(downloadResult!.success).toBe(false);
      expect(downloadResult!.error).toBe('Network error');
    });

    it('returns error when caseId is null', async () => {
      const { result } = renderHook(() => useDraft(null));

      let downloadResult: { success: boolean; error?: string };
      await act(async () => {
        downloadResult = await result.current.downloadDraft({
          format: 'docx',
          content: 'Draft content',
        });
      });

      expect(downloadResult!.success).toBe(false);
      expect(downloadResult!.error).toBe('Case ID is required for download');
      expect(mockDownloadDraftAsDocx).not.toHaveBeenCalled();
    });
  });

  describe('Clear Draft', () => {
    it('clears all draft state', async () => {
      mockGenerateDraftPreview.mockResolvedValue({
        data: {
          draft_text: 'Generated content',
          citations: [{ evidence_id: 'ev-1', snippet: 'Citation' }],
        },
      });

      const { result } = renderHook(() => useDraft('case-123'));

      // Generate a draft first
      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.draftText).toBe('Generated content');
      expect(result.current.hasExistingDraft).toBe(true);

      // Clear the draft
      act(() => {
        result.current.clearDraft();
      });

      expect(result.current.draftText).toBe('');
      expect(result.current.draftCitations).toEqual([]);
      expect(result.current.hasExistingDraft).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('clears error state', async () => {
      mockGenerateDraftPreview.mockResolvedValue({
        error: 'Generation failed',
        data: null,
      });

      const { result } = renderHook(() => useDraft('case-123'));

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.error).toBe('Generation failed');

      act(() => {
        result.current.clearDraft();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('CaseId Changes', () => {
    it('maintains state when caseId changes', async () => {
      mockGenerateDraftPreview.mockResolvedValue({
        data: {
          draft_text: 'Case 1 content',
          citations: [],
        },
      });

      const { result, rerender } = renderHook(
        ({ caseId }) => useDraft(caseId),
        { initialProps: { caseId: 'case-1' } }
      );

      await act(async () => {
        await result.current.generateDraft();
      });

      expect(result.current.draftText).toBe('Case 1 content');

      // Change caseId - state should persist (hook doesn't auto-clear)
      rerender({ caseId: 'case-2' });

      // Draft text persists until explicitly cleared or regenerated
      expect(result.current.draftText).toBe('Case 1 content');
    });
  });
});
