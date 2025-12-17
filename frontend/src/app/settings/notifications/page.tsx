/**
 * Notification Settings Page
 * 005-lawyer-portal-pages Feature - US4 (T057)
 *
 * Page for managing notification preferences.
 */

'use client';

import Link from 'next/link';
import { useSettings } from '@/hooks/useSettings';
import { NotificationSettingsComponent } from '@/components/settings/NotificationSettings';

export default function NotificationSettingsPage() {
  const { notifications, isLoading, isUpdating, error, updateNotifications } = useSettings();

  return (
    <div className="max-w-2xl mx-auto py-6 px-4">
      {/* Breadcrumb */}
      <nav className="mb-6">
        <ol className="flex items-center gap-2 text-sm">
          <li>
            <Link
              href="/settings"
              className="text-[var(--color-text-secondary)] hover:text-[var(--color-primary)]"
            >
              설정
            </Link>
          </li>
          <li className="text-[var(--color-text-secondary)]">/</li>
          <li className="text-[var(--color-text-primary)] font-medium">알림</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">알림 설정</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          이메일 및 푸시 알림을 설정하고 관리합니다.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* Notification Settings */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
        <NotificationSettingsComponent
          notifications={notifications}
          loading={isLoading}
          updating={isUpdating}
          onSubmit={updateNotifications}
        />
      </div>
    </div>
  );
}
