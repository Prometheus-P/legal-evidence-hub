'use client';

/**
 * Client Portal Layout
 * 003-role-based-ui Feature
 * Updated: navbar-sidebar-refactoring
 *
 * Layout for the client portal with simplified navigation.
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
  CreditCard,
} from 'lucide-react';

// Client navigation groups - simplified view
const clientNavGroups: NavGroup[] = [
  {
    id: 'main',
    items: [
      {
        id: 'dashboard',
        label: '내 현황',
        href: '/client/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
      },
      {
        id: 'cases',
        label: '케이스 상태',
        href: '/client/cases',
        icon: <Briefcase className="w-5 h-5" />,
      },
      {
        id: 'messages',
        label: '변호사 소통',
        href: '/client/messages',
        icon: <MessageSquare className="w-5 h-5" />,
      },
      {
        id: 'billing',
        label: '청구/결제',
        href: '/client/billing',
        icon: <CreditCard className="w-5 h-5" />,
      },
    ],
  },
];

// Admin can access all portals for administrative purposes
const ALLOWED_ROLES: UserRole[] = ['client', 'admin'];

export default function ClientLayout({
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
        <PortalSidebar groups={clientNavGroups} />

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
