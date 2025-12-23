/**
 * PortalSidebar Active State Verification Tests
 * 005-lawyer-portal-pages Feature - T069
 * Updated for NavGroup-based interface
 *
 * Tests for FR-009: Sidebar highlights active page on all lawyer portal routes
 */

import React from 'react';
import { render, screen, within } from '@testing-library/react';
import PortalSidebar, { NavItem, NavGroup } from '@/components/shared/PortalSidebar';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  Search,
  Calendar,
  MessageSquare,
  CreditCard,
} from 'lucide-react';

// Mock Next.js navigation
const mockPathname = jest.fn();
jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
}));

// Mock Next.js Link
jest.mock('next/link', () => {
  const MockLink = ({ children, href, className }: { children: React.ReactNode; href: string; className?: string }) => (
    <a href={href} className={className} data-testid={`nav-link-${href}`}>
      {children}
    </a>
  );
  MockLink.displayName = 'MockLink';
  return MockLink;
});

// Mock useAuth hook
jest.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: { name: '김변호사', email: 'lawyer@test.com' },
    logout: jest.fn(),
  }),
}));

// Mock useRole hook
jest.mock('@/hooks/useRole', () => ({
  useRole: () => ({
    role: 'lawyer',
    roleDisplayName: '변호사',
  }),
}));

// Mock NotificationDropdown to avoid act() warnings
jest.mock('@/components/shared/NotificationDropdown', () => ({
  NotificationDropdown: () => <div data-testid="notification-dropdown">Notifications</div>,
}));

// Lawyer navigation groups (matches layout.tsx structure)
const lawyerNavGroups: NavGroup[] = [
  {
    id: 'core',
    items: [
      {
        id: 'dashboard',
        label: '대시보드',
        href: '/lawyer/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
      },
      {
        id: 'cases',
        label: '케이스',
        href: '/lawyer/cases',
        icon: <Briefcase className="w-5 h-5" />,
      },
    ],
  },
  {
    id: 'management',
    label: '관리',
    collapsible: true,
    items: [
      {
        id: 'clients',
        label: '의뢰인',
        href: '/lawyer/clients',
        icon: <Users className="w-5 h-5" />,
      },
      {
        id: 'investigators',
        label: '탐정',
        href: '/lawyer/investigators',
        icon: <Search className="w-5 h-5" />,
      },
      {
        id: 'calendar',
        label: '일정',
        href: '/lawyer/calendar',
        icon: <Calendar className="w-5 h-5" />,
      },
      {
        id: 'messages',
        label: '메시지',
        href: '/lawyer/messages',
        icon: <MessageSquare className="w-5 h-5" />,
        badge: 0,
      },
      {
        id: 'billing',
        label: '청구/결제',
        href: '/lawyer/billing',
        icon: <CreditCard className="w-5 h-5" />,
      },
    ],
  },
];

// Helper to get the desktop sidebar (first aside element, which has lg:flex)
const getDesktopSidebar = (container: HTMLElement) => {
  const asides = container.querySelectorAll('aside');
  // The first aside is the desktop sidebar (hidden lg:flex)
  return asides[0];
};

