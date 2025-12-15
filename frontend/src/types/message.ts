/**
 * Message types for real-time communication
 * 003-role-based-ui Feature - US6
 */

// ============== API Types ==============

export interface MessageSender {
  id: string;
  name: string;
  role: string;
}

export interface Message {
  id: string;
  case_id: string;
  sender: MessageSender;
  recipient_id: string;
  content: string;
  attachments?: string[];
  read_at?: string;
  created_at: string;
  is_mine: boolean;
}

export interface ConversationSummary {
  case_id: string;
  case_title: string;
  other_user: {
    id: string;
    name: string;
    role: string;
  };
  last_message: string;
  last_message_at: string;
  unread_count: number;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
  has_more: boolean;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total_unread: number;
}

export interface UnreadCountResponse {
  total: number;
  by_case: Record<string, number>;
}

// ============== Request Types ==============

export interface SendMessageRequest {
  case_id: string;
  recipient_id: string;
  content: string;
  attachments?: string[];
}

export interface MarkReadRequest {
  message_ids: string[];
}

// ============== WebSocket Types ==============

export type WebSocketMessageType =
  | 'message'
  | 'read'
  | 'typing'
  | 'ping'
  | 'new_message'
  | 'message_sent'
  | 'read_confirmed'
  | 'read_receipt'
  | 'offline_messages'
  | 'presence'
  | 'pong'
  | 'error';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType;
  payload: T;
}

export interface TypingPayload {
  user_id: string;
  case_id: string;
  is_typing: boolean;
}

export interface PresencePayload {
  user_id: string;
  status: 'online' | 'away' | 'offline';
}

export interface OfflineMessagesPayload {
  messages: Message[];
}

// ============== UI State Types ==============

export interface MessageState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
}

export interface ConversationState {
  conversations: ConversationSummary[];
  totalUnread: number;
  isLoading: boolean;
  error: string | null;
}

export interface TypingIndicator {
  userId: string;
  caseId: string;
  timestamp: number;
}

// ============== Direct Message Types (US2 - Lawyer Portal) ==============

/**
 * Direct message between users (not case-specific)
 * Used in /lawyer/messages page
 */
export interface DirectMessage {
  id: string;
  senderId: string;
  senderName: string;
  recipientId: string;
  recipientName: string;
  subject: string;
  content: string;
  isRead: boolean;
  createdAt: string; // ISO 8601
  readAt?: string;
}

export interface DirectMessageSummary {
  id: string;
  senderId: string;
  senderName: string;
  recipientId: string;
  recipientName: string;
  subject: string;
  preview: string; // First 100 chars of content
  isRead: boolean;
  createdAt: string;
}

export interface DirectMessageListResponse {
  messages: DirectMessageSummary[];
  total: number;
  page: number;
  limit: number;
}

export interface DirectMessageQueryParams {
  folder: 'inbox' | 'sent';
  page?: number;
  limit?: number;
}

export interface DirectMessageCreate {
  recipientId: string;
  subject: string;
  content: string;
}

export interface DirectMessageState {
  messages: DirectMessageSummary[];
  total: number;
  currentMessage: DirectMessage | null;
  isLoading: boolean;
  error: string | null;
}
