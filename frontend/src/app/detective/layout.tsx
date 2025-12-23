'use client';

/**
 * Detective Portal Layout
 * 003-role-based-ui Feature
 * Updated: navbar-sidebar-refactoring
 *
 * Layout for the detective portal with field investigation tools.
 * Uses PortalSidebar with NavGroup for hierarchical navigation.
 */

import { PortalSidebar, NavGroup } from '@/components/shared/PortalSidebar';
import RoleGuard from '@/components/auth/RoleGuard';
import { useAuth } from '@/hooks/useAuth';
import { useRole } from '@/hooks/useRole';
import { UserRole } from '@/types/user';
import {
  LayoutDashboard,
  Briefcase,
  MessageSquare,
  Wallet,
} from 'lucide-react';

// Detective navigation groups
const detectiveNavGroups: NavGroup[] = [
  {
    id: 'main',
    items: [
      {
        id: 'dashboard',
        label: '대시보드',
        href: '/detective/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
      },
      {
        id: 'cases',
        label: '의뢰 관리',
        href: '/detective/cases',
        icon: <Briefcase className="w-5 h-5" />,
      },
      {
        id: 'messages',
        label: '메시지',
        href: '/detective/messages',
        icon: <MessageSquare className="w-5 h-5" />,
      },
      {
        id: 'earnings',
        label: '정산/수익',
        href: '/detective/earnings',
        icon: <Wallet className="w-5 h-5" />,
      },
    ],
  },
];

// Admin can access all portals for administrative purposes
const ALLOWED_ROLES: UserRole[] = ['detective', 'admin'];

export default function DetectiveLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user } = useAuth();
  const { role } = useRole();

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
        {/* Sidebar */}
        <PortalSidebar groups={detectiveNavGroups} />

        {/* Main Content */}
        <main className="flex-1 lg:ml-64 min-h-screen">
          {/* Mobile header spacing */}
          <div className="h-16 lg:hidden" />

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
