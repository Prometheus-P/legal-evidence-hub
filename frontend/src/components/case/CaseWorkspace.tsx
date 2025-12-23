'use client';

/**
 * CaseWorkspace - M3 Supporting Pane Layout Container
 * 014-ui-settings-completion Feature
 *
 * 3-column layout for case detail page:
 * - Left Panel (240px): Data lists (evidence, consultation, assets)
 * - Main Workspace (flex-1): Core work area (fact summary, analysis, draft)
 * - Right Panel (280px): Context (timeline mini, relations mini, asset summary)
 *
 * All panels are collapsible for flexible workspace management.
 */

import { useState, ReactNode } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface CaseWorkspaceProps {
  leftPanel: ReactNode;
  mainContent: ReactNode;
  rightPanel: ReactNode;
  leftPanelTitle?: string;
  rightPanelTitle?: string;
  defaultLeftOpen?: boolean;
  defaultRightOpen?: boolean;
}

export function CaseWorkspace({
  leftPanel,
  mainContent,
  rightPanel,
  leftPanelTitle = '자료',
  rightPanelTitle = '컨텍스트',
  defaultLeftOpen = true,
  defaultRightOpen = false,
}: CaseWorkspaceProps) {
  const [leftOpen, setLeftOpen] = useState(defaultLeftOpen);
  const [rightOpen, setRightOpen] = useState(defaultRightOpen);

  return (
    <div className="flex h-full min-h-[600px] bg-[var(--color-bg-secondary)]">
      {/* Left Panel - Data Lists */}
      <aside
        className={`
          relative flex-shrink-0 bg-white dark:bg-neutral-800
          border-r border-gray-200 dark:border-neutral-700
          transition-all duration-300 ease-in-out
          ${leftOpen ? 'w-60' : 'w-0'}
        `}
      >
        {leftOpen && (
          <div className="h-full flex flex-col">
            {/* Panel Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-neutral-700">
              <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
                {leftPanelTitle}
              </h3>
              <button
                onClick={() => setLeftOpen(false)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-neutral-700 text-[var(--color-text-secondary)]"
                aria-label="좌측 패널 접기"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </div>
            {/* Panel Content */}
            <div className="flex-1 overflow-y-auto">
              {leftPanel}
            </div>
          </div>
        )}

        {/* Left Panel Toggle (when collapsed) */}
        {!leftOpen && (
          <button
            onClick={() => setLeftOpen(true)}
            className="absolute -right-8 top-4 p-1.5 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-r-md shadow-sm hover:bg-gray-50 dark:hover:bg-neutral-700 text-[var(--color-text-secondary)]"
            aria-label="좌측 패널 열기"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </aside>

      {/* Main Workspace */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <div className="p-6">
          {mainContent}
        </div>
      </main>

      {/* Right Panel - Context */}
      <aside
        className={`
          relative flex-shrink-0 bg-white dark:bg-neutral-800
          border-l border-gray-200 dark:border-neutral-700
          transition-all duration-300 ease-in-out
          ${rightOpen ? 'w-70' : 'w-0'}
        `}
      >
        {/* Right Panel Toggle (when collapsed) */}
        {!rightOpen && (
          <button
            onClick={() => setRightOpen(true)}
            className="absolute -left-8 top-4 p-1.5 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-l-md shadow-sm hover:bg-gray-50 dark:hover:bg-neutral-700 text-[var(--color-text-secondary)]"
            aria-label="우측 패널 열기"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}

        {rightOpen && (
          <div className="h-full flex flex-col w-70">
            {/* Panel Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-neutral-700">
              <button
                onClick={() => setRightOpen(false)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-neutral-700 text-[var(--color-text-secondary)]"
                aria-label="우측 패널 접기"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
              <h3 className="text-sm font-semibold text-[var(--color-text-primary)]">
                {rightPanelTitle}
              </h3>
            </div>
            {/* Panel Content */}
            <div className="flex-1 overflow-y-auto">
              {rightPanel}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}

export default CaseWorkspace;
