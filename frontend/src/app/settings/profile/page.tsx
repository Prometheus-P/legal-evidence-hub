/**
 * Profile Settings Page
 * 005-lawyer-portal-pages Feature - US4 (T056)
 *
 * Page for editing user profile settings.
 */

'use client';

import Link from 'next/link';
import { useSettings } from '@/hooks/useSettings';
import { ProfileForm } from '@/components/settings/ProfileForm';

export default function ProfileSettingsPage() {
  const { profile, isLoading, isUpdating, error, updateProfile } = useSettings();

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
          <li className="text-[var(--color-text-primary)] font-medium">프로필</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">프로필 설정</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          이름, 연락처, 시간대 등 개인 정보를 관리합니다.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* Profile Form */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
        <ProfileForm
          profile={profile}
          loading={isLoading}
          updating={isUpdating}
          onSubmit={updateProfile}
        />
      </div>

      {/* Account Info */}
      {profile && !isLoading && (
        <div className="mt-6 rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
            계정 정보
          </h2>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-[var(--color-text-secondary)]">역할</dt>
              <dd className="mt-1">
                <span className="inline-flex px-3 py-1 rounded-full bg-[var(--color-bg-secondary)] text-sm font-medium text-[var(--color-text-primary)]">
                  {profile.role === 'lawyer' && '변호사'}
                  {profile.role === 'client' && '의뢰인'}
                  {profile.role === 'detective' && '탐정'}
                  {profile.role === 'admin' && '관리자'}
                  {!['lawyer', 'client', 'detective', 'admin'].includes(profile.role) &&
                    profile.role}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-sm text-[var(--color-text-secondary)]">가입일</dt>
              <dd className="mt-1 text-[var(--color-text-primary)]">
                {new Date(profile.created_at).toLocaleDateString('ko-KR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
