/**
 * LiveRegion Component (T044)
 *
 * Provides screen reader announcements for dynamic content changes.
 * Uses ARIA live regions to announce updates to assistive technologies.
 *
 * Usage:
 * - Use 'polite' for non-urgent updates (loading complete, status changes)
 * - Use 'assertive' for urgent updates (errors, critical alerts)
 *
 * Example:
 * <LiveRegion message="파일이 업로드되었습니다" politeness="polite" />
 */

'use client';

import { useEffect, useState } from 'react';

export type LiveRegionPoliteness = 'polite' | 'assertive' | 'off';

interface LiveRegionProps {
  /**
   * Message to announce to screen readers
   */
  message: string;
  /**
   * Politeness level for the announcement
   * - 'polite': Waits for current speech to finish (default)
   * - 'assertive': Interrupts current speech immediately
   * - 'off': No announcement
   */
  politeness?: LiveRegionPoliteness;
  /**
   * Whether to clear message after announcement (default: true)
   */
  clearOnAnnounce?: boolean;
  /**
   * Delay before clearing message in ms (default: 1000)
   */
  clearDelay?: number;
}

export function LiveRegion({
  message,
  politeness = 'polite',
  clearOnAnnounce = true,
  clearDelay = 1000,
}: LiveRegionProps) {
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    if (message) {
      // Clear first to ensure re-announcement of same message
      setAnnouncement('');
      // Small delay to ensure DOM update triggers announcement
      const announceTimeout = setTimeout(() => {
        setAnnouncement(message);
      }, 100);

      // Clear after announcement if enabled
      let clearMessageTimeout: NodeJS.Timeout | undefined;
      if (clearOnAnnounce) {
        clearMessageTimeout = setTimeout(() => {
          setAnnouncement('');
        }, clearDelay + 100);
      }

      return () => {
        clearTimeout(announceTimeout);
        if (clearMessageTimeout) clearTimeout(clearMessageTimeout);
      };
    }
  }, [message, clearOnAnnounce, clearDelay]);

  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
}

/**
 * Hook for programmatic announcements
 */
export function useLiveRegion() {
  const [message, setMessage] = useState('');
  const [politeness, setPoliteness] = useState<LiveRegionPoliteness>('polite');

  const announce = (
    newMessage: string,
    level: LiveRegionPoliteness = 'polite'
  ) => {
    setPoliteness(level);
    setMessage(''); // Clear first
    setTimeout(() => setMessage(newMessage), 50);
  };

  const announcePolite = (newMessage: string) => announce(newMessage, 'polite');
  const announceAssertive = (newMessage: string) =>
    announce(newMessage, 'assertive');

  return {
    message,
    politeness,
    announce,
    announcePolite,
    announceAssertive,
    LiveRegionComponent: () => (
      <LiveRegion message={message} politeness={politeness} />
    ),
  };
}

/**
 * Global live region context provider
 * Use this in app layout for app-wide announcements
 */
export function LiveRegionProvider({ children }: { children: React.ReactNode }) {
  const { LiveRegionComponent } = useLiveRegion();

  return (
    <>
      {children}
      <LiveRegionComponent />
    </>
  );
}

export default LiveRegion;
