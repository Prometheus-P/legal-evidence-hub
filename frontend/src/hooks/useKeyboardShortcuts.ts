/**
 * useKeyboardShortcuts hook for LEH Lawyer Portal v1
 * User Story 6: Global Search - Keyboard shortcuts
 */

'use client';

import { useEffect, useCallback, useRef } from 'react';

interface ShortcutConfig {
  key: string;
  metaKey?: boolean; // Cmd on Mac, Ctrl on Windows
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: () => void;
  description?: string;
  enabled?: boolean;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: ShortcutConfig[];
  enabled?: boolean;
}

/**
 * Hook for handling global keyboard shortcuts
 */
export function useKeyboardShortcuts({
  shortcuts,
  enabled = true,
}: UseKeyboardShortcutsOptions): void {
  const shortcutsRef = useRef(shortcuts);
  shortcutsRef.current = shortcuts;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Don't trigger shortcuts when typing in input fields
      const target = event.target as HTMLElement;
      const isInputField =
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable;

      for (const shortcut of shortcutsRef.current) {
        if (shortcut.enabled === false) continue;

        // Guard against undefined event.key (some special keys)
        if (!event.key || !shortcut.key) continue;

        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const metaMatch = shortcut.metaKey ? event.metaKey || event.ctrlKey : true;
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey : true;
        const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.altKey ? event.altKey : !event.altKey;

        // For shortcuts requiring meta/ctrl, allow even in input fields
        const requiresModifier = shortcut.metaKey || shortcut.ctrlKey;

        if (keyMatch && metaMatch && ctrlMatch && shiftMatch && altMatch) {
          if (!isInputField || requiresModifier) {
            event.preventDefault();
            event.stopPropagation();
            shortcut.action();
            return;
          }
        }
      }
    },
    [enabled]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown, true);
    return () => {
      window.removeEventListener('keydown', handleKeyDown, true);
    };
  }, [handleKeyDown]);
}

/**
 * Helper to detect OS for showing correct shortcut key
 */
export function getModifierKey(): string {
  if (typeof window === 'undefined') return 'Ctrl';
  // navigator.platform is deprecated, use userAgent as fallback
  const platform = navigator.platform || navigator.userAgent || '';
  const isMac = platform.toUpperCase().indexOf('MAC') >= 0;
  return isMac ? '⌘' : 'Ctrl';
}

/**
 * Format shortcut for display
 */
export function formatShortcut(shortcut: ShortcutConfig): string {
  const parts: string[] = [];
  const modKey = getModifierKey();

  if (shortcut.metaKey) {
    parts.push(modKey);
  }
  if (shortcut.ctrlKey && !shortcut.metaKey) {
    parts.push('Ctrl');
  }
  if (shortcut.shiftKey) {
    parts.push('Shift');
  }
  if (shortcut.altKey) {
    parts.push('Alt');
  }
  // Guard against undefined shortcut.key
  if (shortcut.key) {
    parts.push(shortcut.key.toUpperCase());
  }

  return parts.join(' + ');
}
