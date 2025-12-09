/**
 * KeyboardShortcutsHelp - Modal showing available keyboard shortcuts
 * Phase 11: Polish & Cross-Cutting Concerns
 *
 * Opens with ? key, displays all available shortcuts
 */

'use client';

import { useState, useEffect } from 'react';
import { X, Keyboard } from 'lucide-react';
import { getModifierKey } from '@/hooks/useKeyboardShortcuts';

interface ShortcutItem {
  keys: string[];
  description: string;
  category: string;
}

// All available shortcuts in the application
const SHORTCUTS: ShortcutItem[] = [
  // Navigation
  { keys: ['⌘/Ctrl', 'K'], description: '검색 팔레트 열기', category: '검색' },
  { keys: ['Esc'], description: '모달/팔레트 닫기', category: '검색' },
  { keys: ['↑', '↓'], description: '검색 결과 이동', category: '검색' },
  { keys: ['Enter'], description: '검색 결과 선택', category: '검색' },

  // General
  { keys: ['?'], description: '단축키 도움말', category: '일반' },

  // Dark Mode
  { keys: ['⌘/Ctrl', 'Shift', 'L'], description: '다크모드 전환', category: '테마' },

  // Editor (when in input)
  { keys: ['⌘/Ctrl', 'S'], description: '저장', category: '편집' },
  { keys: ['⌘/Ctrl', 'Z'], description: '실행 취소', category: '편집' },
  { keys: ['⌘/Ctrl', 'Shift', 'Z'], description: '다시 실행', category: '편집' },
];

interface KeyboardShortcutsHelpProps {
  className?: string;
}

export function KeyboardShortcutsHelp({ className }: KeyboardShortcutsHelpProps) {
  const [isOpen, setIsOpen] = useState(false);
  const modKey = getModifierKey();

  // Replace ⌘/Ctrl with actual modifier key
  const getDisplayKeys = (keys: string[]) =>
    keys.map((key) => (key === '⌘/Ctrl' ? modKey : key));

  // Listen for ? key to open modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger when typing in input fields
      const target = e.target as HTMLElement;
      const isInputField =
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable;

      if (isInputField) return;

      // ? key (shift + /)
      if (e.key === '?' || (e.shiftKey && e.key === '/')) {
        e.preventDefault();
        setIsOpen(true);
      }

      // Close on Escape
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Group shortcuts by category
  const groupedShortcuts = SHORTCUTS.reduce(
    (acc, shortcut) => {
      if (!acc[shortcut.category]) {
        acc[shortcut.category] = [];
      }
      acc[shortcut.category].push(shortcut);
      return acc;
    },
    {} as Record<string, ShortcutItem[]>
  );

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 ${className || ''}`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setIsOpen(false)}
      />

      {/* Modal */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-lg">
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-2xl overflow-hidden border border-gray-200 dark:border-neutral-700">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-neutral-700">
            <div className="flex items-center gap-3">
              <Keyboard className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                키보드 단축키
              </h2>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[60vh] overflow-y-auto">
            {Object.entries(groupedShortcuts).map(([category, shortcuts]) => (
              <div key={category} className="mb-6 last:mb-0">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                  {category}
                </h3>
                <div className="space-y-2">
                  {shortcuts.map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between py-2"
                    >
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {shortcut.description}
                      </span>
                      <div className="flex items-center gap-1">
                        {getDisplayKeys(shortcut.keys).map((key, keyIndex) => (
                          <span key={keyIndex}>
                            <kbd className="px-2 py-1 text-xs font-mono bg-gray-100 dark:bg-neutral-700 text-gray-700 dark:text-gray-300 rounded border border-gray-200 dark:border-neutral-600">
                              {key}
                            </kbd>
                            {keyIndex < shortcut.keys.length - 1 && (
                              <span className="text-gray-400 dark:text-gray-500 mx-0.5">
                                +
                              </span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="px-6 py-3 border-t border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-900/50">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              <kbd className="px-1.5 py-0.5 font-mono bg-gray-200 dark:bg-neutral-700 rounded text-xs">
                ?
              </kbd>{' '}
              키로 언제든지 이 도움말을 열 수 있습니다
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default KeyboardShortcutsHelp;
