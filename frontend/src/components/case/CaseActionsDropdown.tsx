/**
 * CaseActionsDropdown Component
 *
 * Consolidates secondary case actions into a dropdown menu to reduce header clutter.
 * Part of Phase 4 UX Enhancements (polymorphic-dazzling-oasis.md).
 *
 * Before: 6 buttons in header (visual clutter, mobile wrapping issues)
 * After: Primary action + dropdown with secondary actions
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
  MoreVertical,
  Edit3,
} from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export interface CaseActionsDropdownProps {
  /**
   * Handler for edit button click
   */
  onEdit: () => void;

  /**
   * Additional CSS classes
   */
  className?: string;
}

interface DropdownItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  type: 'link' | 'button';
  href?: string;
  onClick?: () => void;
  colorClass: string;
}

// =============================================================================
// Component
// =============================================================================

export function CaseActionsDropdown({
  onEdit,
  className = '',
}: CaseActionsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Close on Escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const handleItemClick = (onClick?: () => void) => {
    if (onClick) {
      onClick();
    }
    setIsOpen(false);
  };

  // Define dropdown items
  const items: DropdownItem[] = [
    {
      id: 'edit',
      label: '수정',
      icon: <Edit3 className="w-4 h-4" />,
      type: 'button',
      onClick: onEdit,
      colorClass: 'text-gray-600 dark:text-gray-400',
    },
  ];

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={handleToggle}
        className="p-2 border border-gray-300 dark:border-neutral-600 text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-50 dark:hover:bg-neutral-700 transition-colors"
        aria-label="더보기"
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        <MoreVertical className="w-5 h-5" />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className="absolute right-0 top-full z-50 mt-2 w-48 rounded-lg border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-lg py-1"
          role="menu"
          aria-orientation="vertical"
        >
          {items.map((item) => {
            const commonClasses = `w-full flex items-center gap-3 px-4 py-2.5 text-sm hover:bg-gray-50 dark:hover:bg-neutral-700 transition-colors ${item.colorClass}`;

            if (item.type === 'link' && item.href) {
              return (
                <Link
                  key={item.id}
                  href={item.href}
                  className={commonClasses}
                  role="menuitem"
                  onClick={() => setIsOpen(false)}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              );
            }

            return (
              <button
                key={item.id}
                type="button"
                className={commonClasses}
                role="menuitem"
                onClick={() => handleItemClick(item.onClick)}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default CaseActionsDropdown;
