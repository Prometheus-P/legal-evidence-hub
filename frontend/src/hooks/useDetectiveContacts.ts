/**
 * useDetectiveContacts Hook
 * 011-production-bug-fixes Feature - US2 (T038)
 *
 * Hook for detective contact CRUD operations (lawyer's address book).
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getDetectiveContacts,
  getDetectiveContact,
  createDetectiveContact,
  updateDetectiveContact,
  deleteDetectiveContact,
} from '@/lib/api/investigators';
import type {
  DetectiveContact,
  DetectiveContactCreate,
  DetectiveContactUpdate,
  DetectiveContactQueryParams,
} from '@/types/investigator';

interface UseDetectiveContactsOptions {
  limit?: number;
  autoFetch?: boolean;
}

interface UseDetectiveContactsReturn {
  contacts: DetectiveContact[];
  total: number;
  page: number;
  isLoading: boolean;
  error: string | null;
  search: string;
  setSearch: (search: string) => void;
  setPage: (page: number) => void;
  create: (data: DetectiveContactCreate) => Promise<DetectiveContact | null>;
  update: (detectiveId: string, data: DetectiveContactUpdate) => Promise<DetectiveContact | null>;
  remove: (detectiveId: string) => Promise<boolean>;
  fetchContact: (detectiveId: string) => Promise<DetectiveContact | null>;
  refetch: () => Promise<void>;
}

export function useDetectiveContacts(
  options: UseDetectiveContactsOptions = {}
): UseDetectiveContactsReturn {
  const { limit = 20, autoFetch = true } = options;

  const [contacts, setContacts] = useState<DetectiveContact[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchContacts = useCallback(async () => {
    setError(null);
    setIsLoading(true);

    try {
      const params: DetectiveContactQueryParams = { page, limit };
      if (search) {
        params.search = search;
      }

      const response = await getDetectiveContacts(params);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setContacts(response.data.items);  // Backend uses 'items' field
        setTotal(response.data.total);
      }
    } catch {
      setError('탐정 연락처를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search]);

  // Create a new detective contact
  const create = useCallback(
    async (data: DetectiveContactCreate): Promise<DetectiveContact | null> => {
      try {
        const response = await createDetectiveContact(data);

        if (response.error) {
          setError(response.error);
          return null;
        }

        // Refresh list
        await fetchContacts();
        return response.data || null;
      } catch {
        setError('탐정 연락처 추가 중 오류가 발생했습니다.');
        return null;
      }
    },
    [fetchContacts]
  );

  // Update a detective contact
  const update = useCallback(
    async (detectiveId: string, data: DetectiveContactUpdate): Promise<DetectiveContact | null> => {
      try {
        const response = await updateDetectiveContact(detectiveId, data);

        if (response.error) {
          setError(response.error);
          return null;
        }

        // Update local state
        if (response.data) {
          setContacts((prev) =>
            prev.map((c) => (c.id === detectiveId ? response.data! : c))
          );
        }

        return response.data || null;
      } catch {
        setError('탐정 연락처 수정 중 오류가 발생했습니다.');
        return null;
      }
    },
    []
  );

  // Delete a detective contact
  const remove = useCallback(
    async (detectiveId: string): Promise<boolean> => {
      try {
        const response = await deleteDetectiveContact(detectiveId);

        if (response.error) {
          setError(response.error);
          return false;
        }

        // Remove from local state
        setContacts((prev) => prev.filter((c) => c.id !== detectiveId));
        setTotal((prev) => Math.max(0, prev - 1));

        return true;
      } catch {
        setError('탐정 연락처 삭제 중 오류가 발생했습니다.');
        return false;
      }
    },
    []
  );

  // Fetch a single contact by ID
  const fetchContact = useCallback(
    async (detectiveId: string): Promise<DetectiveContact | null> => {
      try {
        const response = await getDetectiveContact(detectiveId);

        if (response.error) {
          setError(response.error);
          return null;
        }

        return response.data || null;
      } catch {
        setError('탐정 연락처를 불러오는 중 오류가 발생했습니다.');
        return null;
      }
    },
    []
  );

  // Handle search with page reset
  const handleSetSearch = useCallback((newSearch: string) => {
    setSearch(newSearch);
    setPage(1); // Reset to first page on search change
  }, []);

  // Initial fetch
  useEffect(() => {
    if (autoFetch) {
      fetchContacts();
    }
  }, [fetchContacts, autoFetch]);

  return {
    contacts,
    total,
    page,
    isLoading,
    error,
    search,
    setSearch: handleSetSearch,
    setPage,
    create,
    update,
    remove,
    fetchContact,
    refetch: fetchContacts,
  };
}

export default useDetectiveContacts;
