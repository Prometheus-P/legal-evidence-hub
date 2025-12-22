/**
 * SecuritySettingsForm Component
 * 014-ui-settings-completion Feature
 *
 * Form for managing security settings: password change, 2FA toggle, login history.
 */

'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import type { SecuritySettings, PasswordChangeRequest } from '@/types/settings';

interface SecuritySettingsFormProps {
  security: SecuritySettings | null;
  loading?: boolean;
  updating?: boolean;
  onPasswordChange: (data: PasswordChangeRequest) => Promise<boolean>;
  onTwoFactorToggle: (enabled: boolean) => Promise<boolean>;
}

interface PasswordFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface FormErrors {
  current_password?: string;
  new_password?: string;
  confirm_password?: string;
}

export function SecuritySettingsForm({
  security,
  loading,
  updating,
  onPasswordChange,
  onTwoFactorToggle,
}: SecuritySettingsFormProps) {
  const [passwordForm, setPasswordForm] = useState<PasswordFormData>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const validatePasswordForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!passwordForm.current_password) {
      newErrors.current_password = '현재 비밀번호를 입력해주세요.';
    }

    if (!passwordForm.new_password) {
      newErrors.new_password = '새 비밀번호를 입력해주세요.';
    } else if (passwordForm.new_password.length < 8) {
      newErrors.new_password = '비밀번호는 최소 8자 이상이어야 합니다.';
    } else if (passwordForm.new_password === passwordForm.current_password) {
      newErrors.new_password = '새 비밀번호는 현재 비밀번호와 달라야 합니다.';
    }

    if (!passwordForm.confirm_password) {
      newErrors.confirm_password = '비밀번호 확인을 입력해주세요.';
    } else if (passwordForm.new_password !== passwordForm.confirm_password) {
      newErrors.confirm_password = '비밀번호가 일치하지 않습니다.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePasswordForm()) {
      toast.error('입력 정보를 확인해주세요.');
      return;
    }

    const result = await onPasswordChange({
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
    });

    if (result) {
      toast.success('비밀번호가 변경되었습니다.');
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } else {
      toast.error('비밀번호 변경에 실패했습니다.');
    }
  };

  const handleTwoFactorToggle = async () => {
    if (!security) return;

    const result = await onTwoFactorToggle(!security.two_factor_enabled);
    if (result) {
      toast.success(security.two_factor_enabled ? '2단계 인증이 비활성화되었습니다.' : '2단계 인증이 활성화되었습니다.');
    } else {
      toast.error('2단계 인증 설정 변경에 실패했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
          <div className="h-6 w-32 bg-gray-200 rounded mb-4" />
          <div className="space-y-4">
            <div className="h-12 bg-gray-200 rounded" />
            <div className="h-12 bg-gray-200 rounded" />
            <div className="h-12 bg-gray-200 rounded" />
          </div>
        </div>
        <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
          <div className="h-6 w-32 bg-gray-200 rounded mb-4" />
          <div className="h-16 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Password Change Section */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
          비밀번호 변경
        </h2>

        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          {/* Current Password */}
          <div>
            <label
              htmlFor="current_password"
              className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
            >
              현재 비밀번호
            </label>
            <input
              type="password"
              id="current_password"
              value={passwordForm.current_password}
              onChange={(e) => {
                setPasswordForm((prev) => ({ ...prev, current_password: e.target.value }));
                setErrors((prev) => ({ ...prev, current_password: undefined }));
              }}
              className={`w-full px-4 py-2 rounded-lg border ${
                errors.current_password
                  ? 'border-red-300 focus:ring-red-500'
                  : 'border-[var(--color-border-default)] focus:ring-[var(--color-primary)]'
              } focus:outline-none focus:ring-2 focus:border-transparent bg-white`}
              placeholder="현재 비밀번호 입력"
            />
            {errors.current_password && (
              <p className="mt-1 text-sm text-red-600">{errors.current_password}</p>
            )}
          </div>

          {/* New Password */}
          <div>
            <label
              htmlFor="new_password"
              className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
            >
              새 비밀번호
            </label>
            <input
              type="password"
              id="new_password"
              value={passwordForm.new_password}
              onChange={(e) => {
                setPasswordForm((prev) => ({ ...prev, new_password: e.target.value }));
                setErrors((prev) => ({ ...prev, new_password: undefined }));
              }}
              className={`w-full px-4 py-2 rounded-lg border ${
                errors.new_password
                  ? 'border-red-300 focus:ring-red-500'
                  : 'border-[var(--color-border-default)] focus:ring-[var(--color-primary)]'
              } focus:outline-none focus:ring-2 focus:border-transparent bg-white`}
              placeholder="새 비밀번호 입력 (최소 8자)"
            />
            {errors.new_password && (
              <p className="mt-1 text-sm text-red-600">{errors.new_password}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label
              htmlFor="confirm_password"
              className="block text-sm font-medium text-[var(--color-text-primary)] mb-1"
            >
              비밀번호 확인
            </label>
            <input
              type="password"
              id="confirm_password"
              value={passwordForm.confirm_password}
              onChange={(e) => {
                setPasswordForm((prev) => ({ ...prev, confirm_password: e.target.value }));
                setErrors((prev) => ({ ...prev, confirm_password: undefined }));
              }}
              className={`w-full px-4 py-2 rounded-lg border ${
                errors.confirm_password
                  ? 'border-red-300 focus:ring-red-500'
                  : 'border-[var(--color-border-default)] focus:ring-[var(--color-primary)]'
              } focus:outline-none focus:ring-2 focus:border-transparent bg-white`}
              placeholder="새 비밀번호 다시 입력"
            />
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
            )}
          </div>

          {/* Last Password Change Info */}
          {security?.last_password_change && (
            <p className="text-sm text-[var(--color-text-secondary)]">
              마지막 비밀번호 변경:{' '}
              {new Date(security.last_password_change).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          )}

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
                  변경 중...
                </span>
              ) : (
                '비밀번호 변경'
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Two-Factor Authentication Section */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
          2단계 인증
        </h2>

        <div className="flex items-center justify-between p-4 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-secondary)]">
          <div>
            <p className="font-medium text-[var(--color-text-primary)]">2단계 인증 사용</p>
            <p className="text-sm text-[var(--color-text-secondary)]">
              로그인 시 추가 인증 단계를 통해 계정을 보호합니다.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={security?.two_factor_enabled ?? false}
            onClick={handleTwoFactorToggle}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              security?.two_factor_enabled ? 'bg-[var(--color-primary)]' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                security?.two_factor_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Login History Section */}
      <div className="rounded-xl border border-[var(--color-border-default)] bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            로그인 기록
          </h2>
          <span className="text-sm text-[var(--color-text-secondary)]">
            활성 세션: {security?.active_sessions ?? 0}개
          </span>
        </div>

        {security?.login_history && security.login_history.length > 0 ? (
          <div className="space-y-3">
            {security.login_history.map((item, index) => (
              <div
                key={index}
                className="flex items-start justify-between p-4 rounded-lg border border-[var(--color-border-default)] bg-[var(--color-bg-secondary)]"
              >
                <div className="space-y-1">
                  <p className="font-medium text-[var(--color-text-primary)]">{item.device}</p>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    {item.ip_address} {item.location && `• ${item.location}`}
                  </p>
                </div>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {new Date(item.timestamp).toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[var(--color-text-secondary)] text-center py-4">
            로그인 기록이 없습니다.
          </p>
        )}
      </div>
    </div>
  );
}
