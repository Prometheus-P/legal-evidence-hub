/**
 * MessageList Component
 * 011-production-bug-fixes Feature - US2 (T043)
 *
 * List of direct messages with folder tabs (inbox/sent).
 */

'use client';

import React from 'react';
import type { DirectMessageSummary } from '@/types/message';

interface MessageListProps {
  messages: DirectMessageSummary[];
  selectedId?: string;
  isLoading?: boolean;
  folder: 'inbox' | 'sent';
  onFolderChange: (folder: 'inbox' | 'sent') => void;
  onSelect: (message: DirectMessageSummary) => void;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  } else if (diffDays === 1) {
    return '어제';
  } else if (diffDays < 7) {
    return `${diffDays}일 전`;
  } else {
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  }
}

export function MessageList({
  messages,
  selectedId,
  isLoading = false,
  folder,
  onFolderChange,
  onSelect,
}: MessageListProps) {
  return (
    <div className="flex h-full flex-col border-r border-gray-200 bg-white">
      {/* Folder Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          type="button"
          onClick={() => onFolderChange('inbox')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            folder === 'inbox'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          받은 메시지
        </button>
        <button
          type="button"
          onClick={() => onFolderChange('sent')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
            folder === 'sent'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          보낸 메시지
        </button>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          </div>
        )}

        {!isLoading && messages.length === 0 && (
          <div className="py-12 text-center text-sm text-gray-500">
            {folder === 'inbox' ? '받은 메시지가 없습니다' : '보낸 메시지가 없습니다'}
          </div>
        )}

        {!isLoading &&
          messages.map((message) => (
            <button
              key={message.id}
              type="button"
              onClick={() => onSelect(message)}
              className={`w-full border-b border-gray-100 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
                selectedId === message.id ? 'bg-blue-50' : ''
              } ${!message.isRead && folder === 'inbox' ? 'bg-blue-50/50' : ''}`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`text-sm ${
                    !message.isRead && folder === 'inbox'
                      ? 'font-semibold text-gray-900'
                      : 'text-gray-700'
                  }`}
                >
                  {folder === 'inbox' ? message.senderName : message.recipientName}
                </span>
                <span className="text-xs text-gray-400">
                  {formatDate(message.createdAt)}
                </span>
              </div>
              <p
                className={`mt-0.5 text-sm ${
                  !message.isRead && folder === 'inbox'
                    ? 'font-medium text-gray-800'
                    : 'text-gray-600'
                }`}
              >
                {message.subject}
              </p>
              <p className="mt-0.5 line-clamp-1 text-xs text-gray-400">
                {message.preview}
              </p>
              {!message.isRead && folder === 'inbox' && (
                <span className="mt-1 inline-block h-2 w-2 rounded-full bg-blue-500" />
              )}
            </button>
          ))}
      </div>
    </div>
  );
}

export default MessageList;
