/**
 * NotificationDropdown Component
 * 011-production-bug-fixes Feature - US2 (T040)
 *
 * Dropdown menu showing notifications with mark-as-read functionality.
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { NotificationBadge } from './NotificationBadge';
import { NotificationItem } from './NotificationItem';
import { useNotifications } from '@/hooks/useNotifications';

interface NotificationDropdownProps {
  className?: string;
}

export function NotificationDropdown({ className = '' }: NotificationDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const {
    notifications,
    unreadCount,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    refetch,
  } = useNotifications({ limit: 10 });

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
    if (!isOpen) {
      refetch();
    }
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const handleNotificationClick = async (notificationId: string) => {
    await markAsRead(notificationId);
  };

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      <NotificationBadge count={unreadCount} onClick={handleToggle} />

      {isOpen && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-lg">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-100 dark:border-neutral-700 px-4 py-3">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">알림</h3>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={handleMarkAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                모두 읽음
              </button>
            )}
          </div>

          {/* Content */}
          <div className="max-h-96 overflow-y-auto">
            {isLoading && (
              <div className="flex items-center justify-center py-8">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
              </div>
            )}

            {error && (
              <div className="px-4 py-8 text-center text-sm text-red-500">
                {error}
              </div>
            )}

            {!isLoading && !error && notifications.length === 0 && (
              <div className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">
                알림이 없습니다
              </div>
            )}

            {!isLoading &&
              !error &&
              notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onClick={() => handleNotificationClick(notification.id)}
                />
              ))}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-100 dark:border-neutral-700 px-4 py-2">
            <a
              href="/lawyer/notifications"
              className="block text-center text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-200"
            >
              모든 알림 보기
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationDropdown;
