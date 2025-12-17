/**
 * UploadProgress Component (T063)
 *
 * Displays upload progress for evidence files.
 * Shows individual file progress and overall batch progress.
 *
 * Features:
 * - Individual file progress bars
 * - Overall upload progress
 * - Cancel/retry actions per file
 * - Accessible progress announcements
 */

'use client';

import { useEffect, useRef } from 'react';
import { X, Check, AlertCircle, RefreshCw, FileIcon } from 'lucide-react';
import { Button } from '@/components/primitives';

export interface UploadFile {
  /**
   * Unique file ID
   */
  id: string;
  /**
   * File name
   */
  name: string;
  /**
   * File size in bytes
   */
  size: number;
  /**
   * Upload progress (0-100)
   */
  progress: number;
  /**
   * Upload status
   */
  status: 'pending' | 'uploading' | 'completed' | 'error';
  /**
   * Error message if failed
   */
  error?: string;
}

interface UploadProgressProps {
  /**
   * List of files being uploaded
   */
  files: UploadFile[];
  /**
   * Handler to cancel a file upload
   */
  onCancel?: (fileId: string) => void;
  /**
   * Handler to retry a failed upload
   */
  onRetry?: (fileId: string) => void;
  /**
   * Handler to remove a file from list
   */
  onRemove?: (fileId: string) => void;
  /**
   * Whether to show overall progress
   */
  showOverallProgress?: boolean;
  /**
   * Additional classes
   */
  className?: string;
}

/**
 * Format file size to human-readable string
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/**
 * Get status color class
 */
function getStatusColor(status: UploadFile['status']): string {
  switch (status) {
    case 'completed':
      return 'bg-success';
    case 'error':
      return 'bg-error';
    case 'uploading':
      return 'bg-primary';
    default:
      return 'bg-neutral-300 dark:bg-neutral-600';
  }
}

/**
 * Get status icon
 */
function StatusIcon({ status }: { status: UploadFile['status'] }) {
  switch (status) {
    case 'completed':
      return <Check className="w-4 h-4 text-success" aria-hidden="true" />;
    case 'error':
      return <AlertCircle className="w-4 h-4 text-error" aria-hidden="true" />;
    default:
      return <FileIcon className="w-4 h-4 text-neutral-400" aria-hidden="true" />;
  }
}

export function UploadProgress({
  files,
  onCancel,
  onRetry,
  onRemove,
  showOverallProgress = true,
  className = '',
}: UploadProgressProps) {
  const announceRef = useRef<HTMLDivElement>(null);

  // Calculate overall progress
  const totalProgress = files.length > 0
    ? Math.round(files.reduce((sum, f) => sum + f.progress, 0) / files.length)
    : 0;

  const completedCount = files.filter(f => f.status === 'completed').length;
  const errorCount = files.filter(f => f.status === 'error').length;

  // Announce progress changes to screen readers
  useEffect(() => {
    if (completedCount === files.length && files.length > 0) {
      if (announceRef.current) {
        announceRef.current.textContent = `모든 파일 업로드 완료. ${files.length}개 파일이 업로드되었습니다.`;
      }
    }
  }, [completedCount, files.length]);

  if (files.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Screen reader announcements */}
      <div
        ref={announceRef}
        role="status"
        aria-live="polite"
        className="sr-only"
      />

      {/* Overall Progress */}
      {showOverallProgress && files.length > 1 && (
        <div className="p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              전체 진행률
            </span>
            <span className="text-sm text-neutral-500 dark:text-neutral-400">
              {completedCount}/{files.length} 완료
              {errorCount > 0 && ` (${errorCount}개 실패)`}
            </span>
          </div>
          <div
            role="progressbar"
            aria-valuenow={totalProgress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`전체 업로드 진행률 ${totalProgress}%`}
            className="h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden"
          >
            <div
              className="h-full bg-primary transition-all duration-300 ease-out"
              style={{ width: `${totalProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Individual File Progress */}
      <ul
        role="list"
        aria-label="업로드 파일 목록"
        className="space-y-2"
      >
        {files.map((file) => (
          <li
            key={file.id}
            className="p-3 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-700 rounded-lg"
          >
            <div className="flex items-center gap-3">
              {/* Status Icon */}
              <StatusIcon status={file.status} />

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center mb-1">
                  <span
                    className="text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate"
                    title={file.name}
                  >
                    {file.name}
                  </span>
                  <span className="text-xs text-neutral-500 dark:text-neutral-400 ml-2">
                    {formatFileSize(file.size)}
                  </span>
                </div>

                {/* Progress Bar */}
                {file.status === 'uploading' && (
                  <div className="flex items-center gap-2">
                    <div
                      role="progressbar"
                      aria-valuenow={file.progress}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${file.name} 업로드 진행률 ${file.progress}%`}
                      className="flex-1 h-1.5 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden"
                    >
                      <div
                        className={`h-full ${getStatusColor(file.status)} transition-all duration-300 ease-out`}
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-neutral-500 dark:text-neutral-400">
                      {file.progress}%
                    </span>
                  </div>
                )}

                {/* Error Message */}
                {file.status === 'error' && file.error && (
                  <p className="text-xs text-error mt-1">
                    {file.error}
                  </p>
                )}

                {/* Completed Message */}
                {file.status === 'completed' && (
                  <p className="text-xs text-success mt-1">
                    업로드 완료
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1">
                {/* Cancel button for uploading files */}
                {file.status === 'uploading' && onCancel && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onCancel(file.id)}
                    aria-label={`${file.name} 업로드 취소`}
                    className="p-1 min-w-[32px] min-h-[32px]"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}

                {/* Retry button for failed files */}
                {file.status === 'error' && onRetry && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRetry(file.id)}
                    aria-label={`${file.name} 다시 시도`}
                    className="p-1 min-w-[32px] min-h-[32px]"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                )}

                {/* Remove button for completed/failed files */}
                {(file.status === 'completed' || file.status === 'error') && onRemove && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onRemove(file.id)}
                    aria-label={`${file.name} 목록에서 제거`}
                    className="p-1 min-w-[32px] min-h-[32px]"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default UploadProgress;
