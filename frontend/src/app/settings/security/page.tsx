/**
 * Security Settings Page
 * 014-ui-settings-completion Feature
 *
 * Page for managing security settings: password change, 2FA, login history.
 */

'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { SecuritySettingsForm } from '@/components/settings/SecuritySettingsForm';
import { getSecuritySettings, changePassword } from '@/lib/api/settings';
import type { SecuritySettings, PasswordChangeRequest } from '@/types/settings';

export default function SecuritySettingsPage() {
  const [security, setSecurity] = useState<SecuritySettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSecuritySettings = async () => {
      setIsLoading(true);
      const response = await getSecuritySettings();

      if (response.error) {
        setError(response.error);
        // Use mock data for development when API is not available
        setSecurity({
          two_factor_enabled: false,
          last_password_change: new Date().toISOString(),
          active_sessions: 1,
          login_history: [
            {
              timestamp: new Date().toISOString(),
              ip_address: '127.0.0.1',
              device: 'Chrome on macOS',
              location: '서울, 대한민국',
            },
          ],
        });
      } else if (response.data) {
        setSecurity(response.data);
        setError(null);
      }
      setIsLoading(false);
    };

    fetchSecuritySettings();
  }, []);

  const handlePasswordChange = async (data: PasswordChangeRequest): Promise<boolean> => {
    setIsUpdating(true);
    const response = await changePassword(data);
    setIsUpdating(false);

    if (response.error) {
      setError(response.error);
      return false;
    }

    // Update last password change date
    if (security) {
      setSecurity({
        ...security,
        last_password_change: new Date().toISOString(),
      });
    }
    setError(null);
    return true;
  };

  const handleTwoFactorToggle = async (enabled: boolean): Promise<boolean> => {
    // TODO: Implement 2FA toggle API when backend is ready
    if (security) {
      setSecurity({
        ...security,
        two_factor_enabled: enabled,
      });
    }
    return true;
  };

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
          <li className="text-[var(--color-text-primary)] font-medium">보안</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">보안 설정</h1>
        <p className="text-[var(--color-text-secondary)] mt-1">
          비밀번호 변경 및 2단계 인증을 설정합니다.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
          {error}
        </div>
      )}

      {/* Security Settings Form */}
      <SecuritySettingsForm
        security={security}
        loading={isLoading}
        updating={isUpdating}
        onPasswordChange={handlePasswordChange}
        onTwoFactorToggle={handleTwoFactorToggle}
      />
    </div>
  );
}
