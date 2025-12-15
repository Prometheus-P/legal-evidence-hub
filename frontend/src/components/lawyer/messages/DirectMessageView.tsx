/**
 * DirectMessageView Component
 * 011-production-bug-fixes Feature - US2 (T044)
 *
 * View for displaying a single direct message with reply option.
 */

'use client';

import React, { useState } from 'react';
import type { DirectMessage, DirectMessageCreate } from '@/types/message';

interface DirectMessageViewProps {
  message: DirectMessage | null;
  onReply?: (data: DirectMessageCreate) => void;
  onDelete?: (messageId: string) => void;
  onCompose?: () => void;
  isDeleting?: boolean;
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function DirectMessageView({
  message,
  onReply,
  onDelete,
  onCompose,
  isDeleting = false,
}: DirectMessageViewProps) {
  const [isReplying, setIsReplying] = useState(false);
  const [replyContent, setReplyContent] = useState('');

  if (!message) {
    return (
      <div className="flex h-full flex-col items-center justify-center bg-gray-50 text-gray-500">
        <svg
          className="mb-4 h-16 w-16 text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
        <p className="mb-4 text-lg font-medium text-gray-700">메시지를 선택하세요</p>
        <p className="mb-6 text-sm text-gray-400">
          왼쪽 목록에서 메시지를 선택하거나 새 메시지를 작성하세요
        </p>
        {onCompose && (
          <button
            type="button"
            onClick={onCompose}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            새 메시지 작성
          </button>
        )}
      </div>
    );
  }

  const handleReply = () => {
    if (!replyContent.trim() || !onReply) return;

    onReply({
      recipientId: message.senderId,
      subject: `Re: ${message.subject}`,
      content: replyContent,
    });

    setReplyContent('');
    setIsReplying(false);
  };

  const handleDelete = () => {
    if (window.confirm('이 메시지를 삭제하시겠습니까?') && onDelete) {
      onDelete(message.id);
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">{message.subject}</h2>
        <div className="mt-2 flex items-center justify-between text-sm text-gray-500">
          <div>
            <span className="font-medium text-gray-700">
              보낸 사람: {message.senderName}
            </span>
            <span className="mx-2">•</span>
            <span>받는 사람: {message.recipientName}</span>
          </div>
          <span>{formatDateTime(message.createdAt)}</span>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="whitespace-pre-wrap text-gray-700">{message.content}</div>
      </div>

      {/* Actions */}
      <div className="border-t border-gray-200 p-4">
        {isReplying ? (
          <div className="space-y-3">
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="답장 내용을 입력하세요..."
              className="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              rows={4}
              autoFocus
            />
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setIsReplying(false);
                  setReplyContent('');
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                취소
              </button>
              <button
                type="button"
                onClick={handleReply}
                disabled={!replyContent.trim()}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                보내기
              </button>
            </div>
          </div>
        ) : (
          <div className="flex justify-between">
            <button
              type="button"
              onClick={() => setIsReplying(true)}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
                />
              </svg>
              답장
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="flex items-center gap-2 rounded-lg border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              {isDeleting ? '삭제 중...' : '삭제'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default DirectMessageView;
