/**
 * CommandPalette - Global search command palette using cmdk
 * User Story 6: Global Search
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Command } from 'cmdk';
import { useRouter } from 'next/navigation';
import { useGlobalSearch } from '@/hooks/useGlobalSearch';
import { useKeyboardShortcuts, getModifierKey } from '@/hooks/useKeyboardShortcuts';
import { CATEGORY_CONFIG, type SearchCategory } from '@/types/search';

interface CommandPaletteProps {
  className?: string;
}

export function CommandPalette({ className }: CommandPaletteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const {
    query,
    setQuery,
    results,
    isLoading,
    error,
    quickAccess,
    clearResults,
  } = useGlobalSearch({ debounceMs: 300 });

  // Open command palette with Cmd/Ctrl + K
  useKeyboardShortcuts({
    shortcuts: [
      {
        key: 'k',
        metaKey: true,
        action: () => setIsOpen(true),
        description: '검색 팔레트 열기',
      },
    ],
  });

  // Close on escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Handle item selection
  const handleSelect = useCallback(
    (url: string | null) => {
      if (url) {
        router.push(url);
        setIsOpen(false);
        clearResults();
      }
    },
    [router, clearResults]
  );

  // Handle close
  const handleClose = useCallback(() => {
    setIsOpen(false);
    clearResults();
  }, [clearResults]);

  // Group results by category
  const groupedResults = results.reduce((acc, result) => {
    if (!acc[result.category]) {
      acc[result.category] = [];
    }
    acc[result.category].push(result);
    return acc;
  }, {} as Record<SearchCategory, typeof results>);

  const modKey = getModifierKey();

  if (!isOpen) {
    return null;
  }

  return (
    <div className={`fixed inset-0 z-50 ${className || ''}`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Command Dialog */}
      <div className="absolute left-1/2 top-[20%] -translate-x-1/2 w-full max-w-xl">
        <Command
          className="bg-white dark:bg-neutral-800 rounded-xl shadow-2xl overflow-hidden border dark:border-neutral-700"
          shouldFilter={false}
        >
          {/* Search Input */}
          <div className="flex items-center border-b dark:border-neutral-700 px-4">
            <svg
              className="w-5 h-5 text-gray-400 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="사건, 의뢰인, 증거 검색..."
              className="flex-1 py-4 text-base outline-none placeholder-gray-400 dark:bg-neutral-800 dark:text-gray-100"
              autoFocus
            />
            {isLoading && (
              <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
            )}
            <kbd className="ml-3 px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-neutral-700 text-gray-500 dark:text-gray-400 rounded">
              ESC
            </kbd>
          </div>

          {/* Results */}
          <Command.List className="max-h-96 overflow-y-auto p-2">
            {/* Error state */}
            {error && (
              <div className="px-4 py-8 text-center text-red-500 dark:text-red-400">
                <p>{error}</p>
              </div>
            )}

            {/* Empty state with quick access */}
            {!query && !error && (
              <>
                {/* Today's events */}
                {quickAccess.todaysEvents.length > 0 && (
                  <Command.Group heading="오늘의 일정">
                    {quickAccess.todaysEvents.map((event) => (
                      <Command.Item
                        key={event.id}
                        value={`event-${event.id}`}
                        onSelect={() => handleSelect(`/lawyer/calendar?event=${event.id}`)}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                      >
                        <span className="text-lg">📅</span>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {event.title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{event.time}</p>
                        </div>
                      </Command.Item>
                    ))}
                  </Command.Group>
                )}

                {/* Quick actions */}
                <Command.Group heading="바로가기">
                  <Command.Item
                    value="new-case"
                    onSelect={() => handleSelect('/lawyer/cases/new')}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                  >
                    <span className="text-lg">➕</span>
                    <span className="text-sm dark:text-gray-100">새 사건 등록</span>
                  </Command.Item>
                  <Command.Item
                    value="dashboard"
                    onSelect={() => handleSelect('/lawyer/dashboard')}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                  >
                    <span className="text-lg">🏠</span>
                    <span className="text-sm dark:text-gray-100">대시보드</span>
                  </Command.Item>
                  <Command.Item
                    value="calendar"
                    onSelect={() => handleSelect('/lawyer/calendar')}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                  >
                    <span className="text-lg">📆</span>
                    <span className="text-sm dark:text-gray-100">캘린더</span>
                  </Command.Item>
                </Command.Group>

                {/* Recent searches */}
                {quickAccess.recentSearches.length > 0 && (
                  <Command.Group heading="최근 검색">
                    {quickAccess.recentSearches.map((term, index) => (
                      <Command.Item
                        key={`recent-${index}`}
                        value={`recent-${term}`}
                        onSelect={() => setQuery(term)}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                      >
                        <span className="text-lg">🕐</span>
                        <span className="text-sm text-gray-600 dark:text-gray-300">{term}</span>
                      </Command.Item>
                    ))}
                  </Command.Group>
                )}
              </>
            )}

            {/* Search results */}
            {query && !error && results.length === 0 && !isLoading && (
              <Command.Empty className="py-8 text-center text-gray-500 dark:text-gray-400">
                검색 결과가 없습니다
              </Command.Empty>
            )}

            {query && !error && Object.entries(groupedResults).map(([category, items]) => {
              const config = CATEGORY_CONFIG[category as SearchCategory];
              return (
                <Command.Group key={category} heading={config.label}>
                  {items.map((item) => (
                    <Command.Item
                      key={item.id}
                      value={`${category}-${item.id}`}
                      onSelect={() => handleSelect(item.url)}
                      className="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-neutral-700 data-[selected=true]:bg-blue-50 data-[selected=true]:dark:bg-blue-900/30"
                    >
                      <span className={`text-lg ${config.color}`}>{config.icon}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {item.title}
                        </p>
                        {item.subtitle && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                            {item.subtitle}
                          </p>
                        )}
                      </div>
                    </Command.Item>
                  ))}
                </Command.Group>
              );
            })}
          </Command.List>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-2 border-t dark:border-neutral-700 bg-gray-50 dark:bg-neutral-900 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-4">
              <span>
                <kbd className="px-1.5 py-0.5 font-mono bg-gray-200 dark:bg-neutral-700 rounded">↑↓</kbd> 이동
              </span>
              <span>
                <kbd className="px-1.5 py-0.5 font-mono bg-gray-200 dark:bg-neutral-700 rounded">Enter</kbd> 선택
              </span>
            </div>
            <span>
              <kbd className="px-1.5 py-0.5 font-mono bg-gray-200 dark:bg-neutral-700 rounded">{modKey} K</kbd> 검색
            </span>
          </div>
        </Command>
      </div>
    </div>
  );
}
