/**
 * Signup Page
 * Plan 3.19.2 - Routing Structure
 *
 * Features:
 * - Signup form for new users
 * - 14-day free trial emphasis
 * - Real API integration with backend
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signup, SignupRole } from '@/lib/api/auth';
import { logger } from '@/lib/logger';

// T082: Role options for signup dropdown
const ROLE_OPTIONS: { value: SignupRole | ''; label: string; description: string }[] = [
  { value: '', label: '역할을 선택하세요', description: '' },
  { value: 'lawyer', label: '변호사', description: '사건 관리 및 법률 서비스 제공' },
  { value: 'client', label: '의뢰인', description: '법률 서비스 이용' },
  { value: 'detective', label: '탐정', description: '증거 수집 및 현장 조사' },
];

// T085: Role-based redirect paths
const ROLE_DASHBOARD_PATHS: Record<SignupRole, string> = {
  lawyer: '/lawyer/dashboard',
  client: '/client/dashboard',
  detective: '/detective/dashboard',
};

export default function SignupPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<SignupRole | ''>('');  // T082: Role state
  const [lawFirm, setLawFirm] = useState('');
  const [password, setPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    // T086: Block signup without role selection
    if (!role) {
      setError('역할을 선택해주세요.');
      return;
    }

    if (password.length < 8) {
      setError('비밀번호는 8자 이상이어야 합니다.');
      return;
    }

    if (!acceptTerms) {
      setError('이용약관에 동의해주세요.');
      return;
    }

    if (!acceptPrivacy) {
      setError('개인정보처리방침에 동의해주세요.');
      return;
    }

    setLoading(true);

    try {
      // T083: Real API call to backend with role parameter
      const response = await signup({
        name,
        email,
        password,
        role,  // T083: Include role in signup request
        law_firm: lawFirm || undefined,
        accept_terms: acceptTerms,
        accept_privacy: acceptPrivacy,
      });

      if (response.error || !response.data) {
        setError(response.error || '회원가입 중 오류가 발생했습니다.');
        return;
      }

      // Note: Access token is stored in HTTP-only cookie by backend (XSS protection)
      // No localStorage token storage - matches login flow in AuthContext (#309 fix)

      // Cache user info for display purposes
      const userRole = response.data.user?.role || role;
      if (response.data.user) {
        const userData = {
          id: response.data.user.id,
          name: response.data.user.name,
          email: response.data.user.email,
          role: response.data.user.role,
          status: 'active',
          created_at: new Date().toISOString(),
        };
        // Set user_data cookie for middleware
        document.cookie = `user_data=${encodeURIComponent(JSON.stringify({
          name: userData.name,
          email: userData.email,
          role: userData.role,
        }))}; path=/; max-age=${7 * 24 * 60 * 60}`;
        // Cache full user data (matches AuthContext format)
        localStorage.setItem('userCache', JSON.stringify(userData));
        // Set flag to prevent checkAuth race condition after redirect (matches login flow)
        sessionStorage.setItem('justLoggedIn', 'true');
      }

      // T085: Role-based redirect to appropriate dashboard
      const redirectPath = ROLE_DASHBOARD_PATHS[userRole as SignupRole] || '/lawyer/dashboard';
      router.push(redirectPath);
    } catch (err) {
      logger.error('Signup error', err);
      setError('회원가입 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-deep-trust-blue mb-2">
            무료로 시작하기
          </h1>
          <p className="text-neutral-600">14일 무료 체험, 신용카드 필요 없음</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-neutral-700 mb-2">
              이름
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="홍길동"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-2">
              이메일
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="your@email.com"
            />
          </div>

          {/* T082: Role dropdown */}
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-neutral-700 mb-2">
              역할 <span className="text-red-500">*</span>
            </label>
            <select
              id="role"
              name="role"
              required
              value={role}
              onChange={(e) => setRole(e.target.value as SignupRole | '')}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent bg-white"
            >
              {ROLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} disabled={option.value === ''}>
                  {option.label}
                </option>
              ))}
            </select>
            {role && (
              <p className="mt-1 text-xs text-neutral-500">
                {ROLE_OPTIONS.find((opt) => opt.value === role)?.description}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="law-firm" className="block text-sm font-medium text-neutral-700 mb-2">
              소속 (선택)
            </label>
            <input
              id="law-firm"
              name="law-firm"
              type="text"
              value={lawFirm}
              onChange={(e) => setLawFirm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="법무법인 이름"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-2">
              비밀번호
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
              placeholder="8자 이상"
            />
          </div>

          {/* T063 - FR-021, FR-022: 개별 동의 체크박스 */}
          <div className="space-y-3">
            <div className="flex items-start">
              <input
                id="accept-terms"
                name="accept-terms"
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="h-4 w-4 mt-0.5 text-accent focus:ring-accent border-gray-300 rounded"
              />
              <label htmlFor="accept-terms" className="ml-2 block text-sm text-neutral-700">
                <span className="text-red-500">*</span>{' '}
                <a href="/terms" target="_blank" className="text-accent hover:underline">
                  이용약관
                </a>
                에 동의합니다 (필수)
              </label>
            </div>
            <div className="flex items-start">
              <input
                id="accept-privacy"
                name="accept-privacy"
                type="checkbox"
                checked={acceptPrivacy}
                onChange={(e) => setAcceptPrivacy(e.target.checked)}
                className="h-4 w-4 mt-0.5 text-accent focus:ring-accent border-gray-300 rounded"
              />
              <label htmlFor="accept-privacy" className="ml-2 block text-sm text-neutral-700">
                <span className="text-red-500">*</span>{' '}
                <a href="/privacy" target="_blank" className="text-accent hover:underline">
                  개인정보처리방침
                </a>
                에 동의합니다 (필수)
              </label>
            </div>
          </div>

          {error && (
            <div data-testid="error-message" className="text-sm text-red-600 text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 disabled:opacity-50"
          >
            {loading ? '처리 중...' : '무료 체험 시작'}
          </button>
        </form>

        <p className="text-sm text-gray-500 text-center mt-6">
          이미 계정이 있으신가요?{' '}
          <a href="/login" className="text-accent hover:underline">
            로그인
          </a>
        </p>
      </div>
    </div>
  );
}
