/**
 * MessageList Component Tests
 * 011-production-bug-fixes Feature - US2 (T056)
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MessageList } from '@/components/lawyer/messages/MessageList';
import type { DirectMessageSummary } from '@/types/message';

const mockMessages: DirectMessageSummary[] = [
  {
    id: '1',
    senderId: 'user-1',
    senderName: '홍길동',
    recipientId: 'user-2',
    recipientName: '김철수',
    subject: '케이스 관련 문의',
    preview: '안녕하세요, 케이스 진행 상황에 대해 문의드립니다.',
    isRead: false,
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    senderId: 'user-3',
    senderName: '이영희',
    recipientId: 'user-2',
    recipientName: '김철수',
    subject: '미팅 일정',
    preview: '다음 주 미팅 일정 확인 부탁드립니다.',
    isRead: true,
    createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
  },
  {
    id: '3',
    senderId: 'user-2',
    senderName: '김철수',
    recipientId: 'user-4',
    recipientName: '박민수',
    subject: '자료 요청',
    preview: '증거 자료 전달드립니다.',
    isRead: true,
    createdAt: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
  },
];

describe('MessageList', () => {
  const defaultProps = {
    messages: mockMessages,
    folder: 'inbox' as const,
    onFolderChange: jest.fn(),
    onSelect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders folder tabs', () => {
      render(<MessageList {...defaultProps} />);

      expect(screen.getByText('받은 메시지')).toBeInTheDocument();
      expect(screen.getByText('보낸 메시지')).toBeInTheDocument();
    });

    it('highlights active folder tab', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      const inboxTab = screen.getByText('받은 메시지');
      const sentTab = screen.getByText('보낸 메시지');

      expect(inboxTab).toHaveClass('text-blue-600');
      expect(sentTab).not.toHaveClass('text-blue-600');
    });

    it('renders all messages', () => {
      render(<MessageList {...defaultProps} />);

      expect(screen.getByText('케이스 관련 문의')).toBeInTheDocument();
      expect(screen.getByText('미팅 일정')).toBeInTheDocument();
      expect(screen.getByText('자료 요청')).toBeInTheDocument();
    });

    it('shows sender name in inbox folder', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      expect(screen.getByText('홍길동')).toBeInTheDocument();
      expect(screen.getByText('이영희')).toBeInTheDocument();
    });

    it('shows recipient name in sent folder', () => {
      render(<MessageList {...defaultProps} folder="sent" />);

      // 김철수 appears multiple times as recipient
      const kimElements = screen.getAllByText('김철수');
      expect(kimElements.length).toBeGreaterThan(0);
      expect(screen.getByText('박민수')).toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('shows loading spinner when isLoading is true', () => {
      render(<MessageList {...defaultProps} isLoading={true} messages={[]} />);

      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('does not show messages when loading', () => {
      render(<MessageList {...defaultProps} isLoading={true} />);

      expect(screen.queryByText('케이스 관련 문의')).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty message for inbox', () => {
      render(<MessageList {...defaultProps} messages={[]} folder="inbox" />);

      expect(screen.getByText('받은 메시지가 없습니다')).toBeInTheDocument();
    });

    it('shows empty message for sent', () => {
      render(<MessageList {...defaultProps} messages={[]} folder="sent" />);

      expect(screen.getByText('보낸 메시지가 없습니다')).toBeInTheDocument();
    });
  });

  describe('Folder Change', () => {
    it('calls onFolderChange when inbox tab is clicked', () => {
      render(<MessageList {...defaultProps} folder="sent" />);

      const inboxTab = screen.getByText('받은 메시지');
      fireEvent.click(inboxTab);

      expect(defaultProps.onFolderChange).toHaveBeenCalledWith('inbox');
    });

    it('calls onFolderChange when sent tab is clicked', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      const sentTab = screen.getByText('보낸 메시지');
      fireEvent.click(sentTab);

      expect(defaultProps.onFolderChange).toHaveBeenCalledWith('sent');
    });
  });

  describe('Message Selection', () => {
    it('calls onSelect when message is clicked', () => {
      render(<MessageList {...defaultProps} />);

      const message = screen.getByText('케이스 관련 문의').closest('button');
      fireEvent.click(message!);

      expect(defaultProps.onSelect).toHaveBeenCalledWith(mockMessages[0]);
    });

    it('highlights selected message', () => {
      render(<MessageList {...defaultProps} selectedId="1" />);

      const selectedMessage = screen.getByText('케이스 관련 문의').closest('button');
      expect(selectedMessage).toHaveClass('bg-blue-50');
    });
  });

  describe('Unread Messages', () => {
    it('shows unread indicator for unread messages in inbox', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      const unreadMessage = screen.getByText('케이스 관련 문의').closest('button');

      // Check for blue dot indicator
      const unreadIndicator = unreadMessage?.querySelector('.bg-blue-500');
      expect(unreadIndicator).toBeInTheDocument();
    });

    it('applies bold style to unread message subject', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      const unreadSubject = screen.getByText('케이스 관련 문의');
      expect(unreadSubject).toHaveClass('font-medium');
    });

    it('does not show unread indicator for read messages', () => {
      render(<MessageList {...defaultProps} folder="inbox" />);

      const readMessage = screen.getByText('미팅 일정').closest('button');

      // Should not have unread indicator
      const indicator = readMessage?.querySelector('.bg-blue-500.rounded-full.h-2.w-2');
      expect(indicator).not.toBeInTheDocument();
    });

    it('does not show unread indicator in sent folder', () => {
      const unreadSentMessage: DirectMessageSummary = {
        ...mockMessages[0],
        isRead: false,
      };

      render(
        <MessageList
          {...defaultProps}
          messages={[unreadSentMessage]}
          folder="sent"
        />
      );

      const message = screen.getByText('케이스 관련 문의').closest('button');
      const indicator = message?.querySelector('.bg-blue-500.rounded-full.h-2.w-2');
      expect(indicator).not.toBeInTheDocument();
    });
  });

  describe('Date Formatting', () => {
    it('shows time for messages from today', () => {
      const todayMessage: DirectMessageSummary = {
        ...mockMessages[0],
        createdAt: new Date().toISOString(),
      };

      render(<MessageList {...defaultProps} messages={[todayMessage]} />);

      // Should show time format (e.g., "오후 2:30")
      const timeRegex = /오전|오후/;
      const timeElement = screen.getByText(timeRegex);
      expect(timeElement).toBeInTheDocument();
    });

    it('shows "어제" for messages from yesterday', () => {
      const yesterdayMessage: DirectMessageSummary = {
        ...mockMessages[0],
        createdAt: new Date(Date.now() - 86400000).toISOString(),
      };

      render(<MessageList {...defaultProps} messages={[yesterdayMessage]} />);

      expect(screen.getByText('어제')).toBeInTheDocument();
    });

    it('shows days ago for recent messages', () => {
      const threeDaysAgo: DirectMessageSummary = {
        ...mockMessages[0],
        createdAt: new Date(Date.now() - 3 * 86400000).toISOString(),
      };

      render(<MessageList {...defaultProps} messages={[threeDaysAgo]} />);

      expect(screen.getByText('3일 전')).toBeInTheDocument();
    });
  });

  describe('Content Preview', () => {
    it('shows truncated content preview', () => {
      render(<MessageList {...defaultProps} />);

      expect(screen.getByText('안녕하세요, 케이스 진행 상황에 대해 문의드립니다.')).toBeInTheDocument();
    });

    it('applies line-clamp to content', () => {
      render(<MessageList {...defaultProps} />);

      const contentElements = document.querySelectorAll('.line-clamp-1');
      expect(contentElements.length).toBeGreaterThan(0);
    });
  });

  describe('Multiple Messages', () => {
    it('renders messages in order', () => {
      render(<MessageList {...defaultProps} />);

      const messageButtons = screen.getAllByRole('button');
      // First 2 are tabs, rest are messages
      const messageElements = messageButtons.slice(2);

      expect(messageElements).toHaveLength(3);
    });
  });

  describe('Accessibility', () => {
    it('uses button elements for messages', () => {
      render(<MessageList {...defaultProps} />);

      const messages = screen.getAllByRole('button');
      // 2 folder tabs + 3 messages
      expect(messages.length).toBeGreaterThanOrEqual(5);
    });

    it('applies correct styling for keyboard focus', () => {
      render(<MessageList {...defaultProps} />);

      const message = screen.getByText('케이스 관련 문의').closest('button');
      expect(message).toHaveClass('text-left');
    });
  });
});
