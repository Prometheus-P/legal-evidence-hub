/**
 * Logo Component
 * CHAGOK (차곡) - 법률증거허브
 *
 * Reusable logo component with inline SVG for optimal performance.
 * Design: "Neatly Stacked" concept - 3 floating document sheets
 */

import { BRAND } from '@/config/brand';

interface LogoProps {
  /** Size preset or custom pixel value */
  size?: 'sm' | 'md' | 'lg' | number;
  /** Display variant: icon only or icon with text */
  variant?: 'icon' | 'full';
  /** Additional CSS classes */
  className?: string;
}

const SIZE_MAP = {
  sm: 32,
  md: 48,
  lg: 64,
} as const;

/**
 * Inline SVG Logo Icon
 * Teal gradient (#2DD4BF → #0F766E) with stacked white sheets
 */
function LogoIcon({ size }: { size: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="flex-shrink-0"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#2DD4BF" />
          <stop offset="100%" stopColor="#0F766E" />
        </linearGradient>
        <filter id="logoShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="6" result="offsetblur" />
          <feComponentTransfer>
            <feFuncA type="linear" slope="0.2" />
          </feComponentTransfer>
          <feMerge>
            <feMergeNode />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Background */}
      <rect width="512" height="512" rx="102" fill="url(#logoGradient)" />

      {/* Stacked Sheets */}
      <g transform="translate(136, 116)">
        {/* Bottom Sheet */}
        <rect
          x="20"
          y="160"
          width="200"
          height="140"
          rx="20"
          fill="white"
          fillOpacity="0.85"
          filter="url(#logoShadow)"
        />

        {/* Middle Sheet */}
        <rect
          x="20"
          y="80"
          width="200"
          height="140"
          rx="20"
          fill="white"
          fillOpacity="0.92"
          filter="url(#logoShadow)"
        />

        {/* Top Sheet */}
        <g filter="url(#logoShadow)">
          <rect x="20" y="0" width="200" height="140" rx="20" fill="white" />
          {/* Document lines */}
          <rect x="40" y="30" width="60" height="8" rx="4" fill="#0F766E" fillOpacity="0.2" />
          <rect x="40" y="50" width="120" height="8" rx="4" fill="#0F766E" fillOpacity="0.1" />
          <rect x="40" y="70" width="120" height="8" rx="4" fill="#0F766E" fillOpacity="0.1" />
        </g>
      </g>
    </svg>
  );
}

export function Logo({ size = 'md', variant = 'icon', className = '' }: LogoProps) {
  const pixelSize = typeof size === 'number' ? size : SIZE_MAP[size];

  if (variant === 'icon') {
    return (
      <div className={className} role="img" aria-label={`${BRAND.name} 로고`}>
        <LogoIcon size={pixelSize} />
      </div>
    );
  }

  // Full variant: icon + text
  return (
    <div className={`flex items-center gap-2 ${className}`} role="img" aria-label={`${BRAND.name} 로고`}>
      <LogoIcon size={pixelSize} />
      <span
        className="font-bold text-gray-900 dark:text-gray-100"
        style={{ fontSize: `${Math.max(pixelSize * 0.5, 14)}px` }}
      >
        {BRAND.name}
      </span>
    </div>
  );
}

export default Logo;
