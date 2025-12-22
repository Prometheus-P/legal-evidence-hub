/**
 * ProfileForm Component
 * 005-lawyer-portal-pages Feature - US4 (T053)
 *
 * Form for editing user profile settings.
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import type { UserProfile, ProfileUpdateRequest } from '@/types/settings';

interface ProfileFormProps {
  profile: UserProfile | null;
  loading?: boolean;
  updating?: boolean;
  onSubmit: (data: ProfileUpdateRequest) => Promise<boolean>;
}

const TIMEZONES = [
  { value: 'Asia/Seoul', label: '서울 (KST, UTC+9)' },
  { value: 'Asia/Tokyo', label: '도쿄 (JST, UTC+9)' },
  { value: 'America/New_York', label: '뉴욕 (EST, UTC-5)' },
  { value: 'America/Los_Angeles', label: '로스앤젤레스 (PST, UTC-8)' },
  { value: 'Europe/London', label: '런던 (GMT, UTC+0)' },
];

const LANGUAGES = [
  { value: 'ko', label: '한국어' },
  { value: 'en', label: 'English' },
];

export function ProfileForm({ profile, loading, updating, onSubmit }: ProfileFormProps) {
  const [formData, setFormData] = useState<ProfileUpdateRequest>({
    display_name: '',
    phone: '',
    timezone: 'Asia/Seoul',
    language: 'ko',
  });
  const [errors, setErrors] = useState<{ phone?: string }>({});

  // Initialize form data when profile loads
  useEffect(() => {
    if (profile) {
      setFormData({
        display_name: profile.display_name || '',
        phone: profile.phone || '',
        timezone: profile.timezone || 'Asia/Seoul',
        language: profile.language || 'ko',
      });
    }
  }, [profile]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (name === 'phone') {
      setErrors((prev) => ({ ...prev, phone: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: { phone?: string } = {};

    // Phone number validation (Korean format)
    if (formData.phone && !/^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/.test(formData.phone.replace(/-/g, ''))) {
      newErrors.phone = '올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('입력 정보를 확인해주세요.');
      return;
    }

    const result = await onSubmit(formData);
    if (result) {
      toast.success('프로필이 저장되었습니다.');
    } else {
      toast.error('프로필 저장에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 bg-gray-200 rounded" />
        <div className="h-10 bg-gray-200 rounded" />
        <div className="h-10 bg-gray-200 rounded" />
        <div className="h-10 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        {/* Display Name */}
        <div>
          <label
            htmlFor="display_name"
            className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
          >
            이름
          </label>
          <input
            type="text"
            id="display_name"
            name="display_name"
            value={formData.display_name}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
            placeholder="이름을 입력하세요"
          />
        </div>

        {/* Email (readonly) */}
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
          >
            이메일
          </label>
          <input
            type="email"
            id="email"
            value={profile?.email || ''}
            disabled
            className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] bg-gray-50 text-[var(--color-text-secondary)] cursor-not-allowed"
          />
          <p className="mt-1 text-xs text-[var(--color-text-secondary)]">
            이메일은 변경할 수 없습니다.
          </p>
        </div>

        {/* Phone */}
        <div>
          <label
            htmlFor="phone"
            className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
          >
            전화번호
          </label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            className={`w-full px-4 py-2 rounded-lg border ${
              errors.phone
                ? 'border-red-300 focus:ring-red-500'
                : 'border-[var(--color-border-default)] focus:ring-[var(--color-primary)]'
            } focus:outline-none focus:ring-2 focus:border-transparent`}
            placeholder="010-1234-5678"
          />
          {errors.phone && (
            <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
          )}
        </div>

        {/* Timezone */}
        <div>
          <label
            htmlFor="timezone"
            className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
          >
            시간대
          </label>
          <select
            id="timezone"
            name="timezone"
            value={formData.timezone}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent bg-white"
          >
            {TIMEZONES.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label}
              </option>
            ))}
          </select>
        </div>

        {/* Language */}
        <div>
          <label
            htmlFor="language"
            className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
          >
            언어
          </label>
          <select
            id="language"
            name="language"
            value={formData.language}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg border border-[var(--color-border-default)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent bg-white"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
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
