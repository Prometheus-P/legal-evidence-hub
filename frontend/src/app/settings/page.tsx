/**
 * Settings Hub Page
 * 005-lawyer-portal-pages Feature - US4 (T055)
 *
 * Navigation hub for all settings sections.
 */

'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getCurrentUser, UserInfo } from '@/lib/api/auth';

interface SettingsSection {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
}

const SETTINGS_SECTIONS: SettingsSection[] = [
  {
    title: '프로필',
    description: '이름, 연락처, 시간대 등 개인 정보를 관리합니다.',
    href: '/settings/profile',
    icon: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    ),
  },
  {
    title: '알림',
    description: '이메일 및 푸시 알림 설정을 관리합니다.',
    href: '/settings/notifications',
    icon: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
    ),
  },
  {
    title: '보안',
    description: '비밀번호 변경 및 2단계 인증을 설정합니다.',
    href: '/settings/security',
    icon: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
    ),
  },
  {
    title: '청구',
    description: '결제 방법 및 청구 내역을 관리합니다.',
    href: '/settings/billing',
    icon: (
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
        />
      </svg>
    ),
  },
];

export default function SettingsPage() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      const response = await getCurrentUser();

      if (response.error) {
        setError(response.error);
        setUser(null);
      } else if (response.data) {
        setUser(response.data);
        setError(null);
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">설정</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          계정 설정을 관리하고 환경을 구성합니다.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* User Profile Summary */}
      {loading ? (
        <div className="mb-8 p-6 rounded-xl border border-[var(--color-border-default)] bg-white shadow-sm animate-pulse">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gray-200" />
            <div className="space-y-2">
              <div className="h-5 w-32 bg-gray-200 rounded" />
              <div className="h-4 w-48 bg-gray-200 rounded" />
            </div>
          </div>
        </div>
      ) : user ? (
        <div className="mb-8 p-6 rounded-xl border border-[var(--color-border-default)] bg-white shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white text-2xl font-bold">
              {user.name?.charAt(0) || user.email.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                {user.name || '이름 없음'}
              </h2>
              <p className="text-[var(--color-text-secondary)]">{user.email}</p>
              <span className="inline-flex mt-1 px-2 py-0.5 rounded-full bg-[var(--color-bg-secondary)] text-xs font-medium text-[var(--color-text-secondary)]">
                {user.role === 'lawyer' && '변호사'}
                {user.role === 'client' && '의뢰인'}
                {user.role === 'detective' && '탐정'}
                {user.role === 'admin' && '관리자'}
                {!['lawyer', 'client', 'detective', 'admin'].includes(user.role) && user.role}
              </span>
            </div>
          </div>
        </div>
      ) : null}

      {/* Settings Sections Grid */}
      <div className="grid gap-4 sm:grid-cols-2">
        {SETTINGS_SECTIONS.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="p-6 rounded-xl border border-[var(--color-border-default)] bg-white shadow-sm hover:border-[var(--color-primary)] hover:shadow-md transition-all group"
          >
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] group-hover:bg-[var(--color-primary)]/10 group-hover:text-[var(--color-primary)] transition-colors">
                {section.icon}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)] transition-colors">
                  {section.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] mt-1">
                  {section.description}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Environment Info (for debugging) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-8 p-6 rounded-xl border border-dashed border-[var(--color-border-default)] bg-gray-50">
          <h3 className="text-sm font-medium text-[var(--color-text-secondary)] mb-2">
            개발 환경 정보
          </h3>
          <dl className="grid gap-2 text-xs">
            <div className="flex gap-2">
              <dt className="text-[var(--color-text-secondary)]">환경:</dt>
              <dd className="font-mono text-[var(--color-text-primary)]">
                {process.env.NEXT_PUBLIC_APP_ENV || 'development'}
              </dd>
            </div>
            <div className="flex gap-2">
              <dt className="text-[var(--color-text-secondary)]">API URL:</dt>
              <dd className="font-mono text-[var(--color-text-primary)] break-all">
                {process.env.NEXT_PUBLIC_API_BASE_URL || '미설정'}
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
