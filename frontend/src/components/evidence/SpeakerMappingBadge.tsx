/**
 * Speaker Mapping Badge Component
 * 015-evidence-speaker-mapping: T026, T027, T028
 *
 * 증거 목록에서 화자 매핑 상태를 표시하는 뱃지
 */

'use client';

import { useState } from 'react';
import { Users, UserCheck } from 'lucide-react';
import type { SpeakerMapping } from '@/types/evidence';

interface SpeakerMappingBadgeProps {
  /** Whether this evidence has speaker mapping configured */
  hasSpeakerMapping?: boolean;
  /** The actual speaker mapping (for tooltip display) */
  speakerMapping?: SpeakerMapping;
  /** Click handler to open mapping modal */
  onClick?: () => void;
  /** Size variant */
  size?: 'sm' | 'md';
  /** Whether to show as interactive (clickable) */
  interactive?: boolean;
}

export function SpeakerMappingBadge({
  hasSpeakerMapping,
  speakerMapping,
  onClick,
  size = 'sm',
  interactive = true,
}: SpeakerMappingBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  // Determine if mapping exists
  const isMapped = hasSpeakerMapping || (speakerMapping && Object.keys(speakerMapping).length > 0);

  // Get mapping count for display
  const mappingCount = speakerMapping ? Object.keys(speakerMapping).length : 0;

  // Size classes
  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-1',
  };

  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';

  // If no mapping and not interactive, don't render anything
  if (!isMapped && !interactive) {
    return null;
  }

  // T028: Build tooltip content with mapped parties
  const tooltipContent = () => {
    if (!speakerMapping || Object.keys(speakerMapping).length === 0) {
      return '화자 매핑 미설정';
    }

    return (
      <div className="space-y-1">
        <div className="font-medium mb-1">화자 매핑</div>
        {Object.entries(speakerMapping).map(([speaker, item]) => (
          <div key={speaker} className="flex justify-between gap-3 text-xs">
            <span className="text-gray-300">&quot;{speaker}&quot;</span>
            <span className="text-white font-medium">→ {item.party_name}</span>
          </div>
        ))}
      </div>
    );
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick?.();
  };

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={interactive ? handleClick : undefined}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        disabled={!interactive}
        className={`
          inline-flex items-center gap-1 rounded-full font-medium transition-colors
          ${sizeClasses[size]}
          ${
            isMapped
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
              : 'bg-gray-100 dark:bg-neutral-700 text-gray-500 dark:text-gray-400'
          }
          ${
            interactive
              ? 'cursor-pointer hover:bg-green-200 dark:hover:bg-green-900/50'
              : 'cursor-default'
          }
        `}
        title={isMapped ? `${mappingCount}명 매핑됨` : '화자 매핑 설정'}
      >
        {isMapped ? (
          <>
            <UserCheck className={iconSize} />
            <span>{mappingCount}명</span>
          </>
        ) : (
          <>
            <Users className={iconSize} />
            <span>매핑</span>
          </>
        )}
      </button>

      {/* T028: Tooltip showing mapped parties */}
      {showTooltip && speakerMapping && Object.keys(speakerMapping).length > 0 && (
        <div
          className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2
                     bg-gray-900 dark:bg-neutral-700 text-white text-xs rounded-lg py-2 px-3
                     shadow-lg whitespace-nowrap"
        >
          {tooltipContent()}
          {/* Tooltip arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
            <div className="border-4 border-transparent border-t-gray-900 dark:border-t-neutral-700" />
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for table cells - just shows icon
 */
export function SpeakerMappingIcon({
  hasSpeakerMapping,
  speakerMapping,
  onClick,
}: Pick<SpeakerMappingBadgeProps, 'hasSpeakerMapping' | 'speakerMapping' | 'onClick'>) {
  const [showTooltip, setShowTooltip] = useState(false);

  const isMapped = hasSpeakerMapping || (speakerMapping && Object.keys(speakerMapping).length > 0);
  const mappingCount = speakerMapping ? Object.keys(speakerMapping).length : 0;

  if (!isMapped) {
    return null;
  }

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick?.();
  };

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={handleClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="p-1 rounded hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
        title={`${mappingCount}명 화자 매핑됨`}
      >
        <UserCheck className="w-4 h-4 text-green-600 dark:text-green-400" />
      </button>

      {/* Tooltip */}
      {showTooltip && speakerMapping && Object.keys(speakerMapping).length > 0 && (
        <div
          className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2
                     bg-gray-900 dark:bg-neutral-700 text-white text-xs rounded-lg py-2 px-3
                     shadow-lg whitespace-nowrap"
        >
          <div className="space-y-1">
            <div className="font-medium mb-1">화자 매핑</div>
            {Object.entries(speakerMapping).map(([speaker, item]) => (
              <div key={speaker} className="flex justify-between gap-3 text-xs">
                <span className="text-gray-300">&quot;{speaker}&quot;</span>
                <span className="text-white font-medium">→ {item.party_name}</span>
              </div>
            ))}
          </div>
          {/* Tooltip arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-px">
            <div className="border-4 border-transparent border-t-gray-900 dark:border-t-neutral-700" />
          </div>
        </div>
      )}
    </div>
  );
}

export default SpeakerMappingBadge;
