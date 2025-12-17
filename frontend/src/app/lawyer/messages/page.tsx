/**
 * Lawyer Messages Page
 * 003-role-based-ui Feature - US6
 * Updated: 011-production-bug-fixes - US2 (T046)
 *
 * Messages page with tabs for case messages and direct messages.
 */

'use client';

import { Suspense, useState } from 'react';
import { MessagesPageContent } from '@/components/messages';
import { MessageList } from '@/components/lawyer/messages/MessageList';
import { DirectMessageView } from '@/components/lawyer/messages/DirectMessageView';
import { ComposeMessage } from '@/components/lawyer/messages/ComposeMessage';
import { useRole } from '@/hooks/useRole';
import { useDirectMessages } from '@/hooks/useDirectMessages';
import type { DirectMessage, DirectMessageSummary, DirectMessageCreate } from '@/types/message';

type TabType = 'case' | 'direct';

function DirectMessagesSection({ userId }: { userId: string }) {
  const [folder, setFolder] = useState<'inbox' | 'sent'>('inbox');
  const [selectedMessage, setSelectedMessage] = useState<DirectMessage | null>(null);
  const [isComposing, setIsComposing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const {
    messages,
    isLoading,
    error,
    send,
    remove,
    markAsRead,
    fetchMessage,
    refetch,
  } = useDirectMessages({ folder });

  // Suppress unused warning - userId is for future user-specific features
  void userId;

  const handleFolderChange = (newFolder: 'inbox' | 'sent') => {
    setFolder(newFolder);
    setSelectedMessage(null);
  };

  const handleSelectMessage = async (summary: DirectMessageSummary) => {
    setIsComposing(false);
    // Fetch full message content
    const fullMessage = await fetchMessage(summary.id);
    if (fullMessage) {
      setSelectedMessage(fullMessage);
      if (!summary.isRead && folder === 'inbox') {
        await markAsRead(summary.id);
      }
    }
  };

  const handleCompose = () => {
    setIsComposing(true);
    setSelectedMessage(null);
  };

  const handleSend = async (data: DirectMessageCreate) => {
    const result = await send(data);
    if (result) {
      setIsComposing(false);
      setFolder('sent');
      refetch();
    }
  };

  const handleReply = async (data: DirectMessageCreate) => {
    const result = await send(data);
    if (result) {
      refetch();
    }
  };

  const handleDelete = async (messageId: string) => {
    setIsDeleting(true);
    const success = await remove(messageId);
    if (success) {
      setSelectedMessage(null);
    }
    setIsDeleting(false);
  };

  return (
    <div className="flex h-full">
      {/* Left: Message List */}
      <div className="w-80 flex-shrink-0">
        <div className="flex h-12 items-center justify-between border-b border-gray-200 px-4">
          <span className="text-sm font-medium text-gray-700">직접 메시지</span>
          <button
            type="button"
            onClick={handleCompose}
            className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs text-white hover:bg-blue-700"
          >
            + 새 메시지
          </button>
        </div>
        {error && (
          <div className="px-4 py-2 text-sm text-red-500">{error}</div>
        )}
        <MessageList
          messages={messages}
          selectedId={selectedMessage?.id}
          isLoading={isLoading}
          folder={folder}
          onFolderChange={handleFolderChange}
          onSelect={handleSelectMessage}
        />
      </div>

      {/* Right: Message View or Compose */}
      <div className="flex-1">
        {isComposing ? (
          <ComposeMessage
            onSend={handleSend}
            onCancel={() => setIsComposing(false)}
          />
        ) : (
          <DirectMessageView
            message={selectedMessage}
            onReply={handleReply}
            onDelete={handleDelete}
            onCompose={handleCompose}
            isDeleting={isDeleting}
          />
        )}
      </div>
    </div>
  );
}

function LawyerMessagesPageContent() {
  const { user, isAuthenticated } = useRole();
  const [activeTab, setActiveTab] = useState<TabType>('direct');

  if (!isAuthenticated || !user) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <p className="text-gray-500">로그인이 필요합니다.</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 bg-white">
        <button
          type="button"
          onClick={() => setActiveTab('direct')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'direct'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          직접 메시지
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('case')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'case'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          케이스 메시지
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'direct' ? (
          <DirectMessagesSection userId={user.id} />
        ) : (
          <MessagesPageContent portalType="lawyer" currentUserId={user.id} />
        )}
      </div>
    </div>
  );
}

export default function LawyerMessagesPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        </div>
      }
    >
      <LawyerMessagesPageContent />
    </Suspense>
  );
}
