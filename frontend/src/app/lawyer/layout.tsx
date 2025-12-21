'use client';

/**
 * Lawyer Portal Layout
 * 003-role-based-ui Feature
 *
 * Layout for the lawyer portal with sidebar navigation.
 * Responsive design with mobile drawer.
 * Uses design system tokens.
 */

import { useState } from 'react';
import PortalSidebar, { NavIcons, NavItem, HamburgerIcon } from '@/components/shared/PortalSidebar';
import { NotificationDropdown } from '@/components/shared/NotificationDropdown';
import RoleGuard from '@/components/auth/RoleGuard';
// ThemeToggle removed - dark mode disabled
import { useAuth } from '@/hooks/useAuth';
import { useRole } from '@/hooks/useRole';
import { UserRole } from '@/types/user';
import { logger } from '@/lib/logger';

// Lawyer navigation items
const lawyerNavItems: NavItem[] = [
  {
    id: 'dashboard',
    label: '대시보드',
    href: '/lawyer/dashboard',
    icon: <NavIcons.Dashboard />,
  },
  {
    id: 'cases',
    label: '케이스 관리',
    href: '/lawyer/cases',
    icon: <NavIcons.Cases />,
  },
  {
    id: 'clients',
    label: '의뢰인 관리',
    href: '/lawyer/clients',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
  {
    id: 'investigators',
    label: '탐정/조사원',
    href: '/lawyer/investigators',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
  },
  {
    id: 'calendar',
    label: '일정 관리',
    href: '/lawyer/calendar',
    icon: <NavIcons.Calendar />,
  },
  {
    id: 'messages',
    label: '메시지',
    href: '/lawyer/messages',
    icon: <NavIcons.Messages />,
    badge: 0, // Will be updated with unread count
  },
  {
    id: 'billing',
    label: '청구/정산',
    href: '/lawyer/billing',
    icon: <NavIcons.Billing />,
  },
];

const ALLOWED_ROLES: UserRole[] = ['lawyer', 'staff', 'admin'];

export default function LawyerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const { role } = useRole();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      logger.error('Logout failed', error);
    }
  };

  const renderContent = () => {
    if (!user || !role) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
        </div>
      );
    }

    return (
      <div className="flex min-h-screen bg-[var(--color-bg-secondary)]">
      {/* Skip to content link for keyboard users (T043) */}
      <a href="#main-content" className="skip-to-content">
        콘텐츠로 건너뛰기
      </a>

      {/* Sidebar */}
      <PortalSidebar
        role={user.role}
        userName={user.name}
        userEmail={user.email}
        navItems={lawyerNavItems}
        onLogout={handleLogout}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content */}
      <main
        id="main-content"
        className="flex-1 lg:ml-64 min-h-screen"
        tabIndex={-1}
      >
        {/* Top Header */}
        <header className="sticky top-0 z-10 h-16 bg-[var(--color-bg-primary)] border-b border-[var(--color-border-default)] flex items-center px-4 lg:px-6">
          {/* Mobile menu button */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-[var(--color-bg-secondary)] transition-colors mr-2"
            aria-label="메뉴 열기"
          >
            <HamburgerIcon />
          </button>

          <div className="flex-1">
            {/* Breadcrumb or page title can go here */}
          </div>
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Notification dropdown */}
            <NotificationDropdown />

            {/* User menu */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-[var(--color-primary-contrast)] font-semibold text-sm">
                {user.name.slice(0, 2).toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 lg:p-6">
          {children}
        </div>
      </main>
    </div>
    );
  };

  return (
    <RoleGuard allowedRoles={ALLOWED_ROLES}>
      {renderContent()}
    </RoleGuard>
  );
}
