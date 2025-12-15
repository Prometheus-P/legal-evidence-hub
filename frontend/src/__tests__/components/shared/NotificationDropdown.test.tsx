/**
 * NotificationDropdown Component Tests
 * 011-production-bug-fixes Feature - US2 (T055)
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { NotificationDropdown } from '@/components/shared/NotificationDropdown';
import * as useNotificationsHook from '@/hooks/useNotifications';

// Mock the useNotifications hook
jest.mock('@/hooks/useNotifications');

const mockNotifications = [
  {
    id: '1',
    type: 'case_update' as const,
    title: '케이스 업데이트',
    content: '새로운 증거가 업로드되었습니다.',
    isRead: false,
    relatedId: 'case-123',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    type: 'message' as const,
    title: '새 메시지',
    content: '홍길동님이 메시지를 보냈습니다.',
    isRead: true,
    createdAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
  },
  {
    id: '3',
    type: 'system' as const,
    title: '시스템 공지',
    content: '시스템 점검 안내입니다.',
    isRead: false,
    createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
  },
];

const mockUseNotifications = {
  notifications: mockNotifications,
  unreadCount: 2,
  isLoading: false,
  error: null,
  markAsRead: jest.fn(),
  markAllAsRead: jest.fn(),
  refetch: jest.fn(),
};

describe('NotificationDropdown', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue(mockUseNotifications);
  });

  describe('Rendering', () => {
    it('renders notification badge with unread count', () => {
      render(<NotificationDropdown />);

      expect(screen.getByText('2')).toBeInTheDocument();
      expect(screen.getByLabelText('2개의 읽지 않은 알림')).toBeInTheDocument();
    });

    it('does not show badge when unread count is 0', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        unreadCount: 0,
      });

      render(<NotificationDropdown />);

      expect(screen.queryByText('0')).not.toBeInTheDocument();
    });

    it('shows 99+ for counts over 99', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        unreadCount: 150,
      });

      render(<NotificationDropdown />);

      expect(screen.getByText('99+')).toBeInTheDocument();
    });
  });

  describe('Dropdown Toggle', () => {
    it('opens dropdown when badge is clicked', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      expect(screen.getByText('알림')).toBeInTheDocument();
      expect(screen.getByText('모두 읽음')).toBeInTheDocument();
    });

    it('closes dropdown when clicking outside', async () => {
      render(
        <div>
          <NotificationDropdown />
          <div data-testid="outside">Outside</div>
        </div>
      );

      // Open dropdown
      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);
      expect(screen.getByText('알림')).toBeInTheDocument();

      // Click outside
      fireEvent.mouseDown(screen.getByTestId('outside'));

      await waitFor(() => {
        expect(screen.queryByText('모두 읽음')).not.toBeInTheDocument();
      });
    });

    it('calls refetch when dropdown is opened', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      expect(mockUseNotifications.refetch).toHaveBeenCalled();
    });
  });

  describe('Notification List', () => {
    it('displays all notifications', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      expect(screen.getByText('케이스 업데이트')).toBeInTheDocument();
      expect(screen.getByText('새 메시지')).toBeInTheDocument();
      expect(screen.getByText('시스템 공지')).toBeInTheDocument();
    });

    it('shows loading state', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        isLoading: true,
        notifications: [],
      });

      render(<NotificationDropdown />);

      const badge = screen.getByRole('button');
      fireEvent.click(badge);

      // Check for spinner (animated element)
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('shows error message', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        error: '알림을 불러오는 중 오류가 발생했습니다.',
        notifications: [],
      });

      render(<NotificationDropdown />);

      const badge = screen.getByRole('button');
      fireEvent.click(badge);

      expect(screen.getByText('알림을 불러오는 중 오류가 발생했습니다.')).toBeInTheDocument();
    });

    it('shows empty state when no notifications', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        notifications: [],
        unreadCount: 0,
      });

      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('알림');
      fireEvent.click(badge);

      expect(screen.getByText('알림이 없습니다')).toBeInTheDocument();
    });
  });

  describe('Mark as Read', () => {
    it('calls markAsRead when notification is clicked', async () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      const notification = screen.getByText('케이스 업데이트').closest('button');
      fireEvent.click(notification!);

      await waitFor(() => {
        expect(mockUseNotifications.markAsRead).toHaveBeenCalledWith('1');
      });
    });

    it('calls markAllAsRead when "모두 읽음" is clicked', async () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      const markAllButton = screen.getByText('모두 읽음');
      fireEvent.click(markAllButton);

      await waitFor(() => {
        expect(mockUseNotifications.markAllAsRead).toHaveBeenCalled();
      });
    });

    it('does not show "모두 읽음" button when unread count is 0', () => {
      (useNotificationsHook.useNotifications as jest.Mock).mockReturnValue({
        ...mockUseNotifications,
        unreadCount: 0,
      });

      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('알림');
      fireEvent.click(badge);

      expect(screen.queryByText('모두 읽음')).not.toBeInTheDocument();
    });
  });

  describe('Footer Link', () => {
    it('renders link to all notifications page', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      const allNotificationsLink = screen.getByText('모든 알림 보기');
      expect(allNotificationsLink).toHaveAttribute('href', '/lawyer/notifications');
    });
  });

  describe('Notification Types', () => {
    it('displays correct icon for case_update type', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      // Case update notification should have blue icon
      const caseUpdateItem = screen.getByText('케이스 업데이트').closest('button');
      const icon = caseUpdateItem?.querySelector('svg');
      expect(icon).toHaveClass('text-blue-500');
    });

    it('displays correct icon for message type', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      // Message notification should have green icon
      const messageItem = screen.getByText('새 메시지').closest('button');
      const icon = messageItem?.querySelector('svg');
      expect(icon).toHaveClass('text-green-500');
    });

    it('displays correct icon for system type', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      // System notification should have gray icon
      const systemItem = screen.getByText('시스템 공지').closest('button');
      const icon = systemItem?.querySelector('svg');
      expect(icon).toHaveClass('text-gray-500');
    });
  });

  describe('Unread Indicator', () => {
    it('shows unread indicator for unread notifications', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      // Unread notifications should have blue background
      const unreadItem = screen.getByText('케이스 업데이트').closest('button');
      expect(unreadItem).toHaveClass('bg-blue-50');
    });

    it('does not show unread indicator for read notifications', () => {
      render(<NotificationDropdown />);

      const badge = screen.getByLabelText('2개의 읽지 않은 알림');
      fireEvent.click(badge);

      // Read notifications should not have blue background
      const readItem = screen.getByText('새 메시지').closest('button');
      expect(readItem).not.toHaveClass('bg-blue-50');
    });
  });
});
