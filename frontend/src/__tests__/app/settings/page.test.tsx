/**
 * Settings Hub Page Tests
 * 005-lawyer-portal-pages Feature - US4 (T050)
 *
 * TDD: Write tests first, ensure they fail, then implement.
 */

import { render, screen, waitFor } from '@testing-library/react';
import SettingsPage from '@/app/settings/page';
import * as authApi from '@/lib/api/auth';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

// Mock the auth API
jest.mock('@/lib/api/auth', () => ({
  getCurrentUser: jest.fn(),
}));

const mockUser = {
  id: 'user-1',
  name: '홍길동',
  email: 'hong@example.com',
  role: 'lawyer',
  created_at: '2024-01-01T00:00:00Z',
};

describe('SettingsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should show loading state initially', () => {
    (authApi.getCurrentUser as jest.Mock).mockReturnValue(new Promise(() => {}));

    render(<SettingsPage />);

    // Should show loading skeleton (animated pulse element)
    const loadingElement = document.querySelector('.animate-pulse');
    expect(loadingElement).toBeInTheDocument();
  });

  it('should render settings menu with all sections', async () => {
    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: mockUser,
      error: null,
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('설정')).toBeInTheDocument();
    });

    // Check that all settings sections are rendered
    expect(screen.getByText('프로필')).toBeInTheDocument();
    expect(screen.getByText('알림')).toBeInTheDocument();
    expect(screen.getByText('보안')).toBeInTheDocument();
    expect(screen.getByText('청구')).toBeInTheDocument();
  });

  it('should have links to subpages', async () => {
    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: mockUser,
      error: null,
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('프로필')).toBeInTheDocument();
    });

    // Check links exist
    const profileLink = screen.getByRole('link', { name: /프로필/ });
    expect(profileLink).toHaveAttribute('href', '/settings/profile');

    const notificationLink = screen.getByRole('link', { name: /알림/ });
    expect(notificationLink).toHaveAttribute('href', '/settings/notifications');

    const securityLink = screen.getByRole('link', { name: /보안/ });
    expect(securityLink).toHaveAttribute('href', '/settings/security');

    const billingLink = screen.getByRole('link', { name: /청구/ });
    expect(billingLink).toHaveAttribute('href', '/settings/billing');
  });

  it('should display user profile summary when loaded', async () => {
    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: mockUser,
      error: null,
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('홍길동')).toBeInTheDocument();
    });

    expect(screen.getByText('hong@example.com')).toBeInTheDocument();
    expect(screen.getByText('변호사')).toBeInTheDocument();
  });

  it('should show error message on API failure', async () => {
    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: null,
      error: '사용자 정보를 불러올 수 없습니다.',
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('사용자 정보를 불러올 수 없습니다.')).toBeInTheDocument();
    });
  });

  it('should display user initials as avatar', async () => {
    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: mockUser,
      error: null,
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('홍')).toBeInTheDocument();
    });
  });

  it('should show environment info in development mode', async () => {
    const originalEnv = process.env.NODE_ENV;
    // @ts-expect-error - NODE_ENV is normally readonly
    process.env.NODE_ENV = 'development';

    (authApi.getCurrentUser as jest.Mock).mockResolvedValue({
      data: mockUser,
      error: null,
    });

    render(<SettingsPage />);

    await waitFor(() => {
      expect(screen.getByText('개발 환경 정보')).toBeInTheDocument();
    });

    // @ts-expect-error - Restore NODE_ENV
    process.env.NODE_ENV = originalEnv;
  });
});
