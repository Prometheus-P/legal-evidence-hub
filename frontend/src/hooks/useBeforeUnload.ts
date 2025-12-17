/**
 * useBeforeUnload Hook
 * 011-production-bug-fixes Feature
 *
 * Warns users before leaving a page with unsaved changes.
 * Handles both browser refresh/close and Next.js route changes.
 */

'use client';

import { useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface UseBeforeUnloadOptions {
  /** Whether there are unsaved changes */
  isDirty: boolean;
  /** Custom warning message (browser may override) */
  message?: string;
  /** Callback when user confirms leaving */
  onConfirmLeave?: () => void;
}

/**
 * Hook for warning users about unsaved changes
 *
 * Usage:
 * ```tsx
 * const [formData, setFormData] = useState(initialData);
 * const isDirty = JSON.stringify(formData) !== JSON.stringify(initialData);
 *
 * useBeforeUnload({
 *   isDirty,
 *   message: '저장하지 않은 변경사항이 있습니다. 페이지를 떠나시겠습니까?'
 * });
 * ```
 */
export function useBeforeUnload({
  isDirty,
  message = '저장하지 않은 변경사항이 있습니다. 페이지를 떠나시겠습니까?',
  onConfirmLeave,
}: UseBeforeUnloadOptions) {
  // Handle browser beforeunload event (refresh, close tab, external navigation)
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!isDirty) return;

      // Standard way to show confirmation dialog
      e.preventDefault();
      // Chrome requires returnValue to be set
      e.returnValue = message;
      return message;
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty, message]);

  // Confirm navigation helper for programmatic use
  const confirmNavigation = useCallback(
    (callback: () => void) => {
      if (!isDirty) {
        callback();
        return;
      }

      const confirmed = window.confirm(message);
      if (confirmed) {
        onConfirmLeave?.();
        callback();
      }
    },
    [isDirty, message, onConfirmLeave]
  );

  return { confirmNavigation };
}

/**
 * Hook for form dirty state tracking
 *
 * Usage:
 * ```tsx
 * const { isDirty, setIsDirty, markClean } = useFormDirtyState();
 *
 * const handleChange = (value) => {
 *   setFormData(value);
 *   setIsDirty(true);
 * };
 *
 * const handleSubmit = async () => {
 *   await saveData();
 *   markClean();
 * };
 *
 * useBeforeUnload({ isDirty });
 * ```
 */
export function useFormDirtyState(initialDirty = false) {
  const [isDirty, setIsDirtyState] = useState(initialDirty);

  const setIsDirty = useCallback((dirty: boolean) => {
    setIsDirtyState(dirty);
  }, []);

  const markClean = useCallback(() => {
    setIsDirtyState(false);
  }, []);

  const markDirty = useCallback(() => {
    setIsDirtyState(true);
  }, []);

  return { isDirty, setIsDirty, markClean, markDirty };
}

// Need to import useState for useFormDirtyState
import { useState } from 'react';

export default useBeforeUnload;
