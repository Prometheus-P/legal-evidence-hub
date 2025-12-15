/**
 * NotificationBadge Component
 * 011-production-bug-fixes Feature - US2 (T039)
 *
 * Badge showing unread notification count.
 */

'use client';

import React from 'react';

interface NotificationBadgeProps {
  count: number;
  maxCount?: number;
  onClick?: () => void;
  className?: string;
}

export function NotificationBadge({
  count,
  maxCount = 99,
  onClick,
  className = '',
}: NotificationBadgeProps) {
  const displayCount = count > maxCount ? `${maxCount}+` : count.toString();
  const hasUnread = count > 0;
  const ariaLabel = hasUnread ? `${count}개의 읽지 않은 알림` : '알림';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative inline-flex items-center justify-center ${className}`}
      aria-label={ariaLabel}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6 text-gray-600 hover:text-gray-800"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      {hasUnread && (
        <span
          className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-bold text-white"
          aria-hidden="true"
        >
          {displayCount}
        </span>
      )}
    </button>
  );
}

export default NotificationBadge;
