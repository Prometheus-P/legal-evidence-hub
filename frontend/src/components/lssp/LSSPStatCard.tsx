/**
 * LSSPStatCard Component
 *
 * Expandable stat card for LSSP panel.
 * Shows count and summary at a glance, expands to show full content.
 */

'use client';

import { useState, ReactNode } from 'react';
import { ChevronDown, ChevronUp, LucideIcon } from 'lucide-react';

interface LSSPStatCardProps {
  icon: LucideIcon;
  label: string;
  count: number | undefined;
  description?: string;
  iconColor: string;
  bgColor: string;
  children: ReactNode;
  defaultExpanded?: boolean;
}

export function LSSPStatCard({
  icon: Icon,
  label,
  count,
  description,
  iconColor,
  bgColor,
  children,
  defaultExpanded = false,
}: LSSPStatCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden">
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${bgColor}`}>
            <Icon className={`w-5 h-5 ${iconColor}`} />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="font-medium text-neutral-900 dark:text-white">{label}</span>
              {count !== undefined && (
                <span className="px-2 py-0.5 bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-300 text-xs rounded-full">
                  {count}
                </span>
              )}
            </div>
            {description && (
              <p className="text-sm text-neutral-500 dark:text-neutral-400">{description}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-neutral-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-neutral-400" />
          )}
        </div>
      </button>

      {/* Expandable content */}
      {isExpanded && (
        <div className="border-t border-neutral-200 dark:border-neutral-700 p-4">
          {children}
        </div>
      )}
    </div>
  );
}

export default LSSPStatCard;
