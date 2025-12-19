/**
 * Login Page
 * Plan 3.19.2 - Routing Structure Change
 *
 * Features:
 * - Login form (moved from root `/`)
 * - Redirect to dashboard if already authenticated
 *
 * Security:
 * - Uses HTTP-only cookie for authentication
 * - Auth check via useAuth hook (calls /auth/me)
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/hooks/useAuth';
import { getDashboardPath, UserRole } from '@/types/user';
import LandingNav from '@/components/landing/LandingNav';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, logout } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    // Navigation Guard: Redirect if already authenticated
    // Issue #289: Use role-based dashboard path instead of hardcoded /cases
    if (!isLoading && isAuthenticated && user) {
      const dashboardPath = getDashboardPath(user.role as UserRole);
      router.push(dashboardPath);
    }
  }, [isAuthenticated, isLoading, router, user]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-neutral-600">로딩 중...</div>
      </div>
    );
  }

  // If authenticated, show redirecting message (redirect will happen via useEffect)
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="text-neutral-600">대시보드로 이동 중...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <LandingNav
        isScrolled={isScrolled}
        isAuthenticated={isAuthenticated}
        authLoading={isLoading}
        onLogout={logout}
      />

      <main
        id="main-content"
        className="flex items-center justify-center px-4 pb-10 pt-6"
      >
        <div className="w-full max-w-sm">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-secondary mb-2">
              Legal Evidence Hub
            </h1>
            <p className="text-neutral-600">로그인하여 시작하세요</p>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-md">
            <LoginForm />

            <div className="mt-6 pt-6 border-t border-neutral-200 text-center">
              <p className="text-neutral-600">
                계정이 없으신가요?{' '}
                <Link
                  href="/signup"
                  className="text-secondary hover:underline font-medium"
                >
                  회원가입
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
