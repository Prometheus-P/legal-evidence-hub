/**
 * ComposeMessage Component
 * 011-production-bug-fixes Feature - US2 (T045)
 *
 * Form for composing a new direct message.
 */

'use client';

import React, { useState } from 'react';
import type { DirectMessageCreate } from '@/types/message';

interface ComposeMessageProps {
  onSend: (data: DirectMessageCreate) => Promise<void>;
  onCancel: () => void;
  isSending?: boolean;
  /** Pre-filled recipient ID for reply */
  defaultRecipientId?: string;
  /** Pre-filled subject for reply */
  defaultSubject?: string;
}

export function ComposeMessage({
  onSend,
  onCancel,
  isSending = false,
  defaultRecipientId = '',
  defaultSubject = '',
}: ComposeMessageProps) {
  const [recipientId, setRecipientId] = useState(defaultRecipientId);
  const [subject, setSubject] = useState(defaultSubject);
  const [content, setContent] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!recipientId.trim()) {
      newErrors.recipientId = '받는 사람을 입력하세요';
    }
    if (!subject.trim()) {
      newErrors.subject = '제목을 입력하세요';
    }
    if (!content.trim()) {
      newErrors.content = '내용을 입력하세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    await onSend({
      recipientId: recipientId.trim(),
      subject: subject.trim(),
      content: content.trim(),
    });
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">새 메시지</h2>
        <button
          type="button"
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600"
          aria-label="닫기"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          {/* Recipient */}
          <div>
            <label
              htmlFor="recipientId"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              받는 사람 <span className="text-red-500">*</span>
            </label>
            <input
              id="recipientId"
              type="text"
              value={recipientId}
              onChange={(e) => setRecipientId(e.target.value)}
              placeholder="사용자 ID 또는 이메일"
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                errors.recipientId
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
              }`}
            />
            {errors.recipientId && (
              <p className="mt-1 text-xs text-red-500">{errors.recipientId}</p>
            )}
          </div>

          {/* Subject */}
          <div>
            <label
              htmlFor="subject"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              제목 <span className="text-red-500">*</span>
            </label>
            <input
              id="subject"
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="메시지 제목"
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                errors.subject
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
              }`}
            />
            {errors.subject && (
              <p className="mt-1 text-xs text-red-500">{errors.subject}</p>
            )}
          </div>

          {/* Content */}
          <div className="flex-1">
            <label
              htmlFor="content"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              내용 <span className="text-red-500">*</span>
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="메시지 내용을 입력하세요"
              rows={10}
              className={`w-full resize-none rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                errors.content
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
              }`}
            />
            {errors.content && (
              <p className="mt-1 text-xs text-red-500">{errors.content}</p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-gray-200 p-4">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            disabled={isSending}
          >
            취소
          </button>
          <button
            type="submit"
            disabled={isSending}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {isSending ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                보내는 중...
              </span>
            ) : (
              '보내기'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ComposeMessage;
