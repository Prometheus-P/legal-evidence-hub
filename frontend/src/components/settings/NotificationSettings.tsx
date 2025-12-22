/**
 * NotificationSettings Component
 * 005-lawyer-portal-pages Feature - US4 (T054)
 *
 * Form for managing notification preferences.
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import type { NotificationSettings as NotificationSettingsType, NotificationUpdateRequest, NotificationTypes } from '@/types/settings';

type NotificationTypeKey = keyof NotificationTypes;

interface NotificationSettingsProps {
  notifications: NotificationSettingsType | null;
  loading?: boolean;
  updating?: boolean;
  onSubmit: (data: NotificationUpdateRequest) => Promise<boolean>;
}

const NOTIFICATION_TYPES: Array<{ key: NotificationTypeKey; label: string; description: string }> = [
  { key: 'new_evidence', label: '새 증거 업로드', description: '새 증거가 업로드되면 알림을 받습니다.' },
  { key: 'case_updates', label: '케이스 업데이트', description: '케이스 상태가 변경되면 알림을 받습니다.' },
  { key: 'messages', label: '새 메시지', description: '새 메시지가 도착하면 알림을 받습니다.' },
  { key: 'calendar_reminders', label: '일정 알림', description: '예정된 일정에 대한 알림을 받습니다.' },
  { key: 'billing_alerts', label: '청구 알림', description: '청구 관련 알림을 받습니다.' },
];

const FREQUENCIES = [
  { value: 'immediate', label: '즉시' },
  { value: 'daily', label: '매일 요약' },
  { value: 'weekly', label: '매주 요약' },
] as const;

export function NotificationSettingsComponent({
  notifications,
  loading,
  updating,
  onSubmit,
}: NotificationSettingsProps) {
  const [formData, setFormData] = useState<NotificationUpdateRequest>({
    email_enabled: true,
    push_enabled: false,
    frequency: 'daily',
    notification_types: {
      new_evidence: true,
      case_updates: true,
      messages: true,
      calendar_reminders: true,
      billing_alerts: false,
    },
  });

  // Initialize form data when notifications load
  useEffect(() => {
    if (notifications) {
      setFormData({
        email_enabled: notifications.email_enabled,
        push_enabled: notifications.push_enabled,
        frequency: notifications.frequency,
        notification_types: { ...notifications.notification_types },
      });
    }
  }, [notifications]);

  const handleToggle = (field: 'email_enabled' | 'push_enabled') => {
    setFormData((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const handleFrequencyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData((prev) => ({
      ...prev,
      frequency: e.target.value as 'immediate' | 'daily' | 'weekly',
    }));
  };

  const handleTypeToggle = (key: NotificationTypeKey) => {
    setFormData((prev) => ({
      ...prev,
      notification_types: {
        ...prev.notification_types,
        [key]: !prev.notification_types?.[key],
      },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await onSubmit(formData);
    if (result) {
      toast.success('알림 설정이 저장되었습니다.');
    } else {
      toast.error('알림 설정 저장에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-16 bg-gray-200 rounded" />
        <div className="h-16 bg-gray-200 rounded" />
        <div className="h-10 bg-gray-200 rounded" />
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 bg-gray-200 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Main Toggles */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-[var(--color-text-primary)]">
          알림 방식
        </h3>

        {/* Email Toggle */}
        <div className="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border-default)] bg-white">
          <div>
            <p className="font-medium text-[var(--color-text-primary)]">이메일 알림</p>
            <p className="text-sm text-[var(--color-text-secondary)]">
              중요한 업데이트를 이메일로 받습니다.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={formData.email_enabled}
            onClick={() => handleToggle('email_enabled')}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              formData.email_enabled ? 'bg-[var(--color-primary)]' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.email_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Push Toggle */}
        <div className="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border-default)] bg-white">
          <div>
            <p className="font-medium text-[var(--color-text-primary)]">푸시 알림</p>
            <p className="text-sm text-[var(--color-text-secondary)]">
              브라우저 푸시 알림을 받습니다.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={formData.push_enabled}
            onClick={() => handleToggle('push_enabled')}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              formData.push_enabled ? 'bg-[var(--color-primary)]' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.push_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Frequency */}
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-[var(--color-text-primary)]">
          알림 빈도
        </h3>
        <select
          value={formData.frequency}
          onChange={handleFrequencyChange}
          className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent bg-white"
        >
          {FREQUENCIES.map((freq) => (
            <option key={freq.value} value={freq.value}>
              {freq.label}
            </option>
          ))}
        </select>
      </div>

      {/* Notification Types */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-[var(--color-text-primary)]">
          알림 유형
        </h3>
        <div className="space-y-2">
          {NOTIFICATION_TYPES.map((type) => (
            <div
              key={type.key}
              className="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border-default)] bg-white"
            >
              <div>
                <p className="font-medium text-[var(--color-text-primary)]">{type.label}</p>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {type.description}
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={formData.notification_types?.[type.key] ?? false}
                onClick={() => handleTypeToggle(type.key)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  formData.notification_types?.[type.key]
                    ? 'bg-[var(--color-primary)]'
                    : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    formData.notification_types?.[type.key]
                      ? 'translate-x-6'
                      : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={updating}
          className="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {updating ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              저장 중...
            </span>
          ) : (
            '저장'
          )}
        </button>
      </div>
    </form>
  );
}
