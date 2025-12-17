/**
 * useRetry Hook
 * 009-mvp-gap-closure Feature - T024
 *
 * Provides retry functionality with exponential backoff for API calls.
 * Implements FR-009 (네트워크 오류 시 다시 시도 버튼)
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import toast from 'react-hot-toast';

export interface UseRetryOptions {
  /** Maximum number of retry attempts (default: 3) */
  maxRetries?: number;
  /** Initial delay in milliseconds (default: 1000) */
  initialDelay?: number;
  /** Maximum delay in milliseconds (default: 30000) */
  maxDelay?: number;
  /** Backoff multiplier (default: 2) */
  backoffMultiplier?: number;
  /** Show toast notifications for retry attempts (default: true) */
  showToast?: boolean;
  /** Callback when all retries are exhausted */
  onExhausted?: () => void;
}

export interface UseRetryResult<T> {
  /** Execute the function with retry logic */
  execute: () => Promise<T | null>;
  /** Current retry count */
  retryCount: number;
  /** Is currently executing or retrying */
  isLoading: boolean;
  /** Last error encountered */
  error: Error | null;
  /** Reset retry state */
  reset: () => void;
  /** Manually retry the last operation */
  retry: () => Promise<T | null>;
  /** Cancel ongoing retry */
  cancel: () => void;
}

/**
 * Hook for executing async functions with automatic retry and exponential backoff
 *
 * @example
 * ```tsx
 * const { execute, isLoading, error, retry } = useRetry(
 *   async () => {
 *     const response = await apiClient.get('/data');
 *     if (response.error) throw new Error(response.error);
 *     return response.data;
 *   },
 *   { maxRetries: 3, initialDelay: 1000 }
 * );
 *
 * // Execute with automatic retries
 * const data = await execute();
 *
 * // Manual retry button
 * <button onClick={retry} disabled={isLoading}>다시 시도</button>
 * ```
 */
export function useRetry<T>(
  fn: () => Promise<T>,
  options: UseRetryOptions = {}
): UseRetryResult<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    showToast = true,
    onExhausted,
  } = options;

  const [retryCount, setRetryCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const calculateDelay = useCallback(
    (attempt: number): number => {
      const delay = initialDelay * Math.pow(backoffMultiplier, attempt);
      return Math.min(delay, maxDelay);
    },
    [initialDelay, backoffMultiplier, maxDelay]
  );

  const sleep = useCallback(
    (ms: number, signal?: AbortSignal): Promise<void> => {
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(resolve, ms);
        signal?.addEventListener('abort', () => {
          clearTimeout(timeout);
          reject(new DOMException('Aborted', 'AbortError'));
        });
      });
    },
    []
  );

  const execute = useCallback(async (): Promise<T | null> => {
    setIsLoading(true);
    setError(null);
    setRetryCount(0);

    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      if (signal.aborted) {
        setIsLoading(false);
        return null;
      }

      try {
        // Wait before retry (skip for first attempt)
        if (attempt > 0) {
          const delay = calculateDelay(attempt - 1);
          if (showToast) {
            toast(`재시도 중... (${attempt}/${maxRetries})`, {
              icon: '🔄',
              duration: delay,
            });
          }
          await sleep(delay, signal);
        }

        setRetryCount(attempt);
        const result = await fnRef.current();
        setIsLoading(false);
        setError(null);

        if (attempt > 0 && showToast) {
          toast.success('요청이 성공했습니다.');
        }

        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        // Don't retry on abort
        if (err instanceof DOMException && err.name === 'AbortError') {
          setIsLoading(false);
          return null;
        }

        // Check if we should retry
        if (attempt < maxRetries) {
          console.warn(`Retry attempt ${attempt + 1}/${maxRetries} failed:`, lastError.message);
        }
      }
    }

    // All retries exhausted
    setError(lastError);
    setIsLoading(false);

    if (showToast && lastError) {
      toast.error('요청이 실패했습니다. 잠시 후 다시 시도해 주세요.');
    }

    onExhausted?.();

    return null;
  }, [maxRetries, calculateDelay, sleep, showToast, onExhausted]);

  const retry = useCallback(async (): Promise<T | null> => {
    return execute();
  }, [execute]);

  const reset = useCallback(() => {
    abortControllerRef.current?.abort();
    setRetryCount(0);
    setIsLoading(false);
    setError(null);
  }, []);

  const cancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsLoading(false);
  }, []);

  return {
    execute,
    retryCount,
    isLoading,
    error,
    reset,
    retry,
    cancel,
  };
}

/**
 * Simple retry wrapper for one-off operations
 *
 * @example
 * ```tsx
 * const data = await retryOperation(
 *   () => apiClient.get('/data'),
 *   { maxRetries: 3 }
 * );
 * ```
 */
export async function retryOperation<T>(
  fn: () => Promise<T>,
  options: Omit<UseRetryOptions, 'onExhausted'> = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
    showToast = false,
  } = options;

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      // Wait before retry (skip for first attempt)
      if (attempt > 0) {
        const delay = Math.min(
          initialDelay * Math.pow(backoffMultiplier, attempt - 1),
          maxDelay
        );
        if (showToast && typeof window !== 'undefined') {
          toast(`재시도 중... (${attempt}/${maxRetries})`, {
            icon: '🔄',
            duration: delay,
          });
        }
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      return await fn();
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));

      if (attempt < maxRetries) {
        console.warn(`Retry attempt ${attempt + 1}/${maxRetries} failed:`, lastError.message);
      }
    }
  }

  if (showToast && typeof window !== 'undefined') {
    toast.error('요청이 실패했습니다.');
  }

  throw lastError || new Error('Unknown error');
}

export default useRetry;
