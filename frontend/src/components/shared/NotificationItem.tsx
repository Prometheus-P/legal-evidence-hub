/**
 * NotificationItem Component
 * 011-production-bug-fixes Feature - US2 (T041)
 *
 * Individual notification item in the dropdown list.
 */

'use client';

import React from 'react';
import type { Notification } from '@/types/notification';

interface NotificationItemProps {
  notification: Notification;
  onClick?: () => void;
}

function getTypeIcon(type: Notification['type']) {
  switch (type) {
    case 'case_update':
      return (
        <svg
          className="h-5 w-5 text-blue-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      );
    case 'message':
      return (
        <svg
          className="h-5 w-5 text-green-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      );
    case 'system':
      return (
        <svg
          className="h-5 w-5 text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    default:
      return null;
  }
}

function formatTimeAgo(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) {
    return '방금 전';
  } else if (diffMins < 60) {
    return `${diffMins}분 전`;
  } else if (diffHours < 24) {
    return `${diffHours}시간 전`;
  } else if (diffDays < 7) {
    return `${diffDays}일 전`;
  } else {
    return date.toLocaleDateString('ko-KR');
  }
}

export function NotificationItem({
  notification,
  onClick,
}: NotificationItemProps) {
  const { type, title, content, isRead, createdAt } = notification;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
        !isRead ? 'bg-blue-50' : ''
      }`}
    >
      <div className="flex-shrink-0 pt-0.5">{getTypeIcon(type)}</div>
      <div className="min-w-0 flex-1">
        <p
          className={`text-sm ${
            !isRead ? 'font-semibold text-gray-900' : 'text-gray-700'
          }`}
        >
          {title}
        </p>
        <p className="mt-0.5 line-clamp-2 text-xs text-gray-500">{content}</p>
        <p className="mt-1 text-xs text-gray-400">{formatTimeAgo(createdAt)}</p>
      </div>
      {!isRead && (
        <div className="flex-shrink-0">
          <span className="block h-2 w-2 rounded-full bg-blue-500" />
        </div>
      )}
    </button>
  );
}

export default NotificationItem;
