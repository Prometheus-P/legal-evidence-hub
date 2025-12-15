/**
 * Message API client
 * 003-role-based-ui Feature - US6
 */

import { apiClient, ApiResponse } from './client';
import { logger } from '@/lib/logger';
import type {
  Message,
  MessageListResponse,
  ConversationListResponse,
  UnreadCountResponse,
  SendMessageRequest,
  MarkReadRequest,
  DirectMessage,
  DirectMessageSummary,
  DirectMessageListResponse,
  DirectMessageQueryParams,
  DirectMessageCreate,
} from '@/types/message';

const BASE_PATH = '/messages';

interface WebSocketTokenResponse {
  token: string;
  expires_in: number;
}

/**
 * Get list of conversations for the current user
 */
export async function getConversations(): Promise<ApiResponse<ConversationListResponse>> {
  return apiClient.get<ConversationListResponse>(`${BASE_PATH}/conversations`);
}

/**
 * Get unread message count
 */
export async function getUnreadCount(): Promise<ApiResponse<UnreadCountResponse>> {
  return apiClient.get<UnreadCountResponse>(`${BASE_PATH}/unread`);
}

/**
 * Get messages for a case
 */
export async function getMessages(
  caseId: string,
  options?: {
    otherUserId?: string;
    limit?: number;
    beforeId?: string;
  }
): Promise<ApiResponse<MessageListResponse>> {
  const params = new URLSearchParams();
  if (options?.otherUserId) params.set('other_user_id', options.otherUserId);
  if (options?.limit) params.set('limit', String(options.limit));
  if (options?.beforeId) params.set('before_id', options.beforeId);

  const query = params.toString();
  const url = `${BASE_PATH}/${caseId}${query ? `?${query}` : ''}`;

  return apiClient.get<MessageListResponse>(url);
}

/**
 * Send a new message
 */
export async function sendMessage(
  data: SendMessageRequest
): Promise<ApiResponse<Message>> {
  return apiClient.post<Message>(BASE_PATH, data);
}

/**
 * Mark messages as read
 */
export async function markMessagesRead(
  messageIds: string[]
): Promise<ApiResponse<{ marked_count: number }>> {
  const body: MarkReadRequest = { message_ids: messageIds };
  return apiClient.post<{ marked_count: number }>(`${BASE_PATH}/read`, body);
}

/**
 * Issue a short-lived token for WebSocket authentication
 */
export async function getWebSocketToken(): Promise<ApiResponse<WebSocketTokenResponse>> {
  return apiClient.get<WebSocketTokenResponse>(`${BASE_PATH}/ws-token`);
}

// ============== WebSocket Client ==============

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface MessageWebSocketCallbacks {
  onMessage?: (message: Message) => void;
  onTyping?: (data: { user_id: string; case_id: string; is_typing: boolean }) => void;
  onReadReceipt?: (messageIds: string[]) => void;
  onOfflineMessages?: (messages: Message[]) => void;
  onStatusChange?: (status: WebSocketStatus) => void;
  onError?: (error: string) => void;
}

/**
 * Create a WebSocket connection for real-time messaging
 */
