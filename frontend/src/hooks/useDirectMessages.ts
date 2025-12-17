/**
 * useDirectMessages Hook
 * 011-production-bug-fixes Feature - US2 (T036)
 *
 * Hook for direct message CRUD operations.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getDirectMessages,
  getDirectMessage,
  sendDirectMessage,
  deleteDirectMessage,
  markDirectMessageAsRead,
} from '@/lib/api/messages';
import type {
  DirectMessage,
  DirectMessageSummary,
  DirectMessageCreate,
  DirectMessageQueryParams,
} from '@/types/message';

interface UseDirectMessagesOptions {
  folder?: 'inbox' | 'sent';
  limit?: number;
  autoFetch?: boolean;
}

interface UseDirectMessagesReturn {
  messages: DirectMessageSummary[];
  total: number;
  page: number;
  isLoading: boolean;
  error: string | null;
  send: (data: DirectMessageCreate) => Promise<DirectMessage | null>;
  remove: (messageId: string) => Promise<boolean>;
  markAsRead: (messageId: string) => Promise<void>;
  fetchMessage: (messageId: string) => Promise<DirectMessage | null>;
  refetch: () => Promise<void>;
  setPage: (page: number) => void;
}

export function useDirectMessages(
  options: UseDirectMessagesOptions = {}
): UseDirectMessagesReturn {
  const { folder = 'inbox', limit = 20, autoFetch = true } = options;

  const [messages, setMessages] = useState<DirectMessageSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = useCallback(async () => {
    setError(null);
    setIsLoading(true);

    try {
      const params: DirectMessageQueryParams = { folder, page, limit };
      const response = await getDirectMessages(params);

      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setMessages(response.data.messages);
        setTotal(response.data.total);
      }
    } catch {
      setError('메시지를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [folder, page, limit]);

  // Send a new message
  const send = useCallback(
    async (data: DirectMessageCreate): Promise<DirectMessage | null> => {
      try {
        const response = await sendDirectMessage(data);

        if (response.error) {
          setError(response.error);
          return null;
        }

        // Refresh sent folder if viewing it
        if (folder === 'sent' && response.data) {
          await fetchMessages();
        }

        return response.data || null;
      } catch {
        setError('메시지 전송 중 오류가 발생했습니다.');
        return null;
      }
    },
    [folder, fetchMessages]
  );

  // Delete a message
  const remove = useCallback(
    async (messageId: string): Promise<boolean> => {
      try {
        const response = await deleteDirectMessage(messageId);

        if (response.error) {
          setError(response.error);
          return false;
        }

        // Remove from local state
        setMessages((prev) => prev.filter((m) => m.id !== messageId));
        setTotal((prev) => Math.max(0, prev - 1));

        return true;
      } catch {
        setError('메시지 삭제 중 오류가 발생했습니다.');
        return false;
      }
    },
    []
  );

  // Mark message as read
  const markAsRead = useCallback(async (messageId: string) => {
    try {
      const response = await markDirectMessageAsRead(messageId);

      if (response.error) {
        setError(response.error);
        return;
      }

      // Update local state
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, isRead: true, readAt: new Date().toISOString() } : m
        )
      );
    } catch {
      setError('읽음 처리 중 오류가 발생했습니다.');
    }
  }, []);

  // Fetch a single message by ID
  const fetchMessage = useCallback(
    async (messageId: string): Promise<DirectMessage | null> => {
      try {
        const response = await getDirectMessage(messageId);

        if (response.error) {
          setError(response.error);
          return null;
        }

        return response.data || null;
      } catch {
        setError('메시지를 불러오는 중 오류가 발생했습니다.');
        return null;
      }
    },
    []
  );

  // Initial fetch
  useEffect(() => {
    if (autoFetch) {
      fetchMessages();
    }
  }, [fetchMessages, autoFetch]);

  return {
    messages,
    total,
    page,
    isLoading,
    error,
    send,
    remove,
    markAsRead,
    fetchMessage,
    refetch: fetchMessages,
    setPage,
  };
}

export default useDirectMessages;
