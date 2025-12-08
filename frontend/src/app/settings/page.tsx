'use client';

import { useEffect, useState } from 'react';
import { getCurrentUser, UserInfo } from '@/lib/api/auth';

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
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      <div>
        <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">계정 설정</h1>
        <p className="text-[var(--color-text-secondary)]">
          프로필과 환경 구성을 확인하고 업데이트하세요.
        </p>
      </div>

      {error && (
        <div className="p-4 border border-red-200 bg-red-50 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-10">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)]" />
        </div>
      )}

      {!loading && user && (
        <>
          <section className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm space-y-4">
            <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">프로필</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">이름</p>
                <p className="text-base font-medium text-[var(--color-text-primary)]">
                  {user.name}
                </p>
              </div>
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">이메일</p>
                <p className="text-base font-medium text-[var(--color-text-primary)]">
                  {user.email}
                </p>
              </div>
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">역할</p>
                <span className="inline-flex px-3 py-1 rounded-full bg-[var(--color-bg-secondary)] text-sm font-medium text-[var(--color-text-primary)]">
                  {user.role}
                </span>
              </div>
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">가입일</p>
                <p className="text-base font-medium text-[var(--color-text-primary)]">
                  {new Date(user.created_at).toLocaleDateString('ko-KR')}
                </p>
              </div>
            </div>
          </section>

          <section className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">
                배포 환경
              </h2>
              <span className="inline-flex px-3 py-1 rounded-full bg-[var(--color-primary)]/10 text-sm font-medium text-[var(--color-primary)] uppercase tracking-wide">
                {process.env.NEXT_PUBLIC_APP_ENV}
              </span>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">API Base URL</p>
                <code className="text-sm text-[var(--color-text-primary)] break-all">
                  {process.env.NEXT_PUBLIC_API_BASE_URL || '미설정'}
                </code>
              </div>
              <div>
                <p className="text-sm text-[var(--color-text-secondary)] mb-1">App Base URL</p>
                <code className="text-sm text-[var(--color-text-primary)] break-all">
                  {process.env.NEXT_PUBLIC_APP_BASE_URL || '미설정'}
                </code>
              </div>
            </div>
            <p className="text-sm text-[var(--color-text-secondary)]">
              CloudFront 배포 시 두 값이 모두 정확한 도메인을 가리켜야 CORS 및 라우팅 오류가 발생하지 않습니다.
            </p>
          </section>
        </>
      )}
    </div>
  );
}
