/**
 * ResponsiveTable Component (T048)
 *
 * A responsive table that automatically switches to card view on mobile devices.
 * Provides consistent data display across all viewport sizes.
 *
 * Features:
 * - Table view on desktop (>768px)
 * - Card view on mobile (<=768px)
 * - Custom cell rendering
 * - Accessible with proper ARIA attributes
 * - Touch-friendly on mobile
 */

'use client';

import { ReactNode, useEffect, useState } from 'react';

export interface ResponsiveTableColumn<T> {
  /**
   * Key to access data property
   */
  key: keyof T;
  /**
   * Column header text
   */
  header: string;
  /**
   * If true, this column is emphasized in card view
   */
  primary?: boolean;
  /**
   * Custom render function for cell content
   */
  render?: (value: T[keyof T], item: T) => ReactNode;
  /**
   * Additional CSS classes for the column
   */
  className?: string;
  /**
   * Hide this column on mobile card view
   */
  hideOnMobile?: boolean;
}

export interface ResponsiveTableProps<T> {
  /**
   * Data array to display
   */
  data: T[];
  /**
   * Column definitions
   */
  columns: ResponsiveTableColumn<T>[];
  /**
   * Function to extract unique key from each item
   */
  keyExtractor: (item: T) => string;
  /**
   * Accessible caption for the table
   */
  caption?: string;
  /**
   * Message to display when data is empty
   */
  emptyMessage?: string;
  /**
   * Callback when a row/card is clicked
   */
  onRowClick?: (item: T) => void;
  /**
   * Additional CSS classes for the container
   */
  className?: string;
  /**
   * Breakpoint for mobile view (default: 768)
   */
  mobileBreakpoint?: number;
}

export function ResponsiveTable<T>({
  data,
  columns,
  keyExtractor,
  caption,
  emptyMessage = '데이터가 없습니다',
  onRowClick,
  className = '',
  mobileBreakpoint = 768,
}: ResponsiveTableProps<T>) {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.matchMedia(`(max-width: ${mobileBreakpoint}px)`).matches);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [mobileBreakpoint]);

  // Empty state
  if (data.length === 0) {
    return (
      <div className={`text-center py-12 text-neutral-500 ${className}`}>
        <p>{emptyMessage}</p>
      </div>
    );
  }

  // Mobile Card View
  if (isMobile) {
    return (
      <ul
        role="list"
        aria-label={caption}
        className={`space-y-3 ${className}`}
      >
        {data.map((item) => (
          <li
            key={keyExtractor(item)}
            className={`
              bg-white rounded-lg border border-neutral-200 p-4 shadow-sm
              ${onRowClick ? 'cursor-pointer hover:border-primary hover:shadow-md active:bg-neutral-50' : ''}
              transition-all duration-200
            `}
            onClick={() => onRowClick?.(item)}
            role={onRowClick ? 'button' : undefined}
            tabIndex={onRowClick ? 0 : undefined}
            onKeyDown={(e) => {
              if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                onRowClick(item);
              }
            }}
          >
            {columns
              .filter((col) => !col.hideOnMobile)
              .map((column) => {
                const value = item[column.key];
                const displayValue = column.render
                  ? column.render(value, item)
                  : String(value ?? '');

                if (column.primary) {
                  return (
                    <div
                      key={String(column.key)}
                      className="text-base font-semibold text-neutral-900 mb-2"
                    >
                      {displayValue}
                    </div>
                  );
                }

                return (
                  <div
                    key={String(column.key)}
                    className="flex justify-between items-center py-1.5 text-sm border-t border-neutral-100 first:border-t-0"
                  >
                    <span className="text-neutral-500">{column.header}</span>
                    <span className={`text-neutral-900 ${column.className || ''}`}>
                      {displayValue}
                    </span>
                  </div>
                );
              })}
          </li>
        ))}
      </ul>
    );
  }

  // Desktop Table View
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table
        className="min-w-full divide-y divide-neutral-200"
        aria-label={caption}
      >
        {caption && (
          <caption className="sr-only">{caption}</caption>
        )}
        <thead className="bg-neutral-50">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                scope="col"
                className={`
                  px-6 py-3 text-left text-xs font-medium text-neutral-500
                  uppercase tracking-wider ${column.className || ''}
                `}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-neutral-200">
          {data.map((item, index) => (
            <tr
              key={keyExtractor(item)}
              className={`
                ${index % 2 === 0 ? 'bg-white' : 'bg-neutral-50/50'}
                ${onRowClick ? 'cursor-pointer hover:bg-primary-light/30' : ''}
                transition-colors
              `}
              onClick={() => onRowClick?.(item)}
              tabIndex={onRowClick ? 0 : undefined}
              onKeyDown={(e) => {
                if (onRowClick && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  onRowClick(item);
                }
              }}
            >
              {columns.map((column) => {
                const value = item[column.key];
                const displayValue = column.render
                  ? column.render(value, item)
                  : String(value ?? '');

                return (
                  <td
                    key={String(column.key)}
                    className={`
                      px-6 py-4 whitespace-nowrap text-sm
                      ${column.primary ? 'font-medium text-neutral-900' : 'text-neutral-600'}
                      ${column.className || ''}
                    `}
                  >
                    {displayValue}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ResponsiveTable;
