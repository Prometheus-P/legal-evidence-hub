/**
 * useEvidenceUpload Hook Tests
 * Tests for evidence upload functionality with progress tracking
 *
 * Covers:
 * - Presigned URL acquisition
 * - S3 upload with progress
 * - Upload completion notification
 * - Error handling
 * - Feedback message management
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useEvidenceUpload } from '@/hooks/useEvidenceUpload';

// Mock the evidence API
jest.mock('@/lib/api/evidence', () => ({
  getPresignedUploadUrl: jest.fn(),
  uploadToS3: jest.fn(),
  notifyUploadComplete: jest.fn(),
}));

// Mock the logger
jest.mock('@/lib/logger', () => ({
  logger: {
    error: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
  },
}));

import {
  getPresignedUploadUrl,
  uploadToS3,
  notifyUploadComplete,
} from '@/lib/api/evidence';

const mockGetPresignedUploadUrl = getPresignedUploadUrl as jest.Mock;
const mockUploadToS3 = uploadToS3 as jest.Mock;
const mockNotifyUploadComplete = notifyUploadComplete as jest.Mock;

// Helper to create mock File objects
function createMockFile(name: string, size: number = 1024, type: string = 'image/jpeg'): File {
  const blob = new Blob(['x'.repeat(size)], { type });
  return new File([blob], name, { type });
}

describe('useEvidenceUpload', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Initial State', () => {
    it('returns initial upload status', () => {
      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      expect(result.current.uploadStatus).toEqual({
        isUploading: false,
        currentFile: '',
        progress: 0,
        completed: 0,
        total: 0,
      });
      expect(result.current.uploadFeedback).toBeNull();
      expect(result.current.isUploading).toBe(false);
    });
  });

  describe('Successful Upload Flow', () => {
    it('uploads a single file successfully', async () => {
      const mockPresignedResponse = {
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      };

      mockGetPresignedUploadUrl.mockResolvedValue(mockPresignedResponse);
      mockUploadToS3.mockImplementation((url, file, onProgress) => {
        // Simulate progress
        onProgress({ percent: 50 });
        onProgress({ percent: 100 });
        return Promise.resolve(true);
      });
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useEvidenceUpload('case-123', { onUploadComplete: onComplete })
      );

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(mockGetPresignedUploadUrl).toHaveBeenCalledWith('case-123', 'test.jpg', 'image/jpeg');
      expect(mockUploadToS3).toHaveBeenCalled();
      expect(mockNotifyUploadComplete).toHaveBeenCalledWith({
        case_id: 'case-123',
        evidence_temp_id: 'temp-123',
        s3_key: 'cases/case-123/raw/file.jpg',
        file_size: expect.any(Number),
      });
      expect(onComplete).toHaveBeenCalled();
      expect(result.current.uploadFeedback?.tone).toBe('success');
    });

    it('uploads multiple files successfully', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useEvidenceUpload('case-123', { onUploadComplete: onComplete })
      );

      const files = [
        createMockFile('file1.jpg'),
        createMockFile('file2.jpg'),
        createMockFile('file3.jpg'),
      ];

      await act(async () => {
        await result.current.handleUpload(files);
      });

      expect(mockGetPresignedUploadUrl).toHaveBeenCalledTimes(3);
      expect(mockUploadToS3).toHaveBeenCalledTimes(3);
      expect(mockNotifyUploadComplete).toHaveBeenCalledTimes(3);
      expect(result.current.uploadFeedback?.message).toContain('3개 파일 업로드 완료');
    });

    it('tracks upload progress correctly', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });

      let progressCallback: ((progress: { percent: number }) => void) | null = null;
      mockUploadToS3.mockImplementation((url, file, onProgress) => {
        progressCallback = onProgress;
        return new Promise((resolve) => {
          setTimeout(() => resolve(true), 100);
        });
      });
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      // Start upload
      act(() => {
        result.current.handleUpload([file]);
      });

      // Wait for upload to start
      await waitFor(() => {
        expect(result.current.isUploading).toBe(true);
      });

      // Simulate progress updates
      if (progressCallback) {
        act(() => {
          progressCallback!({ percent: 25 });
        });

        expect(result.current.uploadStatus.progress).toBe(25);

        act(() => {
          progressCallback!({ percent: 75 });
        });

        expect(result.current.uploadStatus.progress).toBe(75);
      }
    });
  });

  describe('Error Handling', () => {
    it('handles presigned URL failure', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        error: 'Failed to get presigned URL',
        data: null,
      });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(result.current.uploadFeedback?.tone).toBe('error');
      expect(result.current.uploadFeedback?.message).toContain('업로드 실패');
    });

    it('handles S3 upload failure', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(false);

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(result.current.uploadFeedback?.tone).toBe('error');
    });

    it('handles upload completion notification failure', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({
        error: 'Notification failed',
      });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(result.current.uploadFeedback?.tone).toBe('error');
    });

    it('handles partial upload failure', async () => {
      // First file succeeds, second fails
      mockGetPresignedUploadUrl
        .mockResolvedValueOnce({
          data: {
            upload_url: 'https://s3.example.com/upload',
            evidence_temp_id: 'temp-1',
            s3_key: 'cases/case-123/raw/file1.jpg',
          },
        })
        .mockResolvedValueOnce({
          error: 'Failed',
          data: null,
        });

      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const onComplete = jest.fn();
      const { result } = renderHook(() =>
        useEvidenceUpload('case-123', { onUploadComplete: onComplete })
      );

      const files = [createMockFile('file1.jpg'), createMockFile('file2.jpg')];

      await act(async () => {
        await result.current.handleUpload(files);
      });

      // Should show partial success
      expect(result.current.uploadFeedback?.tone).toBe('info');
      expect(result.current.uploadFeedback?.message).toContain('1개 성공');
      expect(result.current.uploadFeedback?.message).toContain('1개 실패');
      // onComplete should still be called for partial success
      expect(onComplete).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('does nothing when files array is empty', async () => {
      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      await act(async () => {
        await result.current.handleUpload([]);
      });

      expect(mockGetPresignedUploadUrl).not.toHaveBeenCalled();
      expect(result.current.isUploading).toBe(false);
    });

    it('does nothing when caseId is empty', async () => {
      const { result } = renderHook(() => useEvidenceUpload(''));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(mockGetPresignedUploadUrl).not.toHaveBeenCalled();
    });

    it('uses application/octet-stream for files without type', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      // Create file without type
      const blob = new Blob(['test']);
      const file = new File([blob], 'unknown-file');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(mockGetPresignedUploadUrl).toHaveBeenCalledWith(
        'case-123',
        'unknown-file',
        'application/octet-stream'
      );
    });
  });

  describe('Feedback Management', () => {
    it('clears feedback after timeout', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() =>
        useEvidenceUpload('case-123', { feedbackDuration: 1000 })
      );

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(result.current.uploadFeedback).not.toBeNull();

      // Fast-forward past feedback duration
      act(() => {
        jest.advanceTimersByTime(1500);
      });

      expect(result.current.uploadFeedback).toBeNull();
    });

    it('allows manual feedback clearing', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      expect(result.current.uploadFeedback).not.toBeNull();

      act(() => {
        result.current.clearFeedback();
      });

      expect(result.current.uploadFeedback).toBeNull();
    });

    it('resets all state with reset function', async () => {
      mockGetPresignedUploadUrl.mockResolvedValue({
        data: {
          upload_url: 'https://s3.example.com/upload',
          evidence_temp_id: 'temp-123',
          s3_key: 'cases/case-123/raw/file.jpg',
        },
      });
      mockUploadToS3.mockResolvedValue(true);
      mockNotifyUploadComplete.mockResolvedValue({ data: { success: true } });

      const { result } = renderHook(() => useEvidenceUpload('case-123'));

      const file = createMockFile('test.jpg');

      await act(async () => {
        await result.current.handleUpload([file]);
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.uploadStatus).toEqual({
        isUploading: false,
        currentFile: '',
        progress: 0,
        completed: 0,
        total: 0,
      });
      expect(result.current.uploadFeedback).toBeNull();
    });
  });
});
