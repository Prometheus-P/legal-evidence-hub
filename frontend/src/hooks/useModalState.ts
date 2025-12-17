/**
 * useModalState Hook
 * 011-production-bug-fixes Feature
 *
 * URL-based modal state management for proper browser back button handling.
 * Modals are synchronized with URL search params.
 */

'use client';

import { useCallback, useMemo } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';

interface UseModalStateOptions {
  /** Query parameter name for modal state (default: 'modal') */
  paramName?: string;
  /** Whether to replace history instead of push (default: false) */
  replace?: boolean;
}

interface UseModalStateReturn {
  /** Whether the modal is open */
  isOpen: boolean;
  /** Current modal value (e.g., 'create', 'edit', item ID) */
  modalValue: string | null;
  /** Open modal with optional value */
  openModal: (value?: string) => void;
  /** Close modal (navigates back or removes param) */
  closeModal: () => void;
  /** Check if modal matches specific value */
  isModalValue: (value: string) => boolean;
}

/**
 * Hook for URL-synchronized modal state
 *
 * Benefits:
 * - Browser back button closes modal instead of navigating away
 * - Modal state survives page refresh
 * - Shareable URLs with modal open
 *
 * Usage:
 * ```tsx
 * // Basic usage
 * const { isOpen, openModal, closeModal } = useModalState();
 *
 * // With custom param name
 * const { isOpen, openModal, closeModal } = useModalState({ paramName: 'dialog' });
 *
 * // With value (for edit modals)
 * const { isOpen, modalValue, openModal, closeModal } = useModalState({ paramName: 'edit' });
 * openModal('item-123'); // URL: ?edit=item-123
 *
 * // In component
 * <button onClick={() => openModal()}>Open</button>
 * <Modal isOpen={isOpen} onClose={closeModal}>...</Modal>
 * ```
 */
export function useModalState({
  paramName = 'modal',
  replace = false,
}: UseModalStateOptions = {}): UseModalStateReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  // Get current modal value from URL
  const modalValue = useMemo(() => {
    return searchParams?.get(paramName) ?? null;
  }, [searchParams, paramName]);

  // Modal is open if param exists
  const isOpen = modalValue !== null;

  // Build URL with updated search params
  const buildUrl = useCallback(
    (value: string | null): string => {
      const params = new URLSearchParams(searchParams?.toString() || '');

      if (value !== null) {
        params.set(paramName, value);
      } else {
        params.delete(paramName);
      }

      const queryString = params.toString();
      return queryString ? `${pathname}?${queryString}` : pathname || '/';
    },
    [searchParams, pathname, paramName]
  );

  // Open modal with optional value
  const openModal = useCallback(
    (value: string = 'open') => {
      const url = buildUrl(value);
      if (replace) {
        router.replace(url, { scroll: false });
      } else {
        router.push(url, { scroll: false });
      }
    },
    [buildUrl, replace, router]
  );

  // Close modal - prefer back() for proper history navigation
  const closeModal = useCallback(() => {
    // If we pushed to open, go back
    // This provides better UX as it maintains history stack
    if (!replace && isOpen) {
      router.back();
    } else {
      // If replaced or need explicit close, navigate to URL without param
      const url = buildUrl(null);
      router.replace(url, { scroll: false });
    }
  }, [buildUrl, isOpen, replace, router]);

  // Check if modal has specific value
  const isModalValue = useCallback(
    (value: string) => modalValue === value,
    [modalValue]
  );

  return {
    isOpen,
    modalValue,
    openModal,
    closeModal,
    isModalValue,
  };
}

/**
 * Hook for multiple modals on same page
 *
 * Usage:
 * ```tsx
 * const createModal = useModalState({ paramName: 'create' });
 * const editModal = useModalState({ paramName: 'edit' });
 *
 * <button onClick={() => createModal.openModal()}>Create</button>
 * <button onClick={() => editModal.openModal(item.id)}>Edit</button>
 * ```
 */
export function useMultiModalState(modalNames: string[]) {
  const modals = modalNames.reduce(
    (acc, name) => {
      // eslint-disable-next-line react-hooks/rules-of-hooks
      acc[name] = useModalState({ paramName: name });
      return acc;
    },
    {} as Record<string, UseModalStateReturn>
  );

  // Close all modals
  const closeAll = useCallback(() => {
    Object.values(modals).forEach((modal) => {
      if (modal.isOpen) {
        modal.closeModal();
      }
    });
  }, [modals]);

  return { modals, closeAll };
}

export default useModalState;