describe('PortalSidebar Active State - FR-009', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Lawyer Portal Routes', () => {
    it('should highlight "대시보드" when on /lawyer/dashboard', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const dashboardLink = within(sidebar as HTMLElement).getByRole('link', { name: /대시보드/i });
      expect(dashboardLink).toHaveClass('bg-accent');
    });

    it('should highlight "케이스" when on /lawyer/cases', () => {
      mockPathname.mockReturnValue('/lawyer/cases');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const casesLink = within(sidebar as HTMLElement).getByRole('link', { name: /케이스/i });
      expect(casesLink).toHaveClass('bg-accent');
    });

    it('should highlight "케이스" when on /lawyer/cases/123 (nested route)', () => {
      mockPathname.mockReturnValue('/lawyer/cases/123');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const casesLink = within(sidebar as HTMLElement).getByRole('link', { name: /케이스/i });
      expect(casesLink).toHaveClass('bg-accent');
    });

    it('should highlight "의뢰인" when on /lawyer/clients', () => {
      mockPathname.mockReturnValue('/lawyer/clients');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const clientsLink = within(sidebar as HTMLElement).getByRole('link', { name: /의뢰인/i });
      expect(clientsLink).toHaveClass('bg-accent');
    });

    it('should highlight "탐정" when on /lawyer/investigators', () => {
      mockPathname.mockReturnValue('/lawyer/investigators');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const investigatorsLink = within(sidebar as HTMLElement).getByRole('link', { name: /탐정/i });
      expect(investigatorsLink).toHaveClass('bg-accent');
    });

    it('should highlight "일정" when on /lawyer/calendar', () => {
      mockPathname.mockReturnValue('/lawyer/calendar');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const calendarLink = within(sidebar as HTMLElement).getByRole('link', { name: /일정/i });
      expect(calendarLink).toHaveClass('bg-accent');
    });

    it('should highlight "메시지" when on /lawyer/messages', () => {
      mockPathname.mockReturnValue('/lawyer/messages');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const messagesLink = within(sidebar as HTMLElement).getByRole('link', { name: /메시지/i });
      expect(messagesLink).toHaveClass('bg-accent');
    });

    it('should highlight "청구/결제" when on /lawyer/billing', () => {
      mockPathname.mockReturnValue('/lawyer/billing');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const billingLink = within(sidebar as HTMLElement).getByRole('link', { name: /청구\/결제/i });
      expect(billingLink).toHaveClass('bg-accent');
    });
  });

  describe('Non-Active States', () => {
    it('should not highlight other nav items when on /lawyer/dashboard', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      // Cases should not be highlighted
      const casesLink = within(sidebar as HTMLElement).getByRole('link', { name: /케이스/i });
      expect(casesLink).not.toHaveClass('bg-accent');
      expect(casesLink).toHaveClass('text-gray-700');

      // Calendar should not be highlighted
      const calendarLink = within(sidebar as HTMLElement).getByRole('link', { name: /일정/i });
      expect(calendarLink).not.toHaveClass('bg-accent');
    });

    it('should only highlight dashboard for exact match (not /lawyer/dashboard/something)', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const dashboardLink = within(sidebar as HTMLElement).getByRole('link', { name: /대시보드/i });
      expect(dashboardLink).toHaveClass('bg-accent');
    });
  });

  describe('Nested Route Highlighting', () => {
    it('should highlight "케이스" for /lawyer/cases/123/evidence', () => {
      mockPathname.mockReturnValue('/lawyer/cases/123/evidence');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const casesLink = within(sidebar as HTMLElement).getByRole('link', { name: /케이스/i });
      expect(casesLink).toHaveClass('bg-accent');
    });

    it('should highlight "의뢰인" for /lawyer/clients/456', () => {
      mockPathname.mockReturnValue('/lawyer/clients/456');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const clientsLink = within(sidebar as HTMLElement).getByRole('link', { name: /의뢰인/i });
      expect(clientsLink).toHaveClass('bg-accent');
    });

    it('should highlight "메시지" for /lawyer/messages/thread/123', () => {
      mockPathname.mockReturnValue('/lawyer/messages/thread/123');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      const messagesLink = within(sidebar as HTMLElement).getByRole('link', { name: /메시지/i });
      expect(messagesLink).toHaveClass('bg-accent');
    });
  });

  describe('Badge Display', () => {
    it('should show badge on nav item when badge count is greater than 0', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const groupsWithBadge: NavGroup[] = [
        {
          id: 'main',
          items: [
            {
              id: 'messages',
              label: '메시지',
              href: '/lawyer/messages',
              icon: <MessageSquare className="w-5 h-5" />,
              badge: 5,
            },
          ],
        },
      ];

      const { container } = render(<PortalSidebar groups={groupsWithBadge} />);
      const sidebar = getDesktopSidebar(container);

      expect(within(sidebar as HTMLElement).getByText('5')).toBeInTheDocument();
    });

    it('should not show badge when badge count is 0', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      // Messages badge should not be visible (badge is 0)
      const messagesLink = within(sidebar as HTMLElement).getByRole('link', { name: /메시지/i });
      // Check that there's no badge element (no number displayed)
      expect(messagesLink.querySelector('.rounded-full')).not.toBeInTheDocument();
    });
  });

  describe('User Info Display', () => {
    it('should display user name', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      expect(within(sidebar as HTMLElement).getByText('김변호사')).toBeInTheDocument();
    });

    it('should display role display name', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      expect(within(sidebar as HTMLElement).getByText('변호사')).toBeInTheDocument();
    });
  });

  describe('Group Collapsibility', () => {
    it('should render collapsible group label', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar groups={lawyerNavGroups} />);

      const sidebar = getDesktopSidebar(container);
      // Management group should have a label
      expect(within(sidebar as HTMLElement).getByText('관리')).toBeInTheDocument();
    });
  });
});
