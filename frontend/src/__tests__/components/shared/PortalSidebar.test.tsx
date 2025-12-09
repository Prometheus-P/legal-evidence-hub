/**
 * PortalSidebar Active State Verification Tests
 * 005-lawyer-portal-pages Feature - T069
 *
 * Tests for FR-009: Sidebar highlights active page on all lawyer portal routes
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import PortalSidebar, { NavItem, NavIcons } from '@/components/shared/PortalSidebar';

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

// Lawyer navigation items (same as in layout.tsx)
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
    icon: <span data-testid="clients-icon">clients-icon</span>,
  },
  {
    id: 'investigators',
    label: '탐정/조사원',
    href: '/lawyer/investigators',
    icon: <span data-testid="investigators-icon">investigators-icon</span>,
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
    badge: 0,
  },
  {
    id: 'billing',
    label: '청구/정산',
    href: '/lawyer/billing',
    icon: <NavIcons.Billing />,
  },
];

// Default props for sidebar
const defaultProps = {
  role: 'lawyer' as const,
  userName: '김변호사',
  userEmail: 'lawyer@test.com',
  navItems: lawyerNavItems,
  onLogout: jest.fn(),
  isOpen: true,
};

describe('PortalSidebar Active State - FR-009', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Lawyer Portal Routes', () => {
    it('should highlight "대시보드" when on /lawyer/dashboard', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      const dashboardLink = screen.getByRole('link', { name: /대시보드/i });
      expect(dashboardLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "케이스 관리" when on /lawyer/cases', () => {
      mockPathname.mockReturnValue('/lawyer/cases');
      render(<PortalSidebar {...defaultProps} />);

      const casesLink = screen.getByRole('link', { name: /케이스 관리/i });
      expect(casesLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "케이스 관리" when on /lawyer/cases/123 (nested route)', () => {
      mockPathname.mockReturnValue('/lawyer/cases/123');
      render(<PortalSidebar {...defaultProps} />);

      const casesLink = screen.getByRole('link', { name: /케이스 관리/i });
      expect(casesLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "의뢰인 관리" when on /lawyer/clients', () => {
      mockPathname.mockReturnValue('/lawyer/clients');
      render(<PortalSidebar {...defaultProps} />);

      const clientsLink = screen.getByRole('link', { name: /의뢰인 관리/i });
      expect(clientsLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "탐정/조사원" when on /lawyer/investigators', () => {
      mockPathname.mockReturnValue('/lawyer/investigators');
      render(<PortalSidebar {...defaultProps} />);

      const investigatorsLink = screen.getByRole('link', { name: /탐정\/조사원/i });
      expect(investigatorsLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "일정 관리" when on /lawyer/calendar', () => {
      mockPathname.mockReturnValue('/lawyer/calendar');
      render(<PortalSidebar {...defaultProps} />);

      const calendarLink = screen.getByRole('link', { name: /일정 관리/i });
      expect(calendarLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "메시지" when on /lawyer/messages', () => {
      mockPathname.mockReturnValue('/lawyer/messages');
      render(<PortalSidebar {...defaultProps} />);

      const messagesLink = screen.getByRole('link', { name: /메시지/i });
      expect(messagesLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "청구/정산" when on /lawyer/billing', () => {
      mockPathname.mockReturnValue('/lawyer/billing');
      render(<PortalSidebar {...defaultProps} />);

      const billingLink = screen.getByRole('link', { name: /청구\/정산/i });
      expect(billingLink).toHaveClass('bg-[var(--color-primary)]');
    });
  });

  describe('Non-Active States', () => {
    it('should not highlight other nav items when on /lawyer/dashboard', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      // Cases should not be highlighted
      const casesLink = screen.getByRole('link', { name: /케이스 관리/i });
      expect(casesLink).not.toHaveClass('bg-[var(--color-primary)]');
      expect(casesLink).toHaveClass('text-white/80');

      // Calendar should not be highlighted
      const calendarLink = screen.getByRole('link', { name: /일정 관리/i });
      expect(calendarLink).not.toHaveClass('bg-[var(--color-primary)]');
    });

    it('should only highlight dashboard for exact match (not /lawyer/dashboard/something)', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      const dashboardLink = screen.getByRole('link', { name: /대시보드/i });
      expect(dashboardLink).toHaveClass('bg-[var(--color-primary)]');
    });
  });

  describe('Nested Route Highlighting', () => {
    it('should highlight "케이스 관리" for /lawyer/cases/123/evidence', () => {
      mockPathname.mockReturnValue('/lawyer/cases/123/evidence');
      render(<PortalSidebar {...defaultProps} />);

      const casesLink = screen.getByRole('link', { name: /케이스 관리/i });
      expect(casesLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "의뢰인 관리" for /lawyer/clients/456', () => {
      mockPathname.mockReturnValue('/lawyer/clients/456');
      render(<PortalSidebar {...defaultProps} />);

      const clientsLink = screen.getByRole('link', { name: /의뢰인 관리/i });
      expect(clientsLink).toHaveClass('bg-[var(--color-primary)]');
    });

    it('should highlight "메시지" for /lawyer/messages/thread/123', () => {
      mockPathname.mockReturnValue('/lawyer/messages/thread/123');
      render(<PortalSidebar {...defaultProps} />);

      const messagesLink = screen.getByRole('link', { name: /메시지/i });
      expect(messagesLink).toHaveClass('bg-[var(--color-primary)]');
    });
  });

  describe('Settings Link', () => {
    it('should render settings link in bottom section', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      // Settings link should exist
      const settingsLink = screen.getByRole('link', { name: /설정/i });
      expect(settingsLink).toBeInTheDocument();
      expect(settingsLink).toHaveAttribute('href', '/settings');
    });
  });

  describe('Badge Display', () => {
    it('should show badge on nav item when badge count is greater than 0', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const navItemsWithBadge = [...lawyerNavItems];
      const messagesIndex = navItemsWithBadge.findIndex(item => item.id === 'messages');
      navItemsWithBadge[messagesIndex] = { ...navItemsWithBadge[messagesIndex], badge: 5 };

      render(<PortalSidebar {...defaultProps} navItems={navItemsWithBadge} />);

      expect(screen.getByText('5')).toBeInTheDocument();
    });

    it('should not show badge when badge count is 0', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      // Messages badge should not be visible (badge is 0)
      const messagesLink = screen.getByRole('link', { name: /메시지/i });
      expect(messagesLink.querySelector('.bg-\\[var\\(--color-error\\)\\]')).not.toBeInTheDocument();
    });

    it('should show 99+ when badge count exceeds 99', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const navItemsWithHighBadge = [...lawyerNavItems];
      const messagesIndex = navItemsWithHighBadge.findIndex(item => item.id === 'messages');
      navItemsWithHighBadge[messagesIndex] = { ...navItemsWithHighBadge[messagesIndex], badge: 150 };

      render(<PortalSidebar {...defaultProps} navItems={navItemsWithHighBadge} />);

      expect(screen.getByText('99+')).toBeInTheDocument();
    });
  });

  describe('User Info Display', () => {
    it('should display user name and role', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      expect(screen.getByText('김변호사')).toBeInTheDocument();
    });

    it('should display user initials in avatar', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      render(<PortalSidebar {...defaultProps} />);

      // Should show first 2 characters of name uppercased
      expect(screen.getByText('김변')).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('should render sidebar with correct open/closed state', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar {...defaultProps} isOpen={false} />);

      const sidebar = container.querySelector('aside');
      expect(sidebar).toHaveClass('-translate-x-full');
    });

    it('should render sidebar visible when isOpen is true', () => {
      mockPathname.mockReturnValue('/lawyer/dashboard');
      const { container } = render(<PortalSidebar {...defaultProps} isOpen={true} />);

      const sidebar = container.querySelector('aside');
      expect(sidebar).toHaveClass('translate-x-0');
    });
  });
});