const buildSocketUrl = (token: string): string => {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  const wsProtocol = apiBaseUrl.startsWith('https') ? 'wss' : 'ws';
  const wsHost = apiBaseUrl.replace(/^https?:\/\//, '');
  return `${wsProtocol}://${wsHost}${BASE_PATH}/ws?token=${encodeURIComponent(token)}`;
};

export function buildWebSocketUrl(token: string): string {
  return buildSocketUrl(token);
}

export function createMessageWebSocket(
  token: string,
  callbacks: MessageWebSocketCallbacks
): {
  send: (type: string, payload: unknown) => void;
  sendMessage: (caseId: string, recipientId: string, content: string, attachments?: string[]) => void;
  sendTyping: (caseId: string, recipientId: string, isTyping: boolean) => void;
  markRead: (messageIds: string[]) => void;
  close: () => void;
} {
  const wsUrl = buildSocketUrl(token);
  let ws: WebSocket | null = null;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 5;
  let reconnectTimeout: NodeJS.Timeout | null = null;

  const connect = () => {
    callbacks.onStatusChange?.('connecting');

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      reconnectAttempts = 0;
      callbacks.onStatusChange?.('connected');
    };

    ws.onclose = (event) => {
      callbacks.onStatusChange?.('disconnected');

      // Attempt to reconnect if not a normal closure
      if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        reconnectTimeout = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      callbacks.onStatusChange?.('error');
      callbacks.onError?.('WebSocket connection error');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const { type, payload } = data;

        switch (type) {
          case 'new_message':
          case 'message_sent':
            callbacks.onMessage?.(payload as Message);
            break;

          case 'typing':
            callbacks.onTyping?.(payload);
            break;

          case 'read_receipt':
          case 'read_confirmed':
            callbacks.onReadReceipt?.(payload.message_ids);
            break;

          case 'offline_messages':
            callbacks.onOfflineMessages?.(payload.messages);
            break;

          case 'error':
            callbacks.onError?.(payload.message);
            break;

          case 'pong':
            // Keep-alive response, no action needed
            break;
        }
      } catch {
        logger.error('Failed to parse WebSocket message');
      }
    };
  };

  connect();

  const send = (type: string, payload: unknown) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type, payload }));
    }
  };

  return {
    send,

    sendMessage: (caseId: string, recipientId: string, content: string, attachments?: string[]) => {
      send('message', {
        case_id: caseId,
        recipient_id: recipientId,
        content,
        attachments,
      });
    },

    sendTyping: (caseId: string, recipientId: string, isTyping: boolean) => {
      send('typing', {
        case_id: caseId,
        recipient_id: recipientId,
        is_typing: isTyping,
      });
    },

    markRead: (messageIds: string[]) => {
      send('read', { message_ids: messageIds });
    },

    close: () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close(1000, 'User closed connection');
        ws = null;
      }
    },
  };
}

// ============== Direct Message API (US2 - Lawyer Portal) ==============

const DIRECT_MESSAGE_PATH = '/direct-messages';

/**
 * Get list of direct messages (inbox or sent)
 */
export async function getDirectMessages(
  params?: DirectMessageQueryParams
): Promise<ApiResponse<DirectMessageListResponse>> {
  const searchParams = new URLSearchParams();

  if (params?.folder) {
    searchParams.append('folder', params.folder);
  }
  if (params?.page) {
    searchParams.append('page', String(params.page));
  }
  if (params?.limit) {
    searchParams.append('limit', String(params.limit));
  }

  const queryString = searchParams.toString();
  const url = queryString ? `${DIRECT_MESSAGE_PATH}?${queryString}` : DIRECT_MESSAGE_PATH;

  return apiClient.get<DirectMessageListResponse>(url);
}

/**
 * Get a single direct message by ID
 */
export async function getDirectMessage(
  messageId: string
): Promise<ApiResponse<DirectMessage>> {
  return apiClient.get<DirectMessage>(`${DIRECT_MESSAGE_PATH}/${messageId}`);
}

/**
 * Send a new direct message
 */
export async function sendDirectMessage(
  data: DirectMessageCreate
): Promise<ApiResponse<DirectMessage>> {
  return apiClient.post<DirectMessage>(DIRECT_MESSAGE_PATH, data);
}

/**
 * Delete a direct message (soft delete for current user)
 */
export async function deleteDirectMessage(
  messageId: string
): Promise<ApiResponse<{ success: boolean }>> {
  return apiClient.delete<{ success: boolean }>(`${DIRECT_MESSAGE_PATH}/${messageId}`);
}

/**
 * Mark a direct message as read
 */
export async function markDirectMessageAsRead(
  messageId: string
): Promise<ApiResponse<DirectMessage>> {
  return apiClient.patch<DirectMessage>(`${DIRECT_MESSAGE_PATH}/${messageId}/read`, {});
}

// Re-export direct message types
export type {
  DirectMessage,
  DirectMessageSummary,
  DirectMessageListResponse,
  DirectMessageQueryParams,
  DirectMessageCreate,
};
