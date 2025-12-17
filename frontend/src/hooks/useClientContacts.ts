/**
 * useClientContacts Hook
 * 011-production-bug-fixes Feature - US2 (T037)
 *
 * Hook for client contact CRUD operations (lawyer's address book).
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getClientContacts,
  getClientContact,
  createClientContact,
  updateClientContact,
  deleteClientContact,
} from '@/lib/api/clients';
import type {
  ClientContact,
  ClientContactCreate,
  ClientContactUpdate,
  ClientContactQueryParams,
} from '@/types/client';

interface UseClientContactsOptions {
  limit?: number;
  autoFetch?: boolean;
}

interface UseClientContactsReturn {
  contacts: ClientContact[];
  total: number;
  page: number;
  isLoading: boolean;
  error: string | null;
  search: string;
  setSearch: (search: string) => void;
  setPage: (page: number) => void;
  create: (data: ClientContactCreate) => Promise<ClientContact | null>;
  update: (clientId: string, data: ClientContactUpdate) => Promise<ClientContact | null>;
  remove: (clientId: string) => Promise<boolean>;
  fetchContact: (clientId: string) => Promise<ClientContact | null>;
  refetch: () => Promise<void>;
}

export function useClientContacts(
  options: UseClientContactsOptions = {}
): UseClientContactsReturn {
  const { limit = 20, autoFetch = true } = options;

  const [contacts, setContacts] = useState<ClientContact[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchContacts = useCallback(async () => {
    setError(null);
    setIsLoading(true);

    try {
      const params: ClientContactQueryParams = { page, limit };
      if (search) {
        params.search = search;
      }

      const response = await getClientContacts(params);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setContacts(response.data.items);  // Backend uses 'items' field
        setTotal(response.data.total);
      }
    } catch {
      setError('의뢰인 연락처를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [page, limit, search]);

  // Create a new client contact
  const create = useCallback(
    async (data: ClientContactCreate): Promise<ClientContact | null> => {
      try {
        const response = await createClientContact(data);

        if (response.error) {
          setError(response.error);
          return null;
        }

        // Refresh list
        await fetchContacts();
        return response.data || null;
      } catch {
        setError('의뢰인 연락처 추가 중 오류가 발생했습니다.');
        return null;
      }
    },
    [fetchContacts]
  );

  // Update a client contact
  const update = useCallback(
    async (clientId: string, data: ClientContactUpdate): Promise<ClientContact | null> => {
      try {
        const response = await updateClientContact(clientId, data);

        if (response.error) {
          setError(response.error);
          return null;
        }

        // Update local state
        if (response.data) {
          setContacts((prev) =>
            prev.map((c) => (c.id === clientId ? response.data! : c))
          );
        }

        return response.data || null;
      } catch {
        setError('의뢰인 연락처 수정 중 오류가 발생했습니다.');
        return null;
      }
    },
    []
  );

  // Delete a client contact
  const remove = useCallback(
    async (clientId: string): Promise<boolean> => {
      try {
        const response = await deleteClientContact(clientId);

        if (response.error) {
          setError(response.error);
          return false;
        }

        // Remove from local state
        setContacts((prev) => prev.filter((c) => c.id !== clientId));
        setTotal((prev) => Math.max(0, prev - 1));

        return true;
      } catch {
        setError('의뢰인 연락처 삭제 중 오류가 발생했습니다.');
        return false;
      }
    },
    []
  );

  // Fetch a single contact by ID
  const fetchContact = useCallback(
    async (clientId: string): Promise<ClientContact | null> => {
      try {
        const response = await getClientContact(clientId);

        if (response.error) {
          setError(response.error);
          return null;
        }

        return response.data || null;
      } catch {
        setError('의뢰인 연락처를 불러오는 중 오류가 발생했습니다.');
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

export default useClientContacts;
